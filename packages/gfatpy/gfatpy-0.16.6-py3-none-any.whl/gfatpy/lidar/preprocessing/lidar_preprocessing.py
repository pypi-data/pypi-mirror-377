# from curses import set_tabsize
from pathlib import Path
from loguru import logger
import numpy as np
import xarray as xr


# from gfatpy.lidar.preprocessing.lidar_gluing_bravo_aranda import gluing
from gfatpy.utils import calibration
from gfatpy.lidar.utils.utils import LIDAR_INFO
from gfatpy.utils.io import read_yaml_from_info
from gfatpy.lidar.preprocessing.gluing_de_la_rosa_slope import gluing
from gfatpy.utils.utils import adaptive_moving_average, sliding_average
from gfatpy.lidar.utils.file_manager import (
    add_required_channels,
    filename2info,
    search_dc,
)
from gfatpy.lidar.preprocessing.lidar_preprocessing_tools import (
    ff_2D_overlap_from_channels,
)

# from .lidar_merge import apply_polarization_merge
# from .lidar_preprocessing_tools import *  # TODO: Remove wildcard importations within modules

# warnings.filterwarnings("ignore")

__author__ = "Bravo-Aranda, Juan Antonio"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Bravo-Aranda, Juan Antonio"
__email__ = "jabravo@ugr.es"
__status__ = "Production"


""" DEFAULT AUXILIAR INFO
"""
# Root Directory (in NASGFAT)  according to operative system
""" LIDAR PREPROCESSING
"""


def preprocess(
    file_or_path: Path | str,
    channels: list[str] | None = None,
    crop_ranges: tuple[float, float] | None = (0, 20000),
    background_ranges: tuple[float, float] | None = None,
    apply_sm: bool = False,
    apply_dc: bool = True,
    apply_dt: bool = True,
    apply_bg: bool = True,
    apply_bz: bool = True,
    apply_ov: bool = False,
    save_dc: bool = False,
    save_bg: bool = False,
    gluing_products: bool = False,
    force_dc_in_session=False,
    overlap_path: Path | str | None = None,
    smooth_mode: str | None = None,
    **kwargs,
) -> xr.Dataset:
    """It preprocesses lidar netcdf file. It can optionally apply dark-measurement, deadtime, background, zero-bin, and overlap correction and calculate gluing products.

    Args:
        # ...existing args...
        -apply_sliding_average (bool, optional): it applies a sliding average to the signal variables. Defaults to False.
        -y_sm_lims (tuple[float, float], optional): limits for the sliding average. Defaults to (0, 20000).
        -y_sm_hwin (tuple[float, float], optional): half window size for the sliding average. Defaults to (100, 1000).


    Returns:
        -xr.Dataset: xarray.Dataset with the lidar data and information.
    """

    _p = Path(file_or_path)
    if not _p.exists():
        raise ValueError(f"{file_or_path} not found")

    # Get info from filename
    lidar_nick, _, _, _, _, date = filename2info(_p.name)
    global INFO
    INFO = read_yaml_from_info(lidar_nick, date)

    with xr.open_dataset(_p, chunks={}, engine="netcdf4") as _nc:
        dataset = _nc

    if channels is None:
        channels = dataset.channel.values.tolist()
        raw_channels = channels
        product_channels = []
    else:
        channels = add_required_channels(lidar_nick, channels, date)
        # Split channels by raw/products
        raw_channels = [
            channel_
            for channel_ in channels
            if channel_ not in INFO["product_channels"].keys()
        ]

        dataset = drop_unwanted_channels(dataset, keep_channels=raw_channels)

    # If header is defined in INFO, its fields are used to update the dataset. Variables and attributes can be updated. See example on info_alh_20221117.yml
    if "header" in INFO.keys():
        update_from_info(dataset, INFO["header"])

    if apply_sm:
        dataset = apply_smooth(dataset, smooth_mode=smooth_mode, **kwargs)

    if apply_dc:
        dataset = apply_dark_current_correction(
            dataset,
            rs_path=_p,
            save_dc=save_dc,
            force_dc_in_session=force_dc_in_session,
            apply_sm=apply_sm,
            smooth_mode=smooth_mode,
            **kwargs
        )
    else:
        dataset.attrs["dc_corrected"] = str(False)

    if apply_dt:
        dataset = apply_dead_time_correction(
            dataset
        )  # TODO implement search_dt() in the same way of search_dc
    else:
        dataset.attrs["dt_corrected"] = str(False)

    if apply_bg:
        dataset = apply_background_correction(
            dataset, background_ranges=background_ranges, save_bg=save_bg
        )
    else:
        dataset.attrs["bg_corrected"] = str(False)

    if apply_bz:
        dataset = apply_bin_zero_correction(dataset, rs_path=_p)
    else:
        dataset.attrs["bz_corrected"] = str(False)

    if apply_ov:
        dataset = apply_overlap_correction(dataset, overlap_path)
        dataset.attrs["ov_corrected"] = "True"
    else:
        dataset.attrs["ov_corrected"] = "False"

    dataset = apply_crop_ranges_correction(dataset, crop_ranges=crop_ranges)

    if gluing_products:
        dataset = apply_detection_mode_merge(dataset)

    dataset = add_height(dataset)

    return dataset


