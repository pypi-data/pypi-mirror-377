import datetime as dt
from pathlib import Path
from pdb import set_trace
from typing import Tuple
import numpy as np
import pandas as pd
import xarray as xr
from scipy.signal import savgol_filter
from gfatpy.atmo.atmo import transmittance

from gfatpy.utils import utils
from gfatpy.atmo.rayleigh import molecular_properties
from gfatpy.lidar.preprocessing import preprocess
from gfatpy.lidar.utils.file_manager import channel2info
from gfatpy.lidar.utils.utils import LIDAR_INFO, signal_to_rcs
from gfatpy.lidar.quality_assurance.io import rayleigh2earlinet, get_meteo
from gfatpy.lidar.quality_assurance.plot import plot_rayleigh_fit

lidar_id = "gr"
lidar_location = "Granada"

""" Types of Lidar Measurements """
measurement_types = {
    "RS": "Prs",
    "DC": "Pdc",
    "OT": "Pot",
    "DP-P45": "Pdp-45",
    "DP-N45": "Pdp-N45",
}


def rayleigh_fit_channel(
    channel: str,
    rf_dataset: xr.Dataset,
    initial_date: dt.datetime,
    final_date: dt.datetime,
    meteo_profiles: pd.DataFrame,
    meteo_info: dict,
    reference_range: Tuple[float, float],
    smooth_window: float,
) -> xr.Dataset:
    """Rayleigh Fit for a given channel.

    Args:

        - channel (str): Channel to calculate the Rayleigh Fit.
        - rf_dataset (xr.Dataset): Dataset with the lidar measurements.
        - initial_date (dt.datetime): Initial date of the period to calculate the Rayleigh Fit.
        - final_date (dt.datetime): Final date of the period to calculate the Rayleigh Fit.
        - meteo_profiles (pd.DataFrame): Meteo profiles (e.g., from gfatpy.atmo.atmo.generate_meteo_profiles).
        - meteo_info (dict): Meteo information in a dictionary with keys: radiosonde_location, radiosonde_wmo_id, radiosonde_datetime.
        - reference_range (Tuple[float, float]): Reference range to normalize.
        - smooth_window (float): Range window to smooth the signal.

    Returns:
    
        - xr.Dataset: Rayleigh fit dataset.
    """    
    wavelength, *_ = channel2info(channel)

    # Molecular Attenuated Backscatter
    temperature = np.array(meteo_profiles["temperature"])
    pressure = np.array(meteo_profiles["pressure"])
    range = np.array(meteo_profiles["height"])
    mol_properties = molecular_properties(wavelength, pressure, temperature, range)
    att_beta_mol = mol_properties["molecular_beta"]*transmittance(mol_properties['molecular_alpha'], heights=range)**2    
    wavelength, _, polarization, mode = channel2info(channel)

    # RCS
    signal = rf_dataset[f"signal_{channel}"]
    rcs = signal_to_rcs(signal, signal.range)

    # Smooth rcs
    """ Lidar Resolution, Smoothing Bins """
    resolution = np.median(np.diff(signal.range))
    smooth_bins = np.round((smooth_window / resolution)).astype(int)
    sm_rcs = xr.DataArray(
        savgol_filter(rcs, smooth_bins, 3),
        coords={"range": signal.range},
        dims=["range"],
    )

    # Normalize time-averaged RCS, BCS nd Smoothed Time-Averaged RCS
    n_rcs = rcs / rcs.sel(range=slice(*reference_range)).mean("range")

    n_sm_rcs = sm_rcs / sm_rcs.sel(range=slice(*reference_range)).mean("range")

    n_att_beta_mol = att_beta_mol / att_beta_mol.sel(
        range=slice(*reference_range)
    ).mean("range")

    # output dataset will have height info in km
    ranges_km = range * 1e-3
    z_min_km = reference_range[0] * 1e-3
    z_max_km = reference_range[1] * 1e-3

    wavelength = xr.DataArray(data=wavelength, attrs={"str": f"{wavelength}"})
    polarization_long_name = LIDAR_INFO["metadata"]["code_polarization_str2long_name"][polarization]  # type: ignore
    polarization = xr.DataArray(
        data=polarization,
        dims=[],
        attrs={
            "long_name": polarization_long_name,
            "id": LIDAR_INFO["metadata"]["code_polarization_number2str"],
        },
    )
    polarization_code = LIDAR_INFO["metadata"]["code_mode_str2long_name"][mode]  # type: ignore
    detection_mode = xr.DataArray(
        data=mode,
        dims=[],
        attrs={
            "long_name": polarization_code,
            "id": LIDAR_INFO["metadata"]["code_mode_str2number"][mode],
        },
    )

    rcs = xr.DataArray(
        data=rcs,
        dims=["range"],
        coords={"range": ranges_km},
        attrs={
            "name": "RangeCorrectedSignal",
            "long_name": "range corrected signal avg",
            "units": "a.u.",
        },
    )

    n_rcs = xr.DataArray(
        data=n_rcs,
        dims=["range"],
        coords={"range": ranges_km},
        attrs={
            "name": "RangeCorrectedSignal",
            "long_name": "normalized- range-corrected signal.",
            "units": "a.u.",
        },
    )

    smoothed_rcs = xr.DataArray(
        data=sm_rcs,
        dims=["range"],
        coords={"range": ranges_km},
        attrs={
            "name": "RangeCorrectedSignal",
            "long_name": "smoothed range corrected signal",
            "units": "a.u.",
        },
    )

    normalized_smoothed_rcs = xr.DataArray(
        data=n_sm_rcs,
        dims=["range"],
        coords={"range": ranges_km},
        attrs={
            "name": "RangeCorrectedSignal",
            "long_name": "normalized- smoothed- range-corrected signal.",
            "units": "a.u.",
        },
    )

    attenuated_molecular_backscatter = xr.DataArray(
        data=att_beta_mol,
        dims=["range"],
        coords={"range": ranges_km},
        attrs={
            "name": "attnRayleighBSC",
            "long_name": "attenuated molecular backscatter",
            "units": "a.u.",
        },
    )

    normalized_attenuated_molecular_backscatter = xr.DataArray(
        data=n_att_beta_mol,
        dims=["range"],
        coords={"range": ranges_km},
        attrs={
            "name": "attnRayleighBSC",
            "long_name": "attenuated molecular backscatter norm",
            "units": "a.u.",
        },
    )
    dataset = xr.Dataset(
        data_vars={
            "wavelength": wavelength,
            "detection_mode": detection_mode,
            "RCS": rcs,
            "RCS_smooth": smoothed_rcs,
            "RCS_norm": n_rcs,
            "RCS_smooth_norm": normalized_smoothed_rcs,
            "BCS": attenuated_molecular_backscatter,
            "BCS_norm": normalized_attenuated_molecular_backscatter,
        },
        coords={"range": ranges_km},
        attrs={
            "lidar_location": lidar_location,
            "lidar_id": lidar_id,
            "lidar_name": rf_dataset.attrs["system"],
            "channel": channel,
            "radiosonde_location": meteo_info["radiosonde_location"],
            "radiosonde_wmo_id": meteo_info["radiosonde_wmo_id"],
            "radiosonde_datetime": meteo_info["radiosonde_datetime"],
            "datetime_ini": initial_date.strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),  # FIXME: Dejar como estaba o pasar a ISO 8601?. Estaba en formato 20220808T12, ahora en 2022-08-08T12:00:00
            "datetime_end": final_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "datetime_format": "%Y-%m-%dT%H:%M:%S",
            # "timestamp": final_date - initial_date,
            "duration": (final_date - initial_date).total_seconds(),
            "duration_units": "seconds",
            "rayleigh_height_limits": [z_min_km, z_max_km],
        },
    )
    dataset["range"].attrs["units"] = "km"
    dataset["range"].attrs["long_name"] = "height"

    if channel[-1] == "a" and f"dc_{channel}" in [*rf_dataset.variables.keys()]:
        dc_signal = rf_dataset[f"dc_{channel}"]
        # Normalized dc
        n_dc_signal = dc_signal / dc_signal.sel(range=slice(*reference_range)).mean(
            "range"
        )

        dataset["DC"] = xr.DataArray(
            data=dc_signal.values,
            dims=["range"],
            coords={"range": ranges_km},
            attrs={
                "name": "D",
                "long_name": "dark current avg",
                "units": "a.u.",
            },
        )
        dataset["DC_norm"] = xr.DataArray(
            data=n_dc_signal.values,
            dims=["range"],
            coords={"range": ranges_km},
            attrs={
                "name": "D",
                "long_name": "dark current avg norm",
                "units": "a.u.",
            },
        )

        dataset.attrs["dark_subtracted"] = "dark-subtracted"

    return dataset


