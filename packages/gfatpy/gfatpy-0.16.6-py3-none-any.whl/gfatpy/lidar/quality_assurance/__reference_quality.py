import datetime as dt
from pathlib import Path
from pdb import set_trace
from typing import Tuple
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

from gfatpy.atmo.atmo import transmittance
from gfatpy.utils import utils
from gfatpy.atmo.rayleigh import molecular_properties
from gfatpy.lidar.utils.file_manager import channel2info
from gfatpy.lidar.utils.utils import LIDAR_INFO, signal_to_rcs
# from gfatpy.utils.durbin_watson import linear_fit
from gfatpy.utils.optimized import moving_linear_fit


def _get_window_size(
    reference_ranges: tuple[float, float], ranges: np.ndarray[float]
) -> int:
    """It provides the window size of a given reference range (e.g., 6000 - 7000 meters).

    Args:
        reference_ranges (tuple[float, float]): Reference range in meters.
        ranges (np.dnarray[float]): Range array in meters.

    Returns:
        int: Window size.
    """
    dz = np.median(np.diff(ranges))  # type: ignore
    reference_idxs = (
        np.floor(reference_ranges[0] / dz).astype(int),
        np.floor(reference_ranges[1] / dz).astype(int),
    )
    return reference_idxs[1] - reference_idxs[0]


def _attenuated_backscatter(
    rcs: xr.DataArray,
    attenuated_molecular_backscatter: xr.DataArray,
    reference_range: Tuple[float, float],
) -> xr.DataArray:
    """Calculate the attenuated backscatter.

    Args:

        - channel (str): Channel to calculate the Rayleigh Fit.
        - rcs (xr.DataArray): Range Corrected Signal.
        - attenuated_molecular_backscatter (xr.DataArray): Attenuated Molecular Backscatter.
        - reference_range (Tuple[float, float]): Reference range to normalize.

    Returns:

        - xr.DataArray: Attenuated backscatter.
    """

    attenuated_backscatter = attenuated_molecular_backscatter.sel(
        range=slice(*reference_range)
    ).mean("range") * (rcs / rcs.sel(range=slice(*reference_range)).mean("range"))

    return attenuated_backscatter


def _residual(
    attenuated_backscatter: xr.DataArray, attenuated_molecular_backscatter: xr.DataArray
) -> xr.DataArray:
    """Calculate the residual between the attenuated backscatter and the attenuated molecular backscatter.

    Args:
        attenuated_backscatter (xr.DataArray): Attenuated backscatter.
        attenuated_molecular_backscatter (xr.DataArray): Attenuated molecular backscatter.

    Returns:
        xr.DataArray: Residual (difference) between the attenuated backscatter and the attenuated molecular backscatter.
    """

    residual = attenuated_backscatter - attenuated_molecular_backscatter
    residual.attrs = {
        "long_name": "residual between attenuated backscatter and attenuated molecular backscatter",
        "units": "m{-1} sr{-1}",
    }
    return residual


def _attenuated_backscattering_ratio(
    attenuated_backscatter: xr.DataArray,
    attenuated_molecular_backscatter: xr.DataArray,
    reference_ranges: tuple[float, float],
) -> xr.DataArray:
    """Calculate the attenuated backscattering ratio.

    Args:
        attenuated_backscatter (xr.DataArray): Attenuated backscatter.
        attenuated_molecular_backscatter (xr.DataArray): Attenuated molecular backscatter.
        reference_ranges (tuple[float, float]): Reference range to normalize.

    Returns:
        xr.DataArray: Attenuated backscattering ratio.
    """
    window_size_bin = _get_window_size(
        reference_ranges=reference_ranges, ranges=attenuated_backscatter.range.values
    )

    attenuated_backscattering_ratio = (
        (attenuated_backscatter / attenuated_molecular_backscatter)
        .rolling(range=window_size_bin, center=True)
        .mean("range")
    )
    attenuated_backscattering_ratio.attrs = {
        "long_name": "attenuated backscattering ratio",
        "units": "#",
    }

    return attenuated_backscattering_ratio


