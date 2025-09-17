import datetime as dt
from datetime import datetime
from pathlib import Path
from typing import Any
import numpy as np
import xarray as xr
import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt


from gfatpy.lidar.quality_assurance.dead_time import binning, get_valid_an_pc_values, cost_function


def tau_cmax_plot(c_max_range: list[float] | np.ndarray[Any, np.dtype[np.float64]],
                  optimal_taus: list[float] | np.ndarray[Any, np.dtype[np.float64]],
                  pc_signal_channel: str,
                  target_date: str | dt.date,
                  savefig: bool = True,
                  plot_dir: Path = Path.cwd()
                  ):
    
    """Plots the results of optimal_taus vs C_max.
    
    Args:
        c_max_range (np.array): pc threshold candidates.
        optimal_taus (np.array): Optimal tau values.
        pc_signal_channel (str): Channel name.
        target_date (str): Target date.
        savefig (bool): Save the plot. Default=False.
        plot_dir (Path): Path to save the plot. Default=Path.cwd().
        
    Returns:
        None
    """
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y%m%d")

    fig,ax = plt.subplots(figsize=(6,4))
    ax.plot(c_max_range,optimal_taus,  marker='.',linestyle='-',color='b',label=r'Optimal $\tau$')

    ax.set_ylabel(r'Optimal $\tau$ [ns]',fontsize=10)
    ax.set_xlabel(r'$C_{max}$ [MHz]',fontsize=10)
    ax.set_title('Optimal tau vs C_max',fontsize=10)
    ax.legend(fontsize=12)
    xtick_locs, xtick_labels = ax.get_xticks(), ax.get_xticklabels()
    ytick_locs, ytick_labels = ax.get_yticks(), ax.get_yticklabels()
    ax.set_xticks(xtick_locs)
    ax.set_xticklabels(xtick_labels,fontsize=10)
    ax.set_yticks(ytick_locs)
    ax.set_yticklabels(ytick_labels,fontsize=10)
    if savefig==True:
        target_date_str = target_date.strftime("%y%m%dT%H%M%S")
        fig.savefig(plot_dir / f'tau_cmax_{pc_signal_channel}_{target_date_str}.png')