def update_from_info(dataset: xr.Dataset, header: dict):
    """Update dataset variables and attributes from INFO header.

    Args:

        - dataset (xr.Dataset): Dataset to be updated.
        - header (dict): Header from INFO.

    Raises:

        - RuntimeError: Variables or attributes could not be updated.
        - RuntimeError: Attributes could not be updated.

    Returns:

        - xr.Dataset: Updated dataset.
    """
    for key_ in header.keys():
        if key_ in [*dataset.variables.keys()]:
            try:
                # Replace dataset[key_] with header[key_] using the same dimensions and coordinates
                dataset[key_] = xr.DataArray(
                    header[key_], dims=dataset[key_].dims, coords=dataset[key_].coords
                )
            except Exception as e:
                raise RuntimeError(
                    f"Could not update variable {key_} from INFO. Error: {e}"
                )
        if key_ in [*dataset.attrs.keys()]:
            try:
                dataset.attrs[key_] = header[key_]
            except Exception as e:
                raise RuntimeError(
                    f"Could not update attribute {key_} from INFO. Error: {e}"
                )
    return dataset


def drop_unwanted_channels(
    dataset: xr.Dataset, keep_channels: list[str] | None
) -> xr.Dataset:
    """Drop unwanted channels from dataset.

    Args:

        - dataset (xr.Dataset): Dataset to be updated.
        - keep_channels (list[str] | None): List of channels to be removed. Defaults to None meaning all channels are kept.

    Returns:

        - xr.Dataset: Updated dataset.
    """
    if keep_channels is None:
        return dataset
    remove_channels = list(
        filter(lambda channel_: channel_ not in keep_channels, dataset.channel.values)
    )
    remove_signals = list(
        f"signal_{channel_}"
        for channel_ in remove_channels
        if f"signal_{channel_}" in dataset.keys()
    )
    dataset = dataset.drop_vars(remove_signals, errors="raise")
    remove_stderr = list(
        f"stderr_{channel_}"
        for channel_ in remove_channels
        if f"stderr_{channel_}" in dataset.keys()
    )

    dataset = dataset.drop_vars(remove_stderr, errors="raise")
    dataset = dataset.sel(channel=keep_channels)

    return dataset


def add_height(dataset: xr.Dataset) -> xr.Dataset:
    """Add height coordinate to dataset.

    Args:

        - dataset (xr.Dataset): Dataset to be updated.

    Raises:

        - RuntimeError: Zenithal angle is not constant in time. Cannot add height coordinate.

    Returns:

        - xr.Dataset: Updated dataset.
    """
    # Add height because of zenithal angle
    if "zenithal_angle" in [*dataset.variables.keys()]:
        if dataset["zenithal_angle"].values.all():
            zenithal_angle = np.deg2rad(dataset["zenithal_angle"].values[0])
            if zenithal_angle != 0:
                dataset["height"] = dataset["range"] * np.cos(zenithal_angle)
            else:
                dataset["height"] = dataset["range"].copy()
        else:
            raise RuntimeError(
                "Zenithal angle is not constant in time. Cannot add height coordinate."
            )
    return dataset