def _extinction_from_attenuated_backscatter(
    attenuated_backscatter: xr.DataArray,
    attenuated_molecular_backscatter: xr.DataArray,
    reference_ranges: tuple[float, float],
) -> Tuple[xr.DataArray, xr.DataArray, xr.DataArray]:
    """Calculate the extinction from the attenuated backscatter. The Durbin-Watson statistic is also calculated.

    Args:

        - attenuated_backscatter (xr.DataArray): Attenuated backscatter.
        - reference_ranges (tuple[float, float]): Aerosol-free region reference range.

    Returns:

        - Tuple[xr.DataArray, xr.DataArray]: Extinction, its standard deviation and Durbin-Watson statistic.

    References:

        - Baars, H., et al. (2016). https://doi.org/10.5194/acp-16-5111-2016
    """

    ranges = attenuated_backscatter.range.values
    window_size_bin = _get_window_size(reference_ranges=reference_ranges, ranges=ranges)

    results = moving_linear_fit(
        ranges,
        attenuated_backscatter.values/attenuated_molecular_backscatter.values,
        **{"length": window_size_bin, "degree": 1},
    )
    extinction = -0.5*results["slope"]
    std_extinction = 0.5*results["std_slope"]

    extinction = xr.DataArray(
        data=extinction,
        dims=["range"],
        coords={"range": ranges},
        attrs={
            "long_name": "extinction",
            "units": "m{-1} sr{-1}",
        },
    )
    std_extinction = xr.DataArray(
        data=std_extinction,
        dims=["range"],
        coords={"range": ranges},
        attrs={
            "long_name": "std_extinction",
            "units": "m{-1} sr{-1}",
        },
    )

    durbin_watson_statistic = xr.DataArray(
        data=d,
        dims=["range"],
        coords={"range": ranges},
        attrs={
            "long_name": "Durbin-Watson statistic",
            "units": "#",
        },
    )

    return extinction, std_extinction, durbin_watson_statistic


def _slope_attenuated_backscatter(
    attenuated_backscatter: xr.DataArray,
    reference_ranges: tuple[float, float],
) -> xr.DataArray:
    """Calculate the slope of the attenuated backscatter.

    Args:
        attenuated_backscatter (xr.DataArray): Attenuated backscatter.
        reference_ranges (tuple[float, float]): Reference range to normalize.

    Returns:
        xr.DataArray: Slope of the attenuated backscatter.
    """

    ranges = attenuated_backscatter.range.values
    dz = np.median(np.diff(ranges))  # type: ignore
    window_size_bin = _get_window_size(reference_ranges=reference_ranges, ranges=ranges)

    # Apply derivative
    slope_attenuated_backscatter = savgol_filter(
        1e6 * attenuated_backscatter.values,
        window_size_bin,
        1,
        deriv=1,
        delta=dz,
        mode="nearest",
        cval=np.nan,
    )  # Calculate 1st derivative

    slope_attenuated_backscatter = xr.DataArray(
        slope_attenuated_backscatter,
        dims=["range"],
        coords={"range": ranges},
        attrs={"long_name": "slope of attenuated backscatter", "units": "m{-2} sr{-1}"},
    )
    return slope_attenuated_backscatter


def _slope_attenuated_molecular_backscatter(
    attenuated_molecular_backscatter: xr.DataArray,
    reference_ranges: tuple[float, float],
) -> xr.DataArray:
    """Calculate the slope of the attenuated molecular backscatter.

    Args:
        attenuated_molecular_backscatter (xr.DataArray): Attenuated molecular backscatter.
        reference_ranges (tuple[float, float]): Reference range to normalize.

    Returns:
        xr.DataArray: Slope of the attenuated molecular backscatter.
    """

    ranges = attenuated_molecular_backscatter.range.values
    dz = np.median(np.diff(ranges))  # type: ignore
    window_size_bin = _get_window_size(reference_ranges=reference_ranges, ranges=ranges)

    # Apply derivative
    slope_attenuated_molecular_backscatter = savgol_filter(
        1e6 * attenuated_molecular_backscatter.values,
        window_size_bin,
        1,
        deriv=1,
        delta=dz,
        mode="nearest",
        cval=np.nan,
    )  # Calculate 1st derivative

    slope_attenuated_molecular_backscatter = xr.DataArray(
        slope_attenuated_molecular_backscatter,
        dims=["range"],
        coords={"range": ranges},
        attrs={
            "long_name": "slope of attenuated molecular backscatter",
            "units": "m{-2} sr{-1}",
        },
    )
    return slope_attenuated_molecular_backscatter


