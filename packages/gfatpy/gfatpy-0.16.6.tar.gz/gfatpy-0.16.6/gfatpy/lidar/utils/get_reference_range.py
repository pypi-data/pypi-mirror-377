from typing import Tuple
import numpy as np
import pandas as pd
import xarray as xr

from gfatpy.atmo.rayleigh import molecular_properties
from gfatpy.lidar.utils.file_manager import channel2info
from gfatpy.lidar.utils.utils import signal_to_rcs
from gfatpy.utils.utils import linear_fit

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


def _get_mask_residual(
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
    mask.attrs = {
        "long_name": "mask for residual within standard deviation",
        "units": "#",
    }
    return mask

def get_reference_range(channel: str,
    signal: xr.DataArray,
    meteo_profiles: pd.DataFrame,
    reference_candidate_limits: Tuple[float, float],
    reference_half_window: float = 500.,
    dw_thresolds: tuple[float, float] = (1., 3.),
) -> tuple[float, float] | None:
    """It provides the optimal reference range for the signal.

    Args:
        channel (str): Channel of the signal.
        signal (xr.DataArray): Signal to be analyzed.
        meteo_profiles (pd.DataFrame): Meteo profiles from gfatpy.atmo module. 
        reference_candidate_limits (Tuple[float, float]): Reference candidate limits.
        reference_half_window (float, optional): Half Window to split the reference_candidate_limits. Defaults to 500..
        dw_thresolds (tuple[float, float], optional): Durbin-Watson threshold. Defaults to (1., 3.).

    Returns:
        tuple[float, float] | None: Reference range. None if no reference range is found.
    """    

    wavelength, _, _, _ = channel2info(channel)

    full_ranges = signal.range.values

    # Molecular properties from meteo profiles
    mol_properties = molecular_properties(
        wavelength, meteo_profiles["pressure"], meteo_profiles["temperature"], full_ranges
    )

    # Reference ranges
    mol_properties = mol_properties.sel(range=slice(reference_candidate_limits[0]-2*reference_half_window, reference_candidate_limits[1]+2*reference_half_window))
    signal = signal.sel(range=slice(reference_candidate_limits[0]-2*reference_half_window, reference_candidate_limits[1]+2*reference_half_window))
    
    # RCS
    rcs = signal_to_rcs(signal, signal.range)

    # Attenuated Molecular Backscatter
    attenuated_molecular_backscatter = mol_properties["atten_molecular_beta"]
    
    #Condition: residual(z) > 0
    candidates = {}
    candidates['residual'] = {}
    for range_ in np.arange(reference_candidate_limits[0], reference_candidate_limits[1], 2*reference_half_window):        
        candidate_ = (range_-reference_half_window, range_+reference_half_window)

        # Attenuated Backscatter
        attenuated_backscatter = _attenuated_backscatter(
            rcs, attenuated_molecular_backscatter, candidate_
        )

        #residual mask
        mask = _get_mask_residual(attenuated_backscatter, attenuated_molecular_backscatter, candidate_)        
        if mask.values.all():
            candidates['residual'][range_] = {}
            candidates['residual'][range_]['candidate'] = candidate_
            candidates['residual'][range_]['attenuated_backscatter'] = attenuated_backscatter

    if len(candidates['residual']) == 0:
        return None

    candidates['extinction'] = {}
    for range_ in candidates['residual'].keys():
        #Reference range candidate
        candidate_ = candidates['residual'][range_]['candidate']

        # Attenuated Backscatter
        attenuated_backscatter_ = candidates['residual'][range_]['attenuated_backscatter'].sel(range=slice(*candidate_)) 
        attenuated_molecular_backscatter_ = attenuated_molecular_backscatter.sel(range=slice(*candidate_))  
        stats_ = linear_fit(attenuated_backscatter_.range.values, (attenuated_backscatter_/attenuated_molecular_backscatter_).values)

        #Extinction filter        
        extinction, std_extinction = -0.5*stats_["parameters"][1], 0.5*stats_["standard_deviation_parameters"][1]
        if std_extinction >= extinction:
            candidates['extinction'][range_] = {}
            candidates['extinction'][range_]['candidate'] = candidate_
            candidates['extinction'][range_]['attenuated_backscatter'] = attenuated_backscatter
    
    if len(candidates['extinction']) == 0:
        return None

    candidates['durbin_watson'] = {}
    for range_ in candidates['extinction'].keys():   
        candidate_ = candidates['extinction'][range_]['candidate']
        attenuated_backscatter = candidates['extinction'][range_]['attenuated_backscatter']
        attenuated_backscatter_ = attenuated_backscatter.sel(range=slice(*candidate_))
        stats = linear_fit(attenuated_backscatter_.range.values, attenuated_backscatter_.values)
        
        if stats["durbin_watson"] > dw_thresolds[0] and stats["durbin_watson"] < dw_thresolds[1]:
            candidates['durbin_watson'][range_] = {}        
            candidates['durbin_watson'][range_]['candidate'] = candidate_
            candidates['durbin_watson'][range_]['attenuated_backscatter'] = attenuated_backscatter
            candidates['durbin_watson'][range_]['stats'] = stats 

    if len(candidates['durbin_watson']) == 0:
        return None

    candidates['final'] = candidates['durbin_watson'].copy()
    weighting_function = np.nan*np.ones(len(candidates['final'].keys()))
    for idx, range_ in enumerate(candidates['final'].keys()):
        candidate_ = candidates['final'][range_]['candidate']
        attenuated_backscatter = candidates['final'][range_]['attenuated_backscatter']
        stats = candidates['final'][range_]['stats']

        mean_ = np.mean(attenuated_backscatter.sel(range=slice(*candidate_)).values)
        std_ = np.std(attenuated_backscatter.sel(range=slice(*candidate_)).values)
        slope_ = stats["parameters"][1]
        msre_ = stats["msre"]
        anderson_ = stats["anderson"][0]
        weighting_function[idx] = np.abs(mean_)*std_*np.abs(slope_)*msre_*anderson_

    final_ranges = np.array(list(candidates['final'].keys()))
    final_reference_range = final_ranges[np.argmin(weighting_function)]
    final_reference_slice = candidates['final'][final_reference_range]['candidate']

    return final_reference_slice

    # beta_ratio_candidates = {} 
    # for range_ in candidates['extinction'].keys():
    #     attenuated_backscatter = candidates['extinction'][range_]['attenuated_backscatter']
    #     candidate_ = candidates['extinction'][range_]['candidates']
    #     moving_fit = candidates['extinction'][range_]['moving_fit']

    #     att_R = _attenuated_backscattering_ratio(attenuated_backscatter, attenuated_molecular_backscatter, candidate_)
    #     att_R_criterion = np.isclose(
    #     att_R, 1, rtol=rel_diff_thrs_att_back_ratio
    # )
    #     if att_R_criterion.any():
    #         beta_ratio_candidates[range_] = {}
    #     beta_ratio_candidates[range_]['candidates'] = [(range_-slice_window, range_+slice_window) for range_ in ranges[att_R_criterion]]
    #     beta_ratio_candidates[range_]['attenuated_backscatter'] = attenuated_backscatter
    #     beta_ratio_candidates[range_]['moving_fit'] = moving_fit 

    # snr_candidates = {}
    # for range_ in candidates['durbin_watson'].keys():
    #     candidate_ = candidates['durbin_watson'][range_]['candidates']
    #     attenuated_backscatter = candidates['durbin_watson'][range_]['attenuated_backscatter']
    #     stats = candidates['durbin_watson'][range_]['stats']

    #     snr = _snr(attenuated_backscatter, candidate_)
    #     snr_criterion = np.logical_and( snr > snr_thresold)
    #     if snr_criterion.any():
    #         snr_candidates[range_] = {}
    #         snr_candidates[range_]['candidates'] = [(range_-slice_window, range_+slice_window) for range_ in ranges[dw_criterion]]
    #         snr_candidates[range_]['attenuated_backscatter'] = attenuated_backscatter
    #         snr_candidates[range_]['stats'] = stats 