def apply_smooth(
    dataset: xr.Dataset, smooth_mode: str | None = None, **kwargs
) -> xr.Dataset:
    # Apply moving average if requested
    if smooth_mode == "moving":
        logger.info(f"Applying moving average smoothing...")
        for channel_ in dataset.channel.values:  # type: ignore
            dataset[f"signal_{channel_}"] = xr.DataArray(
                adaptive_moving_average(
                    dataset[f"signal_{channel_}"].values,
                    window_sizes=kwargs.get("window_sizes", 10.0),
                ),
                dims=dataset[f"signal_{channel_}"].dims,
                coords=dataset[f"signal_{channel_}"].coords,
            )
    elif smooth_mode == "sliding":
        logger.info(f"Applying sliding average smoothing...")
        for channel_ in dataset.channel.values:
            dataset[f"signal_{channel_}"] = sliding_average(
                dataset[f"signal_{channel_}"],
                maximum_range=kwargs.get("sliding_maximum_range", 4000.0),
                window_range=kwargs.get("window_range", (10, 300)),
            )
    elif smooth_mode == "binning":
        logger.info(f"Not implemented yet...")
        # logger.info(f"Applying binning average smoothing...")
        # bin_size = kwargs.get("binning_average_bin", 10)
        # binned_range = np.arange(dataset["range"].min(), dataset["range"].max() + bin_size, bin_size)
        # # # Perform binning and mean computation lazily
        # dataset = dataset.groupby_bins(
        #     "range", binned_range, eagerly_compute_group=False
        # ).mean()
        # dataset = dataset.rename({f"range_bins": "range"}).assign_coords({"range": binned_range[:-1]})
    elif smooth_mode is None:
        logger.info(f"No smoothing applied...")
    else:
        raise ValueError(
            "smooth_mode not recognized [choose: moving, sliding, binning]."
        )
    return dataset


def apply_dark_current_correction(
    dataset: xr.Dataset,
    rs_path: Path,
    save_dc: bool = False,
    force_dc_in_session=False,
    apply_sm: bool = False,
    smooth_mode: str | None = None,
    crop_ranges: tuple[float, float] | None = (0, 20000),
    **kwargs,
) -> xr.Dataset:
    """Apply dark current correction to dataset.

    Args:

        - dataset (xr.Dataset): Dataset to be corrected.
        - rs_path (Path): Path to the raw data.
        - save_dc (bool, optional): Flag to save the dark current in the dataset. Defaults to False.
        - force_dc_in_session (bool, optional): Flag to force the use of the dark current linked to this measurement period. If not found, the correction cannot be performed. Defaults to False.

    Raises:

        - Warning: Dark current std is too high for an specified channel. Dark measurement shall be not appropiated.

    Returns:

        - xr.Dataset: Dataset with dark current corrected.
    """
    groups = calibration.split_continous_measurements(dataset.time.values)
    channels = dataset.channel.values

    analog_channels: list[str] = list(filter(lambda c: c.endswith("a"), channels))

    for group in groups:
        dc_path = search_dc(
            rs_path,
            session_period=group[[0, -1]],
            force_dc_in_session=force_dc_in_session,
        )
        dc = xr.open_dataset(dc_path)

        dc = drop_unwanted_channels(dc, keep_channels=analog_channels)

        if apply_sm:
            dc = apply_smooth(dc, smooth_mode=smooth_mode, **kwargs)
            
        lower_idx = np.where(dataset.time == group[0])[0][0]
        upper_idx = np.where(dataset.time == group[-1])[0][0] + 1

        for channel in analog_channels:
            signal_str = f"signal_{channel}"
            if dc[signal_str].sel(range=slice(0, 5000)).std("range").std("time") > 0.07:
                raise Warning(
                    f"Dark current std is too high for channel {channel} in {dc_path}. Check if DC was measured correctly."
                )

            dc_mean = dc[signal_str].mean(axis=0)
            
            dataset[signal_str].loc[dict(time=group)] -= dc_mean.values[np.newaxis, :]
            # dataset[signal_str].values[:,lower_idx:upper_idx] -= dc_mean.values #TODO: too slow

            if save_dc:
                if (
                    f"dc_{channel}" not in list(dataset.variables.keys())
                    and lower_idx == 0
                ):
                    dataset[f"dc_{channel}"] = dataset[signal_str] * np.nan

                dataset[f"dc_{channel}"][lower_idx:upper_idx] = dc_mean

    dataset.attrs["dc_corrected"] = str(True)

    return dataset