def _snr(
    signal: xr.DataArray,
    reference_ranges: tuple[float, float],
    mode: str = "analog",
) -> xr.DataArray:
    """Calculate the signal-to-noise ratio (SNR) of the analog signal.

    Args:
        signal (xr.DataArray): Signal.
        noise (xr.DataArray): Noise.
        reference_ranges (tuple[float, float]): Reference range to normalize.

    Returns:
        xr.DataArray: Signal-to-noise ratio (SNR).
    """

    ranges = signal.range.values
    window_size_bin = _get_window_size(reference_ranges=reference_ranges, ranges=ranges)

    if mode == "analog":
        signal_ = signal.rolling(range=window_size_bin, center=True).mean("range")
        noise_ = signal.rolling(range=window_size_bin, center=True).std("range")
    else:
        # TODO: implement equation A10 from the paper Baars et al. (2016) DOI: 10.5194/acp-16-5111-2016
        signal_ = signal.rolling(range=window_size_bin, center=True).mean("range")
        noise_ = signal.rolling(range=window_size_bin, center=True).std("range")
        raise Warning(
            "Only analog mode is implemented. Retrieval is made with analog equations."
        )

    snr = signal_ / noise_
    snr.attrs = {
        "long_name": "signal-to-noise ratio",
        "units": "#",
    }
    return snr


def get_mask_attenuated_backscattering_ratio(
    attenuated_backscattering_ratio: xr.DataArray,
    relative_difference_threshold: float = 0.05,
) -> xr.DataArray:
    """Get mask for attenuated backscattering ratio cloase to one with relative difference lower than a threshold.

    Args:
        attenuated_backscattering_ratio (xr.DataArray): Attenuated backscattering ratio.
        relative_difference_threshold (float, optional): Relative difference threshold. Defaults to 0.05.

    Returns:
        xr.DataArray: Mask for attenuated backscattering ratio.
    """
    # Get boolean variable where the attenuated backscattering ratio is within the thresholds
    mask = np.isclose(
        attenuated_backscattering_ratio, 1, rtol=relative_difference_threshold
    )

    mask = xr.DataArray(
        mask, dims=["range"], coords={"range": attenuated_backscattering_ratio.range}
    )
    mask.attrs = {
        "long_name": "mask for attenuated backscattering ratio within thresholds",
        "thresholds": f"relative difference lower than {relative_difference_threshold}",
        "units": "#",
    }
    return mask


def get_mask_extinction(
    extinction: xr.DataArray,
    std_extinction: xr.DataArray,
) -> xr.DataArray:
    """Get mask for extinction larger than the standard deviation.

    Args:
        extinction (xr.DataArray): Extinction.
        std_extinction (xr.DataArray): Standard deviation of the extinction.

    Returns:
        xr.DataArray: Mask for extinction > extinction std.
    """
    # Get boolean variable where the extinction is within the standard deviation
    mask = extinction > std_extinction
    mask = xr.DataArray(mask, dims=["range"], coords={"range": extinction.range})
    mask.attrs = {
        "long_name": "mask for extinction larger than standard deviation",
        "units": "#",
    }
    return mask


def get_mask_durbin_watson(
    durbin_watson_statistic: xr.DataArray,
    threshold_limits: tuple[float, float] = (1, 3),
) -> xr.DataArray:
    """Get mask for Durbin-Watson statistic within threshold limits.

    Args:
        durbin_watson_statistic (xr.DataArray): Durbin-Watson statistic.
        threshold_limits (tuple[float, float], optional): Threshold limits. Defaults to (1, 3).

    Returns:
        xr.DataArray: Mask for Durbin-Watson statistic.
    """

    # Get boolean variable where the Durbin-Watson statistic is within the threshold limits
    mask = (durbin_watson_statistic > threshold_limits[0]) & (
        durbin_watson_statistic < threshold_limits[1]
    )
    mask = xr.DataArray(
        mask, dims=["range"], coords={"range": durbin_watson_statistic.range}
    )
    mask.attrs = {
        "long_name": "mask for Durbin-Watson statistic within threshold limits",
        "thresholds": f"{threshold_limits[0]} < D-W < {threshold_limits[1]}",
        "units": "#",
    }
    return mask


