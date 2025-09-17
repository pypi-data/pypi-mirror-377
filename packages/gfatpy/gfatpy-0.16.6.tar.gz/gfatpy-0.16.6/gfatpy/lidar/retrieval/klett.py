import numpy as np
import pandas as pd

import xarray as xr
from pathlib import Path
from matplotlib import pyplot as plt
from scipy import integrate
from scipy.integrate import cumulative_trapezoid as cumtrapz
from typing import Any, Tuple, Union

from loguru import logger

from gfatpy.atmo.atmo import transmittance
from gfatpy.lidar.utils.types import ParamsDict
from gfatpy.lidar.utils.utils import refill_overlap, signal_to_rcs
from gfatpy.utils.plot import color_list

def klett_rcs(
    rcs_profile: np.ndarray[Any, np.dtype[np.float64]],
    range_profile: np.ndarray[Any, np.dtype[np.float64]],
    beta_mol_profile: np.ndarray[Any, np.dtype[np.float64]],
    reference: Tuple[float, float],
    lr_part: float | np.ndarray[Any, np.dtype[np.float64]] = 45.,
    lr_mol: float = 8 * np.pi / 3,
    beta_aer_ref: float = 0,
) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Calculate aerosol backscattering using Classical Klett algorithm verified with Fernald, F. G.: Appl. Opt., 23, 652-653, 1984.

    Args:
        rcs_profile (np.ndarray): 1D signal profile.
        range_profile (np.ndarray): 1D range profile with the same shape as rcs_profile.
        beta_mol_profile (np.ndarray): 1D array containing molecular backscatter values.
        lr_mol (float): Molecular lidar ratio (default value based on Rayleigh scattering).
        lr_part (float, optional): Aerosol lidar ratio (default is 45 sr).
        reference (Tuple[float, float]): Range interval (ymin and ymax) for reference calculation.
        beta_aer_ref (float, optional): Aerosol backscatter at reference range (ymin and ymax). Defaults to 0.

    Returns:
        np.ndarray: Aerosol-particle backscattering profile.
    """

    if isinstance(lr_part, float):
        lr_part = np.full(len(range_profile), lr_part)
    if isinstance(lr_mol, float):
        lr_mol = np.full(len(range_profile), lr_mol) # type: ignore

    ymin, ymax = reference
    ymid = (ymin + ymax) / 2

    particle_beta = np.zeros(len(range_profile))

    ymiddle = np.abs(range_profile - ymid).argmin()

    range_resolution = np.median(np.diff(range_profile)).astype(float)

    idx_ref = np.logical_and(range_profile >= ymin, range_profile <= ymax)

    if not idx_ref.any():
        raise ValueError("Range [ymin, ymax] out of rcs size.")

    calib = np.nanmean(
        rcs_profile[idx_ref] / (beta_mol_profile[idx_ref] + beta_aer_ref)
    )

    # from Correct(ed) Klett–Fernald algorithm for elastic aerosol backscatter retrievals: a sensitivity analysis
    # Johannes Speidel* AND Hannes Vogelmann
    # https://doi.org/10.1364/AO.465944
    # Eq. 10
    # Reminder: BR = lr_mol, BP = lr_part

    integral_in_Y = np.flip(cumtrapz( np.flip((lr_mol[:ymiddle] - lr_part[:ymiddle]) * beta_mol_profile[:ymiddle]), dx=range_resolution, initial=0) ) # type: ignore
    exp_Y = np.exp( -2 * integral_in_Y)

    integral_in_particle_beta = np.flip(cumtrapz(np.flip(lr_part[:ymiddle] * rcs_profile[:ymiddle] * exp_Y), dx=range_resolution, initial=0)) # type: ignore

    total_beta = (rcs_profile[:ymiddle] * exp_Y) / (calib + 2 * integral_in_particle_beta)

    particle_beta[:ymiddle] = total_beta - beta_mol_profile[:ymiddle]

    return particle_beta

def quasi_beta(
    rcs_profile: np.ndarray[Any, np.dtype[np.float64]],
    calibration_factor: float,
    range_profile: np.ndarray[Any, np.dtype[np.float64]],
    params: dict | ParamsDict,
    lr_part: float | np.ndarray = 45.0,    
    full_overlap_height: float = 1000.0,    
    debug: bool = False,
) -> np.ndarray:

    #calculate beta attenuated 
    att_beta = rcs_profile / calibration_factor 
    
    star_beta = att_beta / transmittance(params["molecular_alpha"], range_profile)**2 - params["molecular_beta"]

    star_alpha = star_beta * lr_part

    #refill overlap
    star_alpha = refill_overlap(star_alpha, range_profile, full_overlap_height) # type: ignore

    # T2 = np.ones(len(range_profile))
    # for i in range(1, len(range_profile)):
    #     T2[i] = T2[i-1] * np.exp(-2 * (params["molecular_alpha"][i-1] + star_alpha[i-1]) * (range_profile[i] - range_profile[i-1]))

    # quasi_beta1 = att_beta / T2  - params["molecular_beta"]
    quasi_beta = att_beta / transmittance(params["molecular_alpha"] + star_alpha, range_profile)**2 - params["molecular_beta"]

    quasi_alpha = quasi_beta * lr_part    

    if debug:
        fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(10, 5), sharey=True)
        #Axis 1: plot RCS
        ax[0].plot(att_beta, range_profile, lw=2, label="attenuated beta")
        ax[0].set_xscale("log")
        ax[0].set_ylim(0, 9000)
        ax[0].set_xlabel("attenuated beta, [a.u.]")
        ax[0].legend()    
        #Axis 2: plot calibration
        ax[1].plot(1e6*quasi_beta, range_profile, lw=2, label="quasi beta")
        ax[1].plot(1e4*quasi_alpha, range_profile, lw=2, ls = '--', label="star alpha")
        ax[1].set_xscale("linear")
        ax[1].set_ylim(0, 9000)
        ax[1].set_xlabel("quasi beta, [a.u.]")
        ax[1].legend()
        fig.savefig(Path().cwd() / 'quasi_beta.png')

    return quasi_beta

def iterative_beta(
    rcs_profile: np.ndarray,
    calibration_factor: float,
    range_profile: np.ndarray,
    params: dict | ParamsDict,
    lr_part: float | np.ndarray = 45.0,    
    full_overlap_height: float = 1000.0,
    free_troposphere_height: float = 5000.0,    
    debug: bool = False,
    iterations: int = 10,
    tolerance: float = 0.01
) -> np.ndarray:

    alpha_part_previous = np.zeros(len(range_profile))
    beta_part = np.zeros((iterations, len(range_profile)))
    backscattering_ratio = np.zeros((iterations, len(range_profile)))
    relative_diff_beta_previous = 1.0
    beta_part_previous = params["molecular_beta"]
    colors = color_list(iterations)
    resolution = np.median(np.diff(range_profile)).astype(float)

    for idx in range(iterations):
        #Molecular atmosphere
        signal_mol = calibration_factor * params["molecular_beta"] * transmittance(params["molecular_alpha"] + alpha_part_previous, range_profile)**2 / range_profile**2
        rcs_mol = signal_to_rcs(signal_mol, range_profile)
        
        #calculate backscattering ratio
        R = rcs_profile / rcs_mol - 1

        beta_part_current = R * params["molecular_beta"]
        
        if debug:
            beta_part[idx,:] = beta_part_current
            backscattering_ratio[idx,:] = R            

        integral_beta_previous = np.trapz(beta_part_previous[range_profile < free_troposphere_height], dx=resolution)
        integral_beta_current = np.trapz(beta_part_current[range_profile < free_troposphere_height], dx=resolution)

        relative_diff_beta_current = np.abs(integral_beta_current - integral_beta_previous) / integral_beta_previous

        if np.abs(relative_diff_beta_current) < tolerance:            
            break
        else:
            beta_part_previous = beta_part_current
            relative_diff_beta_previous = relative_diff_beta_current            
            alpha_part_previous = refill_overlap(beta_part_current * lr_part, range_profile, full_overlap_height)

    #raise if no convergence
    # if idx == iterations - 1:
    #     raise ValueError("No convergence in iterative beta retrieval.")

    if debug:
        fig, ax = plt.subplots(ncols=4, nrows=1, figsize=(10, 5), sharey=True)
        #Axis 1: plot rcs mol
        ax[0].plot(rcs_mol, range_profile, lw=2, label="mol")
        ax[0].plot(rcs_profile, range_profile, lw=2, label="part")
        ax[0].set_xscale("log")
        ax[0].set_ylim(0, 9000)
        ax[0].set_xlabel("RCS, [a.u.]")
        ax[0].legend()
        #Axis 4: plot backscattering ratio
        for i in range(iterations):
            ax[1].plot(backscattering_ratio[i,:], range_profile, lw=2, color=colors[i], label=f"{i}")        
        ax[1].set_xscale("linear")
        ax[1].set_ylim(0, 9000)
        ax[1].set_xlabel("R, [a.u.]")
        ax[1].legend(fontsize=5)
        #Axis 3: plot beta part
        if "particle_beta" in params:
            ax[2].plot(1e6*params["particle_beta"], range_profile, lw=2, label="synthetic")
        for i in range(iterations):
            ax[2].plot(1e6*beta_part[i,:], range_profile, lw=2, color=colors[i], label=f"{i}")        
        ax[2].set_xscale("linear")
        ax[2].set_ylim(0, 9000)
        ax[2].set_xlabel(r"$\beta$, [a.u.]")
        ax[2].legend(fontsize=5)
        #Axis 4: plot relative diff of beta
        for i in range(iterations):
            ax[3].plot(100*(beta_part[i,range_profile < free_troposphere_height] - params['particle_beta'][range_profile < free_troposphere_height])/params['particle_beta'][range_profile < free_troposphere_height], range_profile[range_profile < free_troposphere_height], lw=2, color=colors[i], label=f"{i}")
        ax[3].set_xscale("linear")
        ax[3].set_ylim(0, 9000)
        ax[3].set_xlabel(r"$\varepsilon_{\beta_{p}}$, [%]")
        ax[3].legend(fontsize=5)

        fig.savefig(Path(__file__).parent.parent.parent.parent / 'tests' / 'figures' / 'iterative_beta.png')        
    
    return beta_part_current
    
def klett_likely_bins(
    rcs_profile: np.ndarray[Any, np.dtype[np.float64]],
    att_mol_beta: np.ndarray[Any, np.dtype[np.float64]],
    heights: np.ndarray[Any, np.dtype[np.float64]],
    min_height: float = 1000,
    max_height: float = 1010,
    window_size: int = 50,
    step: int = 1,
):
    window_size // 2
    i_bin, e_bin = np.searchsorted(heights, [min_height, max_height])

    for i in np.arange(i_bin, e_bin + 1):
        rcs_profile / rcs_profile

    return rcs_profile

def find_lidar_ratio(
    rcs: np.ndarray[Any, np.dtype[np.float64]],
    height: np.ndarray[Any, np.dtype[np.float64]],
    beta_mol: np.ndarray[Any, np.dtype[np.float64]],
    lr_mol: float,
    reference_aod: float,
    mininum_height: float = 0,
    lr_initial: float = 50,
    lr_resol: float = 1,
    max_iterations: int = 100,
    rel_diff_aod_percentage_threshold: float = 1,
    debugging: bool = False,
    klett_reference: Tuple[float, float] = (7000, 8000),
) -> Tuple[float, float | None, bool]:
    """Iterative process to find the lidar ratio (lr) that minimizes the difference between the measured and the calculated aerosol optical depth (aod).

    Args:
        rcs (np.ndarray[Any, np.dtype[np.float64]]): Range Corrected Signal
        height (np.ndarray[Any, np.dtype[np.float64]]): Range profile
        beta_mol (np.ndarray[Any, np.dtype[np.float64]]): Molecular backscattering coefficient profile
        lr_mol (float): Molecular lidar ratio
        reference_aod (float): Reference aerosol optical depth
        mininum_height (float, optional): Fullover height. Defaults to 0.
        lr_initial (float, optional): _description_. Defaults to 50.
        lr_resol (float, optional): _description_. Defaults to 1.
        max_iterations (int, optional): _description_. Defaults to 100.
        rel_diff_aod_percentage_threshold (float, optional): _description_. Defaults to 1.
        debugging (bool, optional): _description_. Defaults to False.
        klett_reference (Tuple[float, float], optional): _description_. Defaults to (7000, 8000).

    Returns:
        Tuple[float, float | None, bool]: _description_
    """

    # Calculate range resolution
    range_resolution = np.median(np.diff(height)).item()

    # Initialize loop
    lr_, iter_, run, success = lr_initial, 0, True, False
    rel_diff_aod = None

    while run:
        iter_ = iter_ + 1

        # Calculate aerosol backscatter
        beta_ = klett_rcs(
            rcs, height, beta_mol, lr_part=lr_, lr_mol=lr_mol, reference=klett_reference
        )

        # Refill beta profile from minimum height to surface to avoid overlap influence
        beta_ = refill_overlap(beta_, height, fulloverlap_height=mininum_height)

        # Calculate aerosol optical depth
        aod_ = integrate.simps(beta_ * lr_, dx=range_resolution)

        # Calculate relative difference between measured and calculated aod
        rel_diff_aod = 100 * (aod_ - reference_aod) / reference_aod

        if debugging:
            print(
                "lidar_ratio: %.1f | lidar_aod: %.3f| reference_aod: %.3f | relative_difference: %.1f%%"
                % (lr_, aod_, reference_aod, rel_diff_aod)
            )

        # Check convergence
        if np.abs(rel_diff_aod) > rel_diff_aod_percentage_threshold:
            if rel_diff_aod > 0:
                if lr_ < 20:
                    run = False
                    print("No convergence. LR goes too low.")
                else:
                    lr_ = lr_ - 1
            else:
                if lr_ > 150:
                    run = False
                    print("No convergence. LR goes too high.")
                else:
                    lr_ = lr_ + 1
        else:
            print("LR found: %f" % lr_)
            run = False
            success = True

        # Check maximum number of iterations
        if iter_ == max_iterations:
            run = False
            print("No convergence. Too many iterations.")

    return lr_, rel_diff_aod, success

def get_calibration_factor(P_elastic: np.ndarray,
                           range_profile: np.ndarray,
                           params: dict | pd.DataFrame,
                           beta_part_profile: np.ndarray,
                           lr_part: float | np.ndarray,                           
                           range_to_average: Tuple[float, float],
                           full_overlap_height: float = 1000.,
                           backscattering_ratio_threshold: float = 1.1,
                           debug: bool = False
                           ) -> Union[Tuple[float, float], Tuple[np.ndarray, np.ndarray]]:

    #fill overlap
    beta_part_profile = refill_overlap(beta_part_profile, range_profile, full_overlap_height)
       
    if isinstance(lr_part, float):
        lr_part = np.full(len(range_profile), lr_part)
    
    #Retrieve inverse squared transmittance 
    T2_elastic = 1/transmittance(params["molecular_alpha"] + beta_part_profile*lr_part, range_profile)**2 # type: ignore
    
    #Get calibration factor
    calibration = signal_to_rcs(P_elastic, range_profile) / (params["molecular_beta"] + beta_part_profile) * T2_elastic

    # Cut heights below overlap height
    calibration = refill_overlap(calibration, range_profile, full_overlap_height, fill_with=np.nan)

    # Filter for backscatter ratio greater than 1.1 and only lower layers
    bakcscattering_ratio = (beta_part_profile + params['molecular_beta']) / params['molecular_beta']
    calibration[bakcscattering_ratio < backscattering_ratio_threshold] = np.nan

    # Filter for area with stable standard deviation    
    ymin, ymax = range_to_average
    idx_ref = np.logical_and(range_profile >= ymin, range_profile <= ymax)
    mean_calib = np.nanmean(calibration[idx_ref])
    std_calib = np.nanstd(calibration[idx_ref])   

    if debug:
        fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(10, 5), sharey=True)
        #Axis 1: plot RCS
        ax[0].plot(signal_to_rcs(P_elastic, range_profile), range_profile, lw=2, label="RCS")
        ax[0].set_xscale("log")
        # ax[0].set_xlim(1e1, 1e6)
        ax[0].set_ylim(0, 9000)
        ax[0].set_xlabel("RCS, [a.u.]")
        ax[0].legend()
        #Axis 2: plot calibration
        ax[1].plot(calibration, range_profile, lw=2, label="calibration")
        ax[1].set_xscale("linear")
        # ax[1].set_xlim(0., 20.)
        ax[1].set_ylim(0, 9000)
        ax[1].set_xlabel("calibration, [a.u.]")
        ax[1].legend()
        fig.savefig(Path(__file__).parent.parent.parent.parent / 'tests' / 'figures' / 'get_calibration_factor.png')
    
    return mean_calib, std_calib # type: ignore

def get_calibration_factor_klett_quicklook(
    rcs_elastic: xr.DataArray,
    mol_properties: pd.DataFrame,
    lr_part: float,
    reference_height_klett: Tuple[float, float],
    full_overlap_height: float,
    backscattering_ratio_threshold: float = 1.1) -> xr.DataArray:

    # Get range profile
    range_profile = rcs_elastic.range.values
    
    #Get time profile
    time_profile = rcs_elastic.time.values
    
    
    #Repeat the molecular properties of that hour for each time
    molecular_beta2D = np.tile(mol_properties["molecular_beta"][np.newaxis, :], (len(time_profile), 1))
    molecular_alpha2D = np.tile(mol_properties["molecular_alpha"][np.newaxis, :], (len(time_profile), 1))

    #Create an empty matrix with dimensions (z, time)
    beta_part_klett = np.zeros((len(time_profile), len(range_profile)))
    
    #Calculate beta part using Klett algorithm for each time
    for i in range(len(time_profile)):
        beta_part = klett_rcs(rcs_elastic.isel(time=i).values,
                                        range_profile,
                                        mol_properties["molecular_beta"],
                                        lr_part = lr_part,
                                        reference = reference_height_klett,
                                        beta_aer_ref = 0.
                                        )
        

        beta_part = refill_overlap(beta_part, range_profile, 
                                          fulloverlap_height=full_overlap_height)

        beta_part_klett[i, :] = beta_part # Guardamos el perfil en la matriz
        
    #Calculate alpha part using lidar ratio    
    alpha_part_klett = beta_part_klett * lr_part
    
    #Calculate transmittance
    transmittance_elastic = np.zeros((len(time_profile), len(range_profile)))
    
    for i, t_i in enumerate(time_profile):
        transmittance_elastic[i, :] = transmittance(molecular_alpha2D[i, :] + alpha_part_klett[i, :], range_profile) 
    
    
    #Calculate calibration factor
    calibration_factor = rcs_elastic / ((molecular_beta2D + beta_part_klett) * transmittance_elastic**2)
    
    return calibration_factor

def get_calibration_factor_ajuste1(
    rcs_elastic: xr.DataArray,
    mol_properties: pd.DataFrame,
    lr_part: float,
    reference_height_klett: Tuple[float, float],
    full_overlap_height: float,
    backscattering_ratio_threshold: float,
    fixed_height: float = 1000.,
    fixed_time: float | str = '00:00:00',
    linear_fitting_if_fixed_height = False,
    linear_fitting_if_fixed_time = False,
    ) -> xr.DataArray:
    
    # Get range profile
    range_profile = rcs_elastic.range.values
    
    #Get time profile
    time_profile = rcs_elastic.time.values
    
    #Repeat the molecular properties of that hour for each time
    molecular_beta2D = np.tile(mol_properties["molecular_beta"][np.newaxis, :], (len(time_profile), 1))
    molecular_alpha2D = np.tile(mol_properties["molecular_alpha"][np.newaxis, :], (len(time_profile), 1))

    #Create an empty matrix with dimensions (z, time)
    beta_part_klett = np.zeros((len(time_profile), len(range_profile)))
    
    #Calculate beta part using Klett algorithm for each time
    for i in range(len(time_profile)):
        beta_part = klett_rcs(rcs_elastic.isel(time=i).values,
                                        range_profile,
                                        mol_properties["molecular_beta"],
                                        lr_part = lr_part,
                                        reference = reference_height_klett,
                                        beta_aer_ref = 0.
                                        )
        

        beta_part = refill_overlap(beta_part, range_profile, 
                                          fulloverlap_height=full_overlap_height)

        beta_part_klett[i, :] = beta_part # Guardamos el perfil en la matriz
        
    #Calculate alpha part using lidar ratio    
    alpha_part_klett = beta_part_klett * lr_part
    
    #Calculate transmittance
    transmittance_elastic = np.zeros((len(time_profile), len(range_profile)))
    
    for i, t_i in enumerate(time_profile):
        transmittance_elastic[i, :] = transmittance(molecular_alpha2D[i, :] + alpha_part_klett[i, :], range_profile) 
    
    #Calculate backscattering ratio
    backscattering_ratio = (beta_part_klett + molecular_beta2D) / molecular_beta2D
    
    
    #Ensure that 'linear_fitting_if_fixed_height' or 'linear_fitting_if_fixed_time' is set to True.
    if not linear_fitting_if_fixed_height and not linear_fitting_if_fixed_time:
        raise ValueError("At least one of the linear fitting flags must be True.")
    
    #Ensure that both not set to True at the same time
    if linear_fitting_if_fixed_height and linear_fitting_if_fixed_time:
        raise ValueError("Both linear fitting flags cannot be True at the same time.")
    
    #Convert backscattering ratio, molecular beta, transmittance and RCS to xarray
    backscattering_ratio = xr.DataArray(backscattering_ratio, coords = {'time': time_profile, 'range': range_profile}, dims = ['time', 'range'])
    molecular_beta2D = xr.DataArray(molecular_beta2D, coords = {'time': time_profile, 'range': range_profile}, dims = ['time', 'range'])
    transmittance_elastic = xr.DataArray(transmittance_elastic, coords = {'time': time_profile, 'range': range_profile}, dims = ['time', 'range'])
    rcs_elastic = xr.DataArray(rcs_elastic, coords = {'time': time_profile, 'range': range_profile}, dims = ['time', 'range'])
    
    if linear_fitting_if_fixed_height:
        R_sel = backscattering_ratio.sel(range = fixed_height, method = 'nearest')
        beta_mol_sel = molecular_beta2D.sel(range = fixed_height, method = 'nearest')
        transmittance_sel = transmittance_elastic.sel(range = fixed_height, method = 'nearest')
        RCS_sel = rcs_elastic.sel(range = fixed_height, method = 'nearest')
        
     
    if linear_fitting_if_fixed_time:
        R_sel = backscattering_ratio.sel(time = fixed_time, method = 'nearest')
        beta_mol_sel = molecular_beta2D.sel(time = fixed_time, method = 'nearest')
        transmittance_sel = transmittance_elastic.sel(time = fixed_time, method = 'nearest')
        RCS_sel = rcs_elastic.sel(time = fixed_time, method = 'nearest')
        
    Rmod = R_sel * beta_mol_sel * transmittance_sel**2
    print(Rmod.values)
    print(RCS_sel.values)    
    #add linear fit with nunpy polyfit
    idx_not_nan = np.logical_and(~np.isnan(Rmod), ~np.isnan(RCS_sel))
    rlt5 = R_sel<backscattering_ratio_threshold
    idx = np.logical_and(idx_not_nan, rlt5)
    plt.plot(idx)
    plt.xlim(200, 230)
    m, b = np.polyfit(Rmod[idx], RCS_sel[idx], 1)
    print(m, b)
        
    R_correlation =np.corrcoef(Rmod[idx], RCS_sel[idx])[0,1]
    calibration_factor = m
        
    return calibration_factor, b, R_correlation

def get_calibration_factor_ajuste2(
    rcs_elastic: xr.DataArray,
    mol_properties: pd.DataFrame,
    lr_part: float,
    reference_height_klett: Tuple[float, float],
    full_overlap_height: float,
    backscattering_ratio_threshold: float,
    fixed_height: float = 1000.,
    fixed_time: float | str = '00:00:00',
    linear_fitting_if_fixed_height = False,
    linear_fitting_if_fixed_time = False,
    ) -> xr.DataArray:
    
    # Get range profile
    range_profile = rcs_elastic.range.values
    
    #Get time profile
    time_profile = rcs_elastic.time.values
    
    #Repeat the molecular properties of that hour for each time
    molecular_beta2D = np.tile(mol_properties["molecular_beta"][np.newaxis, :], (len(time_profile), 1))
    molecular_alpha2D = np.tile(mol_properties["molecular_alpha"][np.newaxis, :], (len(time_profile), 1))

    #Create an empty matrix with dimensions (z, time)
    beta_part_klett = np.zeros((len(time_profile), len(range_profile)))
    
    #Calculate beta part using Klett algorithm for each time
    for i in range(len(time_profile)):
        beta_part = klett_rcs(rcs_elastic.isel(time=i).values,
                                        range_profile,
                                        mol_properties["molecular_beta"],
                                        lr_part = lr_part,
                                        reference = reference_height_klett,
                                        beta_aer_ref = 0.
                                        )
        

        beta_part = refill_overlap(beta_part, range_profile, 
                                          fulloverlap_height=full_overlap_height)

        beta_part_klett[i, :] = beta_part # Guardamos el perfil en la matriz
        
    
    #Calculate transmittance
    transmittance_molecular = np.zeros((len(time_profile), (len(range_profile))))
    
    for i, t_i in enumerate(time_profile):
        transmittance_molecular[i, :] = transmittance(molecular_alpha2D[i, :], range_profile) 
        
    #Calculate backscattering ratio
    backscattering_ratio = (beta_part_klett + molecular_beta2D) / molecular_beta2D
    
    
    #Calculate k_star
    k_star = rcs_elastic / ((molecular_beta2D + beta_part_klett) * transmittance_molecular**2)
    
    #Calculate cumulative alpha
    cumulative_alpha = integrate.cumulative_trapezoid(mol_properties["particle_alpha2D"], dx=range_profile[1]-range_profile[0], axis=1, initial=0)
    
    #Ensure that 'linear_fitting_if_fixed_height' or 'linear_fitting_if_fixed_time' is set to True.
    if not linear_fitting_if_fixed_height and not linear_fitting_if_fixed_time:
        raise ValueError("At least one of the linear fitting flags must be True.")
    
    #Ensure that both not set to True at the same time
    if linear_fitting_if_fixed_height and linear_fitting_if_fixed_time:
        raise ValueError("Both linear fitting flags cannot be True at the same time.")
    
    #Convert backscattering ratio, molecular beta, transmittance and RCS to xarray
    k_star = xr.DataArray(k_star, coords = {'time': time_profile, 'range': range_profile}, dims = ['time', 'range'])
    cumulative_alpha = xr.DataArray(cumulative_alpha, coords = {'time': time_profile, 'range': range_profile}, dims = ['time', 'range'])
    backscattering_ratio = xr.DataArray(backscattering_ratio, coords = {'time': time_profile, 'range': range_profile}, dims = ['time', 'range'])
    
    if linear_fitting_if_fixed_height:
        R_sel = backscattering_ratio.sel(range = fixed_height, method = 'nearest')
        k_star_sel = np.log(k_star.sel(range = fixed_height, method = 'nearest'))
        cumulative_alpha_sel = cumulative_alpha.sel(range = fixed_height, method = 'nearest')
        
     
    if linear_fitting_if_fixed_time:
        R_sel = backscattering_ratio.sel(time = fixed_time, method = 'nearest')
        k_star_sel = np.log(k_star.sel(time = fixed_time, method = 'nearest'))
        cumulative_alpha_sel = cumulative_alpha.sel(time = fixed_time, method = 'nearest')
      
    #add linear fit with nunpy polyfit
    idx_not_nan = np.logical_and(~np.isnan(k_star_sel), ~np.isnan(cumulative_alpha_sel))
    rlt5 = R_sel<backscattering_ratio_threshold
    idx = np.logical_and(idx_not_nan, rlt5)
    m, b = np.polyfit(cumulative_alpha_sel[idx], k_star_sel[idx], 1)

        
    R_correlation =np.corrcoef(cumulative_alpha_sel[idx], k_star_sel[idx])[0,1]
    calibration_factor = np.exp(b)
        
    return calibration_factor, m, R_correlation