def apply_dead_time_correction(dataset: xr.Dataset) -> xr.Dataset:
    """Apply dead time correction to dataset.

    Args:

        - dataset (xr.Dataset): Dataset to be corrected.

    Raises:

        - ValueError: No dead time value defined in INFO->{lidar_name}->{channel}.
        - ValueError: No dead time value defined in INFO->{lidar_name}.

    Returns:

        - xr.Dataset: Dataset with dead time corrected.
    """
    # dt_path = search_dt(rs_path, session_period=dataset.time.values[[0,-1]]) #
    # dt_dict = open_dataset(dt_path) #TODO

    lidar_name = dataset.attrs["system"].lower()
    try:
        dt_dict = {
            key: value["dead_time_ns"]
            for (key, value) in INFO["channels"].items()
            if value.get("dead_time_ns", False)
        }
    except Exception:
        raise ValueError(f"No dead time value defined in INFO->{lidar_name}].")

    photocounting_channels: list[str] = list(
        filter(lambda c: c.endswith("p"), dataset.channel.values)
    )

    for channel in photocounting_channels:
        # tau from ns to us
        try:
            tau_us = dt_dict[channel] * 1e-3
        except KeyError:
            raise ValueError(  # TODO
                f"No dead time value defined in INFO->{lidar_name}->{channel}."
            )

        signal_str = f"signal_{channel}"

        # Eq 4 [D'Amico et al., 2016]
        # No infinites nor negative values
        # condition = np.logical_and(~np.isinf(dataset[signal_str]), dataset[signal_str] > 0)
        # dataset[signal_str] = dataset[signal_str].where(condition)/ ( 1 - dataset[signal_str].where(condition) * tau_us )

        dataset[signal_str] = dataset[signal_str] / (1 - dataset[signal_str] * tau_us)
        dataset.attrs["dt_corrected"] = str(True)

    return dataset


def apply_background_correction(
    dataset: xr.Dataset,
    background_ranges: tuple[float, float] | None = None,
    save_bg: bool = False,
) -> xr.Dataset:
    """Apply background correction to dataset.

    Args:

        - dataset (xr.Dataset): Dataset to be corrected.
        - background_ranges (tuple[float, float] | None, optional): Range where background average will be performed for each signal. This value is subtracted to the whole profile. Defaults to None.
        - save_bg (bool, optional): Flag to save the background in the dataset. Defaults to False.

    Raises:

        - ValueError: background_ranges should be in order (min, max).

    Returns:

        - xr.Dataset: Dataset with background corrected.
    """
    if background_ranges is None:
        background_ranges = (
            dataset.attrs["BCK_MIN_ALT"],
            dataset.attrs["BCK_MAX_ALT"],
        )

    if background_ranges[1] <= background_ranges[0]:
        raise ValueError("background_ranges should be in order (min, max)")

    ranges_between = (background_ranges[0] < dataset.range) & (
        dataset.range < background_ranges[1]
    )
    channels: list[str] = dataset.channel.values
    for channel in channels:
        signal_str = f"signal_{channel}"
        try:
            background = dataset[signal_str].loc[:, ranges_between].mean(axis=1)
        except:
            background = np.ones(1)
        dataset[signal_str] -= background

        if save_bg:
            dataset[f"bg_{channel}"] = background

    dataset.attrs["bg_corrected"] = str(True)

    return dataset