def get_mask_nsr(
    nsr: xr.DataArray, threshold_limits: tuple[float, float] = (0.0, 0.15)
) -> xr.DataArray:
    """Get mask for NSR within threshold limits.

    Args:
        nsr (xr.DataArray): Noise-to-signal ratio.
        threshold_limits (tuple[float, float], optional): Threshold limits. Defaults to (0.0, 0.15).

    Returns:
        xr.DataArray: Mask for NSR.
    """
    # Get boolean variable where the Durbin-Watson statistic is within the threshold limits
    mask = (nsr > threshold_limits[0]) & (nsr < threshold_limits[1])
    mask = xr.DataArray(mask, dims=["range"], coords={"range": nsr.range})
    mask.attrs = {
        "long_name": "mask for NSR within threshold limits",
        "thresholds": f"{threshold_limits[0]} < NSR < {threshold_limits[1]}",
        "units": "#",
    }
    return mask


def get_mask_residual(
    attenuated_backscatter: xr.DataArray,
    attenuated_molecular_backscatter: xr.DataArray,
    reference_ranges: tuple[float, float],
) -> xr.DataArray:
    """Get mask for residual within the standard deviation.

    Args:
        attenuated_backscatter (xr.DataArray): Attenuated backscatter.
        attenuated_molecular_backscatter (xr.DataArray): Attenuated molecular backscatter.
        reference_ranges (tuple[float, float]): Aerosol-free reference range.

    Returns:
        xr.DataArray: Mask for residual.
    """
    window_size_bin = _get_window_size(
        reference_ranges, attenuated_backscatter.range.values
    )

    # Get boolean variable where the residual is within the standard deviation
    att_beta_mean = attenuated_backscatter.rolling(
        range=window_size_bin, center=True
    ).mean("range")
    att_beta_mean = att_beta_mean.where(~np.isnan(att_beta_mean), drop=True)
    att_beta_std = attenuated_backscatter.rolling(
        range=window_size_bin, center=True
    ).std("range")
    att_beta_std = att_beta_std.where(~np.isnan(att_beta_std), drop=True)
    att_mol_beta_mean = attenuated_molecular_backscatter.rolling(
        range=window_size_bin, center=True
    ).mean("range")
    att_mol_beta_mean = att_mol_beta_mean.where(~np.isnan(att_mol_beta_mean), drop=True)
    att_mol_beta_std = attenuated_molecular_backscatter.rolling(
        range=window_size_bin, center=True
    ).std("range")    
    att_mol_beta_std = att_mol_beta_std.where(~np.isnan(att_mol_beta_std), drop=True)

    mask = (att_beta_mean + att_beta_std) > (att_mol_beta_mean - att_mol_beta_std)
    # mask = xr.DataArray(
    #     mask, dims=["range"], coords={"range": attenuated_backscatter.range}
    # )
    mask.attrs = {
        "long_name": "mask for residual within standard deviation",
        "units": "#",
    }
    
    # breakpoint()
    # fig, ax = plt.subplots()
    # att_mol_beta_mean.plot(ax=ax, ls = '--', label='Attenuated Molecular Backscatter')    
    # att_beta_mean.plot(ax=ax, ls = '--', label='Attenuated Backscatter')
    # (att_mol_beta_mean - att_mol_beta_std).plot(ax=ax, label='Attenuated Molecular Backscatter - std')
    # (att_beta_mean + att_beta_std).plot(ax=ax, label='Attenuated  Backscatter + std')
    # ax.legend()
    # fig.savefig(f'residual_condition.png')
    # breakpoint()

    return mask