def dead_time_corr_study_prf(signal_an: xr.DataArray, 
                             signal_pc: xr.DataArray,
                             taus_cmax: pd.DataFrame,
                             pc_signal_channel: str, 
                             c_max_treshold: float = 100,
                             max_corr_range: float = 350,
                             plot_crop_range: tuple = (0,2000),
                             reference_range: float = 500,
                             debugging: bool = False, 
                             save_debug_plot: bool = False, 
                             plot_dir: Path | str | None = None):
    
    """
    Study the effect of the dead time correction in the correlation range and 
    select the best tau and C_max pair.
    
    Args:
        signal_an (xr.Dataset): Analog signal.
        signal_pc (xr.Dataset): Photon counting signal.
        taus_cmax (pd.DataFrame): Dead time values and pc thresholds candidates.
        pc_signal_channel (str): Photon counting channel name.
        c_max_treshold (float): Photon counting threshold in MHz for range in which to calculate corr. Default=100.
        max_corr_range (float): Maximum correlation range. Default=350.
        plot_crop_range (tuple): Plot crop range to limit plot and calculation range. Default=(0,2000).
        reference_range (float): Reference range in whicih to normalise an signal to pc. Default=500.
        debugging (bool): Debugging mode with additonal plots. Default=False.
        save_debug_plot (bool): Save the plot. Default=False.
        plot_dir (str | None): Path to save the plot. Default=None means current working directory.
        
    Returns:
        best_tau (float): Optimal dead time value.
        best_cmax (float): Optimal pc threshold value.
    """
    
    """Crop the signals using plot_crop_range"""

    if isinstance(plot_dir, str):
        plot_dir = Path(plot_dir)
    if plot_dir is None:
        plot_dir = Path.cwd()

    # Crop pc and an signals for a better plot in the near-medium range and select a time range (nightime): 
    #plot_crop_range = (0,2000)    # dt correction effect important when the signal i sstrong -> near range
    raw_pc_prf = signal_pc.sel(range=slice(*plot_crop_range))
    raw_an_prf = signal_an.sel(range=slice(*plot_crop_range))
    

    """Apply dt correction by hand using taus and C_max from dead_time_finder_channel_victor"""
    # 1) Load the (taus,C_max) pairs and correct of dt:
    C_max = taus_cmax['c_max'].values                                          
    taus = taus_cmax[f'dead_time_{pc_signal_channel}'].values
    # 2) Dead time correction by hand:
    dt_pc_signals = []
    for t in taus:
        dt_pc = raw_pc_prf / (1 - raw_pc_prf * (t*1e-3))   # dt correction with tau in us
        dt_pc_signals.append(dt_pc)
    """Apply C_max treshold and select the valid zone after overlap peak"""
    # 1) To select zone after the overlap, we select range after the max (overlap)
    max_idx = np.where(raw_pc_prf.values==np.max(raw_pc_prf.values))[0][0] # type: ignore
    min_range = raw_pc_prf.range.values[max_idx]
    max_range = plot_crop_range[1]
    cut_raw_pc_prf = raw_pc_prf.sel(range=slice(min_range,max_range))
    # 2) Now we apply C_max treshold:
    c_max = c_max_treshold                     # MHz
    mask = (cut_raw_pc_prf<c_max).values       # boolean mask
    cut_raw_pc_prf = cut_raw_pc_prf[mask]      # masked array that fulfill c<c_max and after the overlap

    if debugging==True:
        # Plot 1 -> effect of the dt correction in the raw pc signals
        fig_1,ax_1=plt.subplots(figsize=(9,5))        
        ax_1.plot(raw_an_prf.range,raw_an_prf, color ='black', label='raw_an') #type: ignore
        ax_1.plot(raw_pc_prf.range,raw_pc_prf, color ='blue', label='raw_pc') #type: ignore
        #ax_1.plot(n_raw_an.range,n_raw_an, color='black', label='norm_an')
        #ax_1.plot(dt_pc_signals[0].range,dt_pc_signals[0], label=f'tau = {taus[0]}')  # equivalent to raw signal
        #ax_1.plot(dt_pc_signals[1].range,dt_pc_signals[1], label=f'tau = {taus[1]}')  # really bad tau value -> bad result
        ax_1.plot(dt_pc_signals[2].range,dt_pc_signals[2], label=f'tau = {taus[2]}')
        ax_1.plot(dt_pc_signals[3].range,dt_pc_signals[3], label=f'tau = {taus[3]}')
        ax_1.plot(dt_pc_signals[4].range,dt_pc_signals[4], label=f'tau = {taus[4]}')
        ax_1.plot(dt_pc_signals[5].range,dt_pc_signals[5], label=f'tau = {taus[5]}')
        ax_1.plot(dt_pc_signals[6].range,dt_pc_signals[6], label=f'tau = {taus[6]}')
        ax_1.hlines(y=c_max,xmin=0,xmax=plot_crop_range[1], color='red', linestyle='--', label=f'Treshold: {c_max} [MHz]')
        ax_1.fill_between(cut_raw_pc_prf.range,y1=cut_raw_pc_prf,y2=c_max, alpha=0.3, color='green', label='Valid corr. zone')
        ax_1.set_xlim(0,plot_crop_range[1])
        ax_1.legend(fontsize=9)

        if save_debug_plot==True:
            fig_1.savefig(plot_dir / f'dt_effect_and_valid_corr_range_{pc_signal_channel}_{raw_pc_prf.time.dt.strftime("%y%m%d").values}.png')

    """Corr Calculations: using scipy.signal.pearsonr and a LS fit to obtain slope and offset"""
    # 1) Crop the signals to the correlation range:
    min_corr_range = cut_raw_pc_prf.range.values[0]  # first range of the already cut signal
    max_corr_range = max_corr_range                  # max range for corr. as a user parameter
    if min_corr_range>max_corr_range:
        min_corr_range, max_corr_range = 150,350
    raw_an_corr_range = raw_an_prf.sel(range=slice(min_corr_range,max_corr_range))  # not normalised
    corr_cut_pc_signals = [s.sel(range=slice(min_corr_range,max_corr_range)) for s in dt_pc_signals]
    # 2) Correlation calculations:
    r_pearson = []
    p_pearson = []
    slopes = []
    offset = []
    for i,s in enumerate(corr_cut_pc_signals):
        # 2.1) Correlation with scipy.signal.pearsonr:  (Not really necessary)
        # Use the raw an signal for corr. calculations
        #print(s.values.shape,raw_an_corr_range.values.shape)
        r,p = pearsonr(s.values,raw_an_corr_range.values)
        r_pearson.append(r)
        p_pearson.append(p)
        # 2.2) Correlation with LS fit:
        fit_params = np.polyfit(raw_an_corr_range.values,s.values,1)
        m,o = fit_params
        slopes.append(m)
        offset.append(o)
        if debugging==True:
        # Plot 2 -> correlation figures:
            fig_2,ax_2 = plt.subplots(figsize=(4,4))
            ax_2.plot(raw_an_corr_range.values,s.values,'b.',label = f'tau = {taus[i]} [ns]' )
            ax_2.plot(raw_an_corr_range.values,np.polyval(fit_params,raw_an_corr_range.values), label = f'y={m:.3f}x + {o:.3f}')
            ax_2.legend()
            if save_debug_plot==True:
                fig_2.savefig(plot_dir / f'corr_{pc_signal_channel}_{taus[i]}_{C_max[i]}_{raw_pc_prf.time.dt.strftime("%y%m%d").values}.png')
    
    # 3) Select the best tau and C_max pair that gave closest to zero offset.
    best_idx = np.argmin(np.abs(offset))   # Which correlation gave closest to zero offset
    best_tau, best_cmax = taus[best_idx], C_max[best_idx]

    """Create df with results for all c_max and taus"""
    result_df = pd.DataFrame()
    result_df['c_max'] = C_max
    result_df['tau'] = taus
    result_df['r_pearson'] = np.array(r_pearson).round(6)
    result_df['p_pearson'] = p_pearson
    result_df['slopes'] = slopes
    result_df['offsets'] = offset
    #result_df['r_spearman'] = r_spearman
    #result_df['p_spearman'] = p_spearman
    #result_df = result_df.round(6)
    if debugging==True:
        print(result_df)
        if save_debug_plot==True:
            result_df.to_csv(plot_dir / f'dt_study_results_{pc_signal_channel}_{raw_pc_prf.time.dt.strftime("%y%m%d").values}.csv')
    
    """Final plot in the correlation range with the best tau and C_max and the dt_effects"""
    if debugging==True:
        # Plot 3 -> dt effect in the corr range and the best tau:
        # Normalise an to pc for better plot
        # Divide by the own signal in that value to transport it to 0,1 and then scale with the pc signal.
        # NOTE: if the selected range doesn't exactly exits, we select the 'nearest'.
        n_raw_an = (raw_an_prf / raw_an_prf.sel(range=reference_range,method='nearest'))* raw_pc_prf.sel(range=reference_range,method='nearest')
        n_raw_an_corr_range = n_raw_an.sel(range=slice(min_corr_range,max_corr_range))
        
        fig_3,ax_3= plt.subplots(figsize=(8,5))
        
        for i,s in enumerate(corr_cut_pc_signals[2:]):
            ax_3.plot(s.range,s,label=f'corr = {r_pearson[i+2].round(6)} ; tau = {taus[i+2]} [ns]')
            if i==best_idx:
                ax_3.fill_between(s.range,y1=s-2,y2=s+2,alpha=0.3,color='lime',label=f'Best tau = {taus[i+2]} [ns] and C_max = {C_max[i+2]} [MHz]')

        ax_3.plot(corr_cut_pc_signals[0].range,corr_cut_pc_signals[0],color='blue',label='raw_pc')
        ax_3.plot(n_raw_an_corr_range.range,n_raw_an_corr_range,color='black',label='norm_an')
        ax_3.set_ylabel('Raw pc signal [MHz]',fontsize=10)
        ax_3.set_xlabel('Range',fontsize=10)
        xtick_locs, xtick_labels = ax_3.get_xticks(), ax_3.get_xticklabels()
        ytick_locs, ytick_labels = ax_3.get_yticks(), ax_3.get_yticklabels()
        ax_3.set_xticks(xtick_locs)
        ax_3.set_xticklabels(xtick_labels,fontsize=10)
        ax_3.set_yticks(ytick_locs)
        ax_3.set_yticklabels(ytick_labels,fontsize=10)
        ax_3.legend(fontsize=9)

        if save_debug_plot==True:
            fig_3.savefig(plot_dir / f'dt_study_results_{pc_signal_channel}_{raw_pc_prf.time.dt.strftime("%y%m%d").values}.png')

    return best_tau, best_cmax