def apply_bin_zero_correction(dataset: xr.Dataset, rs_path: Path) -> xr.Dataset:
    """Apply zero bin correction to dataset.

    Args:

        - dataset (xr.Dataset): Dataset to be corrected.
        - rs_path (Path): Path to the raw data.

    Raises:

        - ValueError: No bin zero value defined in INFO->{lidar_name}.

    Returns:

        - xr.Dataset: Dataset with zero bin corrected.
    """
    # bz_path = search_bz(rs_path, session_period=dataset.time.values[[0,-1]]) #
    # bz_dict = open_dataset(bz_path) #TODO
    bz_dict = None

    if bz_dict is None:
        lidar_name = dataset.attrs["system"].lower()
        try:
            bz_dict = {
                key: value["bin_zero"] for (key, value) in INFO["channels"].items()
            }
        except Exception:
            raise ValueError(f"No bin zero value defined in INFO->{lidar_name}.")

    channels: list[str] = dataset.channel.values
    for channel in channels:
        signal_str = f"signal_{channel}"
        dataset[signal_str] = dataset[signal_str].shift(
            range=-bz_dict[channel], fill_value=0.0
        )

    dataset.attrs["bz_corrected"] = str(True)

    return dataset


def apply_overlap_correction(
    dataset: xr.Dataset,
    ff_overlap_path: Path | str | None = None,
    nf_overlap_path: Path | str | None = None,
) -> xr.Dataset:
    """Apply overlap correction to dataset.

    Args:

        - dataset (xr.Dataset): Dataset to be corrected.
        - overlap_path (Path): Path to the overlap file.

    Returns:

        - xr.Dataset: Dataset with overlap corrected.
    """

    def apply_correction(
        dataset: xr.Dataset,
        overlap: xr.DataArray,
        channels2correct: list[str],
        overlap_channel: str,
    ) -> xr.Dataset:

        try:
            for channel_ in channels2correct:
                if channel_ in dataset.channel.values:
                    signal_str = f"signal_{channel_}"

                    # Perform overlap correction
                    dataset[signal_str] = dataset[signal_str] / overlap
                    dataset[signal_str].attrs["overlap_applied"] = overlap_channel
                    dataset["overlap_corrected"][dataset.channel.values == channel_] = 1
        except:
            raise Warning("Could not apply overlap correction")
        return dataset

    lidar_name = dataset.attrs["system"].lower()
    overlap_channels = INFO["overlap_channels"]
    linked_channels = INFO["overlap_linked_channels"]

    # New array to store if overlap correction was applied
    overlap_corrected = xr.DataArray(
        np.zeros(dataset.channel.size),
        dims=("channel"),
        coords={"channel": dataset.channel},
    )
    dataset["overlap_corrected"] = overlap_corrected

    # Apply overlap correction for far-field channels
    # TODO: Move to LIDAR_INFO

    # Load overlap dataset
    if ff_overlap_path is not None:
        overlap = xr.open_dataarray(ff_overlap_path)
    else:
        overlap = None

    for channel_ in linked_channels.keys():
        # Check channel_ in dataset

        if channel_ not in dataset.channel.values:
            continue

        # Select overlap array for channel
        if overlap is not None:
            if channel_ in overlap.channel.values:
                overlap_ = overlap.sel(channel=channel_)
            else:
                raise ValueError(f"Channel {channel_} not found in overlap file")
        else:
            nf_channel_ = overlap_channels[channel_]
            if not nf_channel_ in dataset.channel.values:
                raise ValueError(
                    f"Channel {nf_channel_} not found in dataset. Please include near-field channel in dataset to retrieve overlap."
                )
            overlap_ = ff_2D_overlap_from_channels(
                dataset, channel_ff=channel_, channel_nf=nf_channel_
            )
        # Check size of arrays
        if dataset.range.size != overlap_.range.size:
            # Adapt size of overlap array to dataset
            overlap_ = overlap_.interp(range=dataset.range, method="linear")

        # Save overlap array
        if overlap_.values.any():
            # Apply overlap correction
            dataset = apply_correction(
                dataset, overlap_, linked_channels[channel_], overlap_channel=channel_
            )

            dataset[f"overlap_{channel_}"] = overlap_

    # Apply overlap correction for far-field channels
    if nf_overlap_path is not None:
        linked_channels = {
            "355npa": [
                "355npa",
                "355npp",
                "355nsa",
                "355nsp",
                "387nta",
                "387ntp",
                "408nta",
                "408ntp",
            ],
            "532npa": ["532npa", "532npp", "607nta", "607ntp"],
        }
        # Load overlap dataset
        overlap = xr.open_dataarray(nf_overlap_path)

        for channel_ in overlap.channel.values:
            # Select overlap array for channel
            overlap_ = overlap.sel(channel=channel_)

            # Check size of arrays
            if dataset.range.size != overlap_.range.size:
                # Adapt size of overlap array to dataset
                overlap_ = overlap_.interp(range=dataset.range, method="linear")

            # Apply overlap correction
            dataset = apply_correction(
                dataset, overlap_, linked_channels[channel_], overlap_channel=channel_
            )

            # Save overlap array
            if dataset["overlap_corrected"].values.any():
                dataset[f"overlap_{channel_}"] = overlap_
    return dataset