def get_mask_slope_attenuated_backscatter(
    slope_attenuated_backscatter: xr.DataArray,
    slope_attenuated_molecular_backscatter: xr.DataArray,
    relative_difference_thershold: float = 0.1,
) -> xr.DataArray:
    """Get mask for slope of attenuated backscatter within threshold limits.

    Args:
        slope_attenuated_backscatter (xr.DataArray): Slope of attenuated backscatter.
        slope_attenuated_molecular_backscatter (xr.DataArray): Slope of attenuated molecular backscatter.
        relative_difference_thershold (float, optional): Relative difference threshold. Defaults to 0.1.

    Returns:
        xr.DataArray: Mask for slope of attenuated backscatter.
    """
    # Get boolean variable where the slope of the attenuated backscatter is within the threshold limits
    mask = np.isclose(
        slope_attenuated_backscatter,
        slope_attenuated_molecular_backscatter,
        rtol=relative_difference_thershold,
    )

    mask = xr.DataArray(
        mask, dims=["range"], coords={"range": slope_attenuated_backscatter.range}
    )
    mask.attrs = {
        "long_name": "mask for slope of attenuated backscatter within threshold limits",
        "thresholds": f"diff < {relative_difference_thershold}",
        "units": "#",
    }
    return mask


def get_rayleigh_fit_analysis_data(
    channel: str,
    rf_dataset: xr.Dataset,
    initial_date: dt.datetime,
    final_date: dt.datetime,
    meteo_profiles: pd.DataFrame,
    reference_ranges: Tuple[float, float],
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

    wavelength, _, polarization, mode = channel2info(channel)
    ranges = rf_dataset.range.values
    # RCS
    signal = (
        rf_dataset[f"signal_{channel}"]
        .sel(time=slice(initial_date, final_date))
        .mean("time")
    )
    rcs = signal_to_rcs(signal, signal.range)

    snr = _snr(signal, reference_ranges)

    # Molecular properties from meteo profiles
    mol_properties = molecular_properties(
        wavelength, meteo_profiles["pressure"], meteo_profiles["temperature"], ranges
    )

    # Attenuated Molecular Backscatter
    attenuated_molecular_backscatter = mol_properties["atten_molecular_beta"]

    # Attenuated Backscatter
    attenuated_backscatter = _attenuated_backscatter(
        rcs, attenuated_molecular_backscatter, reference_ranges
    )

    # Attenuated Backscattering Ratio
    attenuated_backscattering_ratio = _attenuated_backscattering_ratio(
        attenuated_backscatter, attenuated_molecular_backscatter, reference_ranges
    )
    attenuated_backscattering_ratio_mask = get_mask_attenuated_backscattering_ratio(
        attenuated_backscattering_ratio
    )

    # Residual
    residual = _residual(attenuated_backscatter, attenuated_molecular_backscatter)
    residual_mask = get_mask_residual(
        attenuated_backscatter, attenuated_molecular_backscatter, reference_ranges
    )

    # Slope of Attenuated Backscatter
    slope_attenuated_backscatter = _slope_attenuated_backscatter(
        attenuated_backscatter, reference_ranges
    )

    # Slope of Attenuated Molecular Backscatter
    slope_attenuated_molecular_backscatter = _slope_attenuated_molecular_backscatter(
        attenuated_molecular_backscatter, reference_ranges
    )

    slope_mask = get_mask_slope_attenuated_backscatter(
        slope_attenuated_backscatter, slope_attenuated_molecular_backscatter
    )

    # Extinction
    extinction, std_extinction, durbin_watson_statistic = (
        _extinction_from_attenuated_backscatter(
            attenuated_backscatter, reference_ranges
        )
    )

    extinction_mask = get_mask_extinction(extinction, std_extinction)
    durbin_watson_mask = get_mask_durbin_watson(durbin_watson_statistic)

    # SNR
    snr = _snr(signal, reference_ranges)
    nsr_mask = get_mask_nsr(1 / snr)

    # Combine all masks
    all_mask = np.logical_and.reduce(
        [
            attenuated_backscattering_ratio_mask,
            residual_mask,
            slope_mask,
            extinction_mask,
            durbin_watson_mask,
            nsr_mask,
        ],
        axis=0,
    )

    all_mask = xr.DataArray(
        all_mask,
        dims=["range"],
        coords={"range": ranges},
        attrs={"long_name": "all masks applied", "units": "#"},
    )

    dataset = xr.Dataset(
        data_vars={
            "attenuated_backscatter": attenuated_backscatter,
            "attenuated_molecular_backscatter": attenuated_molecular_backscatter,
            "attenuated_backscattering_ratio": attenuated_backscattering_ratio,
            "residual": residual,
            "slope_attenuated_backscatter": slope_attenuated_backscatter,
            "slope_attenuated_molecular_backscatter": slope_attenuated_molecular_backscatter,
            "extinction": extinction,
            "std_extinction": std_extinction,
            "durbin_watson_statistic": durbin_watson_statistic,
            "snr": snr,
            "attenuated_backscattering_ratio_mask": attenuated_backscattering_ratio_mask,
            "residual_mask": residual_mask,
            "slope_mask": slope_mask,
            "extinction_mask": extinction_mask,
            "durbin_watson_mask": durbin_watson_mask,
            "nsr_mask": nsr_mask,
            "mask": all_mask,
            "minimum_range": reference_ranges[0],
            "maximum_range": reference_ranges[1],
        },
        coords={"range": ranges},
        attrs={
            "lidar_location": rf_dataset.attrs["location"],
            "lidar_name": rf_dataset.attrs["system"],
            "channel": channel,
            "datetime_ini": initial_date.strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),  # FIXME: Dejar como estaba o pasar a ISO 8601?. Estaba en formato 20220808T12, ahora en 2022-08-08T12:00:00
            "datetime_end": final_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "datetime_format": "%Y-%m-%dT%H:%M:%S",
            "duration": (final_date - initial_date).total_seconds(),
            "duration_units": "seconds",
        },
    )
    dataset["range"].attrs["units"] = "km"
    dataset["range"].attrs["long_name"] = "height"

    # Get optimum reference range
    # window_size_bin = _get_window_size(reference_ranges, dataset.range.values)
    # slope, _, _, msre, anderson_coefficient, _  = durbin_watson_test(
    # dataset.range.values,
    # dataset.attenuated_backscatter.values,
    # **{"length": window_size_bin, "degree": 1},
    # )

    # ydata = rolling_window_test(dataset.attenuated_backscatter.values, window_size_bin).T
    # abs_mean_attenuated_backscatter = np.abs(np.nanmean(ydata, axis=0))
    # std_attenuated_backscatter = np.nanstd(ydata, axis=0)
    # breakpoint()
    # weighting_function = np.abs(slope) * msre * anderson_coefficient.statistic
    # optimum_range = ranges[np.argmin(weighting_function)]
    # dataset['optimum_range'] = xr.DataArray(optimum_range, dims=[], attrs={"units": "km", "long_name": "optimum range"})

    #Save optimum range as the first range fulfilling the conditions in all_mask
    if all_mask.any():
        optimum_range = dataset.range.values[all_mask.values][0]
    else:
        optimum_range = -999.
        
    dataset["optimum_range"] = xr.DataArray(
        optimum_range,
        dims=[],
        attrs={"units": "m", "long_name": "optimum refenence range"},
    )
    return dataset