def rayleigh_fit_from_file(
    file: Path,
    reference_range: Tuple[float, float],
    channels: list[str] | None = None,
    initial_hour: int | None = None,
    duration: float = 30,
    smooth_window: float = 250,
    crop_ranges: tuple[float, float] = (0, 30000),
    range_limits: tuple[float, float] | None = None,
    meteorology_source: str = "standard_atmosphere",
    output_dir: Path | str | None = None,
    save_fig: bool = False,
):
    """Rayleigh Fit from file

    Args:

        - file (Path): lidar netcdf file
        - channels (list[str] | None, optional): Channels to use for the rayleigh fits. Defaults [None] means all channels.
        - initial_hour (int | None, optional): Starting time of average. Defaults [None] means the last hour of the file.
        - duration (float, optional): Duration in minutes of the period to average. Defaults to 30.
        - reference_range (Tuple[float, float], optional): Reference range to average. Defaults to (7000, 8000).
        - smooth_window (float, optional): Range window to smooth the signal. Defaults to 250.
        - crop_ranges (tuple[float, float], optional): Rayleigh fit range. Defaults to (0, 30000).
        - range_limits (tuple[float, float] | None, optional): figure X axis limits. Defaults to None.
        - meteorology_source (str, optional): Options to retrieve the optical molecular properties ['ecmwf' | "standard atmosphere"]. If float pressure and temperature are provided. The 'scaled standard atmosphere' is used. Defaults to "standard_atmosphere".
        - save_fig (bool, optional): save plot image as png. Defaults to False.

    Raises:

        - NotADirectoryError: Output directory does not exist.
        - ValueError: initial_hour not found.

    Returns:
    
        - None: None
    """    

    if output_dir is None:
        output_dir = Path.cwd()
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    if not output_dir.exists() or not output_dir.is_dir():
        raise NotADirectoryError(f"Output directory {output_dir} does not exist.")

    # Lidar preprocess
    lidar_ds = preprocess(
        file,
        channels=channels,
        crop_ranges=crop_ranges,
        save_dc=True,
        save_bg=True,
    )
    # time in array
    times = lidar_ds["time"].values
    times = np.array([utils.numpy_to_datetime(xx) for xx in times])

    # ranges in array
    range = lidar_ds["range"].values

    # Define initial and final date
    initial_date = dt.datetime(
        times[1].year, times[1].month, times[1].day
    )
    if initial_hour is None:
        initial_hour = (times[-1] - dt.timedelta(minutes=60)).hour
    if initial_hour is not None:
        initial_date = initial_date.replace(hour=initial_hour)
    else:
        raise ValueError("initial_hour not found.")
    final_date = initial_date + dt.timedelta(minutes=duration)

    # Select of period:
    rf = lidar_ds.sel(time=slice(initial_date, final_date)).mean("time")
    rf.attrs = lidar_ds.attrs

    # Get meteo profiles
    meteo_profiles, meteo_info = get_meteo(initial_date, range, meteorology_source)

    if channels is None:
        channels_: list[str] = rf.channel.values.tolist()
        channels = channels_

    # For channel
    for channel_ in channels:
        if channel_ in rf.channel.values:
            dataset = rayleigh_fit_channel(
                channel_,
                rf,
                initial_date,
                final_date,
                meteo_profiles,
                meteo_info,
                reference_range,
                smooth_window,
            )

            file_nc, _ = rayleigh2earlinet(dataset, output_dir=output_dir)

            if save_fig:
                plot_rayleigh_fit(
                    file_nc, output_dir=output_dir, range_limits=range_limits
                )
    lidar_ds.close()
    return None