def apply_crop_ranges_correction(
    dataset: xr.Dataset, crop_ranges: tuple[float, float] | None = (0, 20000)
) -> xr.Dataset:
    """It crops the dataset range dimension to `crop_ranges` values.

    Args:

        - dataset (xr.Dataset): Dataset to be cropped.
        - crop_ranges (tuple[float, float] | None, optional): Mininum and maximum ranges. Defaults to (0, 20000).

    Raises:

        - ValueError: crop_ranges should be in order (min, max).

    Returns:

        - xr.Dataset: Dataset with range cropped.
    """
    # TODO: Apply crop ranges. With dataset.sel(range=slice(*crop_ranges))

    if crop_ranges is None:
        return dataset

    if crop_ranges[0] > crop_ranges[-1]:
        raise ValueError("crop_ranges should be in order (min, max)")

    dataset = dataset.sel(range=slice(*crop_ranges))

    return dataset


def apply_detection_mode_merge(dataset: xr.Dataset) -> xr.Dataset:
    """It performs the detection-mode gluing.

    Args:
        dataset (xr.Dataset): Dataset to be merged.

    Returns:
        xr.Dataset: Merged dataset.
    """
    LIDAR_INFO["metadata"]["code_telescope_str2number"]
    LIDAR_INFO["metadata"]["code_mode_str2number"]

    channels_pc: list[str] = list(
        filter(
            lambda c: any(
                c.startswith(vc) and c.endswith("p") for vc in dataset.channel.values
            ),
            dataset.channel.values,
        )
    )

    range_m = dataset["range"].values
    glued_list: list[dict] = []

    for channel_pc in channels_pc:
        channel_an = f"{channel_pc[0:-1]}a"

        if f"signal_{channel_an}" not in list(dataset.variables.keys()):
            continue

        signal_gl = gluing(
            dataset[f"signal_{channel_an}"], dataset[f"signal_{channel_pc}"]
        )

        print(f"Gluing done for channels: {channel_an} and {channel_pc}")

        polarization = channel_pc[-1] if channel_pc[-1] in ["p", "s"] else ""
        telescope = channel_pc[0]  # Primera letra representa el telescopio
        wavelength = channel_pc[1:-1]  # Longitud de onda sin la primera ni última letra

        glued_list.append(
            {
                "name": f"{channel_pc[0:-1]}g",
                "signal": signal_gl,
                "polarization": polarization,
                "telescope": telescope,
                "wavelength": wavelength,
            }
        )

    glued_signal = {
        f"signal_{glued['name']}": (["time", "range"], glued["signal"])
        for glued in glued_list
    }

    other_var = {
        "wavelength": (["channel"], [g["wavelength"] for g in glued_list]),
        "polarization": (["channel"], [g["polarization"] for g in glued_list]),
        "telescope": (["channel"], [g["telescope"] for g in glued_list]),
        "bin_shift": (["channel"], [0 for _ in glued_list]),
    }

    glued_dataset = xr.Dataset(
        glued_signal | other_var,
        coords={
            "range": range_m,
            "time": dataset["time"].values,
            "channel": list(map(lambda i: i["name"], glued_list)),
        },
    )

    return xr.merge([dataset, glued_dataset])