def plot_reference_analysis(dataset, **kwargs):
    fig, ax = plt.subplots(6, 1, figsize=kwargs.get("figsize", (15, 10)), sharex=True)

    dataset["range"] = dataset["range"] / 1e3

    # Plot attenuated total and molecular backscatter
    (1e6 * dataset["attenuated_molecular_backscatter"]).plot(
        x="range", ax=ax[0], label="$\\beta_{mol}^{att}$", color="blue"
    )
    (1e6 * dataset["attenuated_backscatter"]).plot(
        x="range", ax=ax[0], label="$\\beta^{att}$", color="red"
    )
    # Plot attenuated backscatter applying all_mask
    (1e6 * dataset["attenuated_backscatter"].where(dataset["mask"])).plot(
        x="range", ax=ax[0], color="green", label="$masked \\beta^{att}$"
    )
    ax[0].set_xlabel("Height (km)")
    ax[0].set_ylabel("$\\beta_{att}$\n$[Mm^{-1} sr^{-1}]$")
    ax[0].set_xticklabels([])

    # ax[1].set_yscale('log')  # Uncomment this line
    ax[0].set_ylim(0.1, 8)
    ax[0].set_yscale("log")
    ax[0].set_xlabel(None)  # Remove this line
    # ax[0].set_yscale("log")  # Uncomment this line

    # Plot attenuated backscattering ratio
    dataset["attenuated_backscattering_ratio"].plot(
        x="range", ax=ax[1], label="backscattering ratio", color="red"
    )
    dataset["attenuated_backscattering_ratio"].where(
        dataset["attenuated_backscattering_ratio_mask"]
    ).plot(x="range", ax=ax[1], color="green", label="$masked \\beta^{att}$")
    # Add horizontal line at 1
    ax[1].axhline(1, color="k", linestyle="--")
    ax[1].set_ylabel("$R_{att}$\n[#]")
    ax[1].set_ylim(0.8, 1.3)
    ax[1].set_xlabel(None)
    # ax[1].set_yscale('log')

    # Plot slopes
    (1e3 * dataset["slope_attenuated_molecular_backscatter"]).plot(
        x="range",
        ax=ax[2],
        color="k",
        label="slope of $\\beta_{mol}^{att}$",
    )
    (1e3 * dataset["slope_attenuated_backscatter"]).plot(
        x="range", ax=ax[2], color="red", label="slope of $\\beta^{att}$"
    )
    (1e3 * dataset["slope_attenuated_backscatter"]).where(dataset["slope_mask"]).plot(
        x="range", ax=ax[2], color="green", label="masked slope of $\\beta^{att}$"
    )
    ax[2].set_xlabel("")
    ax[2].set_ylabel("d$\\beta_{att}/dz$\n$[km^{-1} sr^{-1} m^{-1}]$")
    ax[2].set_ylim(-0.5, 0.5)

    # Plot extinctions
    (1e9 * dataset["extinction"]).plot(
        x="range", ax=ax[3], color="red", label="extinction"
    )
    (1e9 * dataset["std_extinction"]).plot(
        x="range", ax=ax[3], color="blue", label="std extinction"
    )
    (1e9 * dataset["extinction"]).where(dataset["extinction_mask"]).plot(
        x="range", ax=ax[3], color="green", label="masked extinction"
    )
    ax[3].axhline(0, color="k", linestyle="--")
    ax[3].set_xlabel("")
    ax[3].set_ylabel("$\\alpha$\n$[Gm^{-1}]$")
    ax[3].set_ylim(-0.1, 0.25)
    ax[3].set_xlim(*kwargs.get("range_limits", (0, 10)))
    # ax[3].set_xticklabels(np.arange(3, 11, 1))

    # Plot durbin-watson statistic
    dataset["durbin_watson_statistic"].plot(
        x="range", ax=ax[4], color="red", label="Durbin-Watson"
    )
    dataset["durbin_watson_statistic"].where(dataset["durbin_watson_mask"]).plot(
        x="range", ax=ax[4], color="green", label="masked Durbin-Watson"
    )
    ax[4].axhline(1, color="k", linestyle="--")
    ax[4].axhline(3, color="k", linestyle="--")
    ax[4].set_xlabel("")
    ax[4].set_ylabel("D-W stat.,\n\[#]")
    ax[4].set_ylim(0, 4)

    # Plot SNR
    (1 / dataset["snr"]).plot(x="range", ax=ax[5], color="red", label="NSR")
    (1 / dataset["snr"]).where(dataset["nsr_mask"]).plot(
        x="range", ax=ax[5], color="green", label="mask NSR"
    )

    ax[5].axhline(0.15, color="k", linestyle="--")
    ax[5].set_xlabel("Height (km)")
    ax[5].set_ylabel("NSR\n\[#]")
    ax[5].set_ylim(0, 0.25)
    range_limits = kwargs.get("range_limits", (0, 10000.0))
    ax[5].set_xlim(range_limits[0] / 1e3, range_limits[1] / 1e3)
    ax[5].set_xticklabels(ax[4].get_xticks())

    for ax_ in ax:
        ax_.legend(loc="upper left", fontsize=8)
        # Set fontsize of the labels to 8
        ax_.tick_params(axis="both", which="major", labelsize=8)
        ax_.minorticks_on()
        ax_.grid(which="both", linestyle="--", alpha=0.5)

    fig.savefig(
        kwargs.get("output_dir", Path.cwd())
        / f"attenuated_molecular_backscatter_vs_rcs2attbeta_{dataset.attrs['channel']}_{dataset['minimum_range'].item()}-{dataset['maximum_range'].item()}.png",
        dpi=kwargs.get("dpi", 300),
        bbox_inches="tight",
    )
    return fig