def dead_time_assesment_by_channel(
        lidar: xr.Dataset,
        an_signal_channel: str,
        pc_signal_channel: str,
        ini_corr_time: str | dt.datetime, 
        end_corr_time: str | dt.datetime,
        savefig: bool,
        an_threshold: float = 0.01,
        debugging: bool = True,
        tau_range: list[float] | np.ndarray[Any, np.dtype[np.float64]] = np.arange(2., 10., 0.01),
        c_max_range: list[float] | np.ndarray[Any, np.dtype[np.float64]] = np.arange(10., 100., 10.),
        pc_bin_width: float = 1.0,
        output_dir: Path = Path.cwd()
        ):
    
    """Find the optimal dead time value for a given channel by applying different 
    pc thresholds to obtain dt and then studying corraltion between an and dt corrected pc signals.

    Args:
        lidar (Path): Lidar data file.
        an_signal_channel (str): Analog channel name.
        pc_signal_channel (str): Photon counting channel name.
        ini_corr_time (str | dt.datetime): initial time of the range from which the profile for corr study is selected
        end_corr_time (str | dt.datetime): final time of the range from which the profile for corr study is selected
        savefig (bool): Save the plot. Default=False.
        an_threshold (float): Analog threshold in mV. Default=0.01.
        debugging (bool): Debugging mode. Default=True. Wheter to show additional correlation plots or not.
        tau_range (list | np.darray): Candidate dead time values. Default=np.arange(2, 10, 0.01).
        c_max_range (list | np.darray): Candidate pc thresholds. Default=np.arange(0, 100, 10).
        pc_bin_width (float): Width of the bin. Default=1.0. In MHz.
        output_dir (Path): Path to save the results and plots. Default=Path.cwd().
        

    Returns:
        best_tau (float): Optimal dead time value.
        best_cmax (float): Optimal pc threshold value.
    """

    if isinstance(tau_range, list):
        tau_range = np.array(tau_range)

    target_date = lidar.time.values[0].astype(str).split("T")[0].replace("-", "")
    signal_an = lidar[f"signal_{an_signal_channel}"]
    signal_pc = lidar[f"signal_{pc_signal_channel}"]


    optimal_taus = []
    J_values = []
    for c in c_max_range:
        # 1) Treshold condition:
        valid_signal_an,valid_signal_pc = get_valid_an_pc_values(signal_an=signal_an,
                                                            signal_pc=signal_pc,
                                                            pc_threshold=c,
                                                            an_threshold=an_threshold)
        #print('valid values ok')

        # 2) Binning:
        median_pc, median_an, std_an = binning(signal_an = valid_signal_an, 
                                             signal_pc = valid_signal_pc, 
                                             pc_signal_channel= pc_signal_channel,
                                             target_date=target_date,
                                             pc_binning_range=(0,c),
                                             pc_bin_width=pc_bin_width, # pc_bin_width in MHz
                                             plot_dir = output_dir,
                                             savefig = savefig )


        #print('binning ok')
        # 3) Minimising and obtaining the optimal tau:
        J, optimal_tau = cost_function(tau_range = tau_range, 
                                       median_an = median_an, 
                                       median_pc = median_pc, 
                                       std_an = std_an, 
                                       pc_signal_channel = pc_signal_channel,
                                       target_date = target_date, 
                                       savefig = savefig,
                                       plot_dir = output_dir)
        J_values.append(J)
        optimal_taus.append(optimal_tau)
        #print('minimisation ok')

    # 4) Plotting:
    tau_cmax_plot(
        c_max_range= c_max_range,
        optimal_taus= optimal_taus,
        pc_signal_channel= pc_signal_channel,
        target_date= target_date,
        savefig= savefig,
        plot_dir= output_dir)

    taus_cmax = pd.DataFrame()
    taus_cmax['c_max'] = c_max_range
    taus_cmax[f'dead_time_{pc_signal_channel}'] = optimal_taus
    
    """Study which pair (tau,C_max) is the best for the dead time correction using the 1st profile"""
    if isinstance(ini_corr_time, dt.datetime):
        ini_corr_time = ini_corr_time.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(end_corr_time, dt.datetime):
        end_corr_time = end_corr_time.strftime("%Y-%m-%dT%H:%M:%S")

    raw_pc = signal_pc.sel(time=slice(ini_corr_time,end_corr_time))
    raw_an = signal_an.sel(time=slice(ini_corr_time,end_corr_time))
    raw_pc_prf = raw_pc[0]     # 1st signal in the time range -> individual profile
    raw_an_prf = raw_an[0]     # 1st signal in the time range -> individual profile
    best_tau, best_cmax = dead_time_corr_study_prf(signal_an= raw_an_prf, 
                             signal_pc = raw_pc_prf,
                             taus_cmax = taus_cmax,
                             pc_signal_channel = pc_signal_channel, 
                             c_max_treshold = 100,
                             max_corr_range =  350,
                             plot_crop_range = (0,2000),
                             reference_range = 500,
                             debugging = debugging)

    return best_tau, best_cmax
    
    """Now we could use this for several days and chek that the best result is always for 50 MHz"""
    """Then average the tau of the different days similar to the 2009 article"""


