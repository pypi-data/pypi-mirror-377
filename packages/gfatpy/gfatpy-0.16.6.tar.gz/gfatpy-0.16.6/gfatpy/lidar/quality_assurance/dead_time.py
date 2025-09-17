import datetime as dt
from datetime import datetime
from pathlib import Path
from typing import Any
import numpy as np
import xarray as xr
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from gfatpy.lidar.preprocessing import preprocess
from gfatpy.utils.plot import color_list


def binning(
    signal_an: np.ndarray[Any, np.dtype[np.float64]],
    signal_pc: np.ndarray[Any, np.dtype[np.float64]],
    pc_signal_channel: str,
    target_date: str | dt.date,
    pc_binning_range: tuple[float, float] = (0, 50),
    pc_bin_width: float = 1.0,    
    plot_dir: Path = Path.cwd(),
    savefig: bool = False,
):
    """Binning of AN and PC daily signals.

    Args:
        signal_an (np.ndarray): Analog signal.
        signal_pc (np.ndarray): Photon counting signal.
        pc_signal_channel (str): Channel name.
        target_date (str | datetime.date): Target date.
        pc_binning_range (tuple[float, float]): Range of PC signal. Default=(0, 50). In MHz.
        pc_bin_width (float): Width of the bin. Default=1.0. In MHz.        
        plot_dir (Path): Path to save the plot. Default=Path.cwd().
        savefig (bool): Save the plot. Default=False.
    """

    def plot_binning(
        signal_an: np.ndarray[Any, np.dtype[np.float64]],
        signal_pc: np.ndarray[Any, np.dtype[np.float64]],
        median_pc: np.ndarray[Any, np.dtype[np.float64]],
        median_an: np.ndarray[Any, np.dtype[np.float64]],
        std_an: np.ndarray[Any, np.dtype[np.float64]],
        pc_signal_channel: str,
        target_date: str,
        plot_dir: Path,
        savefig: bool,
    ):
        fig, ax = plt.subplots(figsize=[10, 5])
        ax.scatter(signal_pc, signal_an, c="grey", s=0.5, label="raw")
        ax.errorbar(
            median_pc,
            median_an,
            yerr=std_an,
            linestyle="None",
            marker=".",
            color="red",
            label="binning",
        )
        ax.set_xlabel("PC signal, [MHz]")
        ax.set_ylabel("dc-corrected AN signal, [mV]")
        ax.set_title(f"{pc_signal_channel} | {target_date}")
        ax.set_yscale("linear")
        ax.set_xlim(*pc_binning_range)
        ax.legend(fontsize=10, loc="upper right")
        if savefig:
            plt.savefig(plot_dir / f'binning_{pc_signal_channel}_{target_date}.png')
        plt.close(fig)

    if isinstance(target_date, str):        
        target_date = datetime.strptime(target_date, "%Y%m%d")

    # Apply binning to pc and an
    bins = np.arange(
        pc_binning_range[0], pc_binning_range[1] + pc_bin_width, pc_bin_width
    )

    # Use numpy.digitize to get the bin indices for each element in signal_pc
    bin_indices = np.digitize(signal_pc, bins)

    median_an = np.array([np.median(signal_an[bin_indices == i]) for i in range(1, len(bins))])

    std_an = np.array([np.std(signal_an[bin_indices == i]) for i in range(1, len(bins))])
    median_pc = np.array([np.median(signal_pc[bin_indices == i]) for i in range(1, len(bins))])
    isnan = np.logical_and(np.isnan(median_pc), np.isnan(median_an), np.isnan(std_an))

    # Plot binning
    plot_binning(
        signal_an,
        signal_pc,
        median_pc,
        median_an,
        std_an,
        pc_signal_channel,
        target_date.strftime("%Y%m%d"),
        plot_dir,
        savefig=savefig,
    )

    return median_pc[~isnan], median_an[~isnan], std_an[~isnan]


def get_valid_an_pc_values(
    signal_an: xr.DataArray,
    signal_pc: xr.DataArray,
    pc_threshold: float,
    an_threshold: float,
) -> tuple[np.ndarray[Any, np.dtype[np.float64]], np.ndarray[Any, np.dtype[np.float64]]]:
    """Filter analog and photoncouting signal using analog and photoncouting thresholds and removing NaNs.

    Args:
        signal_an (xr.DataArray): Analog signal.
        signal_pc (xr.DataArray): Photon counting signal.
        pc_threshold (float): Photon counting threshold in MHz.
        an_threshold (float): Analog threshold in mV.

    Returns:
        tuple[np.ndarray[Any, np.dtype[np.float64]], np.ndarray[Any, np.dtype[np.float64]]]: Filtered analog and photoncouting signal.
    """

    gl_condition = np.logical_and(
        signal_an.values > an_threshold, signal_pc.values < pc_threshold
    )
    an = np.concatenate(signal_an.where(gl_condition).values, axis=0)
    pc = np.concatenate(signal_pc.where(gl_condition).values, axis=0)
    isnan = np.logical_and(np.isnan(an), np.isnan(pc))
    an = an[~isnan]
    pc = pc[~isnan]
    return an, pc


def cost_function(
    tau_range: np.ndarray[Any, np.dtype[np.float64]],
    median_an: np.ndarray[Any, np.dtype[np.float64]],
    median_pc: np.ndarray[Any, np.dtype[np.float64]],
    std_an: np.ndarray[Any, np.dtype[np.float64]],
    pc_signal_channel: str,
    target_date: str | dt.date,
    savefig: bool,
    plot_dir: Path = Path.cwd(),
) -> tuple[np.ndarray[Any, np.dtype[np.float64]], float]:
    """Cost function to find the optimal dead time value (tau).

    Args:
        tau_range (np.ndarray): Candidate dead time values.
        median_an (np.ndarray): Binned valid analog signal from `.binning` function.
        median_pc (np.ndarray): Binned valid photon counting signal from `.binning` function.
        std_an (np.ndarray): Standard deviation of the binned analog signal from `.binning` function.
        pc_signal_channel (str): Channel name.
        target_date (str | datetime.date): Target date.
        savefig (bool): Save the plot. Default=False.
        plot_dir (Path): Path to save the plot. Default=Path.cwd().

    Returns:
        tuple[np.ndarray[Any, np.dtype[np.float64]], float]: Cost function and optimal dead time value.
    """
    
    def plot_cost_function(
        tau_range: np.ndarray[Any, np.dtype[np.float64]],
        J: np.ndarray[Any, np.dtype[np.float64]],
        pc_signal_channel: str,
        plot_dir: Path,
        target_date: str,
        optimal_tau_index: int,
        savefig: bool,
    ):
        logJ = np.log(J)
        optimal_tau = tau_range[optimal_tau_index]
        fig, ax = plt.subplots(figsize=[15, 5])
        ax.plot(tau_range, logJ, c="blue", lw=2, label="J", zorder=1)
        ax.scatter(
            optimal_tau,
            logJ[optimal_tau_index],
            marker="p",
            s=50,
            color="yellow",
            label=f"optimal tau = {optimal_tau:.2f} ns",
            zorder=2,
        )
        ax.set_ylabel("log(J), [#]")
        ax.set_xlabel(r"$\tau$, [ns]")
        ax.minorticks_on()
        ax.grid(True, which="both", linestyle=":", linewidth=0.5, color=[0.3, 0.3, 0.3])
        ax.set_title(f"{pc_signal_channel} | {target_date}")
        ax.legend(fontsize=10, loc="upper center")
        if savefig:
            plt.savefig(plot_dir / f'cost_function_{pc_signal_channel}_{target_date}.png')
        plt.close(fig)

    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y%m%d")

    J = np.nan * np.ones(len(tau_range))
    for idx, tau_ in enumerate(tau_range):
        dt_pc = median_pc / (1 - tau_ * median_pc * 1e-3)
        if not np.isnan(dt_pc).any() and not np.isnan(median_an).any():
            try:
                fit_values = np.polyfit(dt_pc, median_an, 1)
                virtual_an = np.polyval(fit_values, dt_pc)
            except Exception as e:                
                print(e)
                raise ValueError("Error in fitting binned an and pc")

            try:
                # Cost function
                idx_zero = std_an == 0
                J[idx] = np.sum(
                    (median_an[~idx_zero] - virtual_an[~idx_zero]) ** 2
                    / std_an[~idx_zero] ** 2
                ) / len(median_an)
            except Exception as e:                
                print(e)
                raise ValueError("Error in cost function")
    optimal_tau_index = np.log(J).argmin().astype(int)

    plot_cost_function(
        tau_range=tau_range,
        J=J,
        pc_signal_channel=pc_signal_channel,
        plot_dir=plot_dir,
        target_date=target_date.strftime("%Y%m%d"),
        optimal_tau_index=optimal_tau_index,
        savefig=savefig,
    )
    optimal_tau = float(tau_range[optimal_tau_index])

    return J, optimal_tau


def plot_influence_of_dead_time_correction(
    tau_range: np.ndarray[Any, np.dtype[np.float64]],
    optimal_tau: float,
    median_an: np.ndarray[Any, np.dtype[np.float64]],
    median_pc: np.ndarray[Any, np.dtype[np.float64]],
    pc_signal_channel: str,
    target_date: str,
    plot_dir: Path,
    savefig: bool,
):
    fig, ax = plt.subplots(figsize=[15, 5])    
    h0_line, = ax.plot(median_pc, median_an, c="black", lw=1.5, zorder=2)
    colors = color_list(len(tau_range))
    handles = [None] * len(tau_range)
    for idx, tau_ in enumerate(tau_range):
        dt_pc = median_pc / (1 - tau_ * median_pc * 1e-3)
        handles[idx] = ax.scatter(dt_pc, median_an, #type: ignore
                                  color=colors[idx], alpha=0.7) 

    # Create a ScalarMappable object with the jet colormap and the range of values
    norm = mcolors.Normalize(vmin=tau_range.min(), vmax=tau_range.max())
    sm = cm.ScalarMappable(cmap='jet', norm=norm)
    sm.set_array([])  # Set a dummy array for the ScalarMappable

    # Add the colorbar to the figure
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', boundaries=tau_range, cmap='jet')

    cbar.set_label(r'$\tau$, [ns]')

    opt_dt_pc = median_pc / (1 - optimal_tau * median_pc * 1e-3)
    h_opt, = ax.plot(opt_dt_pc,median_an, c="red", lw=2, zorder=2) #type: ignore
    ax.legend(
        [h0_line,h_opt], #type: ignore
        ['raw', f"optimal tau [{optimal_tau:.2f} ns]"],
        fontsize=10,
        loc="upper left")
    # ax.legend([h0, handles[0], handles[-1]], fontsize=10, loc="upper left")
    ax.set_xlabel("dt-corrected PC signal, [MHz]")
    ax.set_ylabel("dc-corrected AN signal, [mV]")
    ax.set_title(f"{target_date} | {pc_signal_channel}")
    ax.grid(True, which="both", linestyle=":", linewidth=0.5, color=[0.3, 0.3, 0.3])
    fig.tight_layout()
    if savefig:
        plt.savefig(plot_dir / f'pc_taus_{pc_signal_channel}_{target_date}.png')
    plt.close(fig)

def plot_gluing_thresholds(
    signal_an: xr.DataArray,
    signal_pc: xr.DataArray,
    pc_threshold: float,
    an_threshold: float,
    target_date: str,
    plot_dir: Path,
    savefig: bool,
    range_limits: tuple[float, float],
):
    pc_signal_channel = str(signal_pc.name).split("_")[-1]

    fig, ax = plt.subplots(figsize=[15, 5])
    lan = signal_an.plot.line(x="range", c="grey", lw=0.5, label="an", ax=ax) #type: ignore
    lpc = signal_pc.plot.line(x="range", c="black", lw=0.5, label="pc", ax=ax) #type: ignore

    l1 = plt.hlines(
        pc_threshold, xmin=0, xmax=10000, color="darkred", ls="--", label="Cmax"
    )
    l2 = plt.hlines(
        an_threshold,
        xmin=0,
        xmax=10000,
        color="violet",
        ls="--",
        label="bg_threshold_an",
    )

    ax.set_title(f"{pc_signal_channel} | {target_date}")
    ax.set_yscale("log")
    ax.set_ylim(0.01, 3000)
    ax.set_xlim(*range_limits)
    ax.legend(handles=[lan[0], lpc[0], l1, l2], fontsize=10, loc="upper right")

    if savefig:
        plt.savefig(plot_dir / f"gluing_thresholds_{pc_signal_channel}_{target_date}.png")
    plt.close(fig)


def dead_time_finder_by_channel(
    lidar: xr.Dataset,
    an_signal_channel: str,
    pc_signal_channel: str,
    pc_threshold: float,
    an_threshold: float,
    tau_range: list[float] | np.ndarray[Any, np.dtype[np.float64]] = np.arange(2, 10, 0.01),
    pc_binning_range: tuple[float, float] = (0., 50.),
    pc_bin_width: float = 1.0,
    plot_dir: Path = Path.cwd(),
    savefig: bool = False,
    range_limits: tuple[float, float] = (0, 10000),
) -> float:
    """Find the optimal dead time value for a given channel.

    Args:
        lidar (Path): Lidar data file.
        channel_an (str): Analog channel name.
        channel_pc (str): Photon counting channel name.
        pc_threshold (float): Photon counting threshold in MHz.
        an_threshold (float): Analog threshold in mV.
        tau_range (list): Candidate dead time values.
        pc_binning_range (tuple[float, float]): Range of PC signal. Default=(0, 50). In MHz.
        pc_bin_width (float): Width of the bin. Default=1.0. In MHz.
        plot_dir (Path): Path to save the plot. Default=Path.cwd().
        savefig (bool): Save the plot. Default=False.
        range_limits (tuple[float, float]): Range of the plot. Default=(0, 10000).

    Returns:
        float: Optimal dead time value.
    """

    target_date = lidar.time.values[0].astype(str).split("T")[0].replace("-", "")
    signal_an = lidar[f"signal_{an_signal_channel}"]
    signal_pc = lidar[f"signal_{pc_signal_channel}"]

    if isinstance(tau_range, list):
        tau_range = np.array(tau_range)

    plot_gluing_thresholds(
        signal_an=signal_an,
        signal_pc=signal_pc,
        pc_threshold=pc_threshold,
        an_threshold=an_threshold,
        target_date=target_date,
        plot_dir=plot_dir,
        savefig=savefig,
        range_limits=range_limits,
    )

    # get valid an and pc values
    an, pc = get_valid_an_pc_values(
        signal_an=signal_an,
        signal_pc=signal_pc,
        pc_threshold=pc_threshold,
        an_threshold=an_threshold,
    )

    if len(an) < 100 or len(pc) < 100:
        print(f"Empty arrays for {pc_signal_channel} | {target_date}")
        return np.nan

    # apply binning
    median_pc, median_an, std_an = binning(
        signal_an=an,
        signal_pc=pc,
        pc_signal_channel=pc_signal_channel,
        target_date=target_date,
        pc_binning_range=pc_binning_range,
        pc_bin_width=pc_bin_width,
        plot_dir=plot_dir,
        savefig=savefig,
    )
    

    # Retrieve cost function
    J, optimal_tau = cost_function(
        tau_range=tau_range,
        median_an=median_an,
        median_pc=median_pc,
        std_an=std_an,
        pc_signal_channel=pc_signal_channel,
        target_date=target_date,
        savefig=savefig,
        plot_dir=plot_dir,
    )    

    # Plot influence of dead time correction
    plot_influence_of_dead_time_correction(
        tau_range=tau_range,
        optimal_tau=optimal_tau,
        median_an=median_an,
        median_pc=median_pc,
        pc_signal_channel=pc_signal_channel,
        target_date=target_date,
        plot_dir=plot_dir,
        savefig=savefig,
    )

    #Check if optimal tau is out of range
    if optimal_tau == tau_range[0] or optimal_tau == tau_range[-1]:
        print(f'Warning! {datetime} | {pc_signal_channel} : tau out of range')
        return np.nan
    print(f"{datetime} | Optimal tau for {pc_signal_channel} = {optimal_tau} ns")
    
    return optimal_tau


def estimate_daily_dead_time(
    file: Path | str,
    target_pc_channels: list[str] | None = None,
    tau_dir: Path | str = Path.cwd(),
    tau_range: list | np.ndarray[Any, np.dtype[np.float64]] = np.arange(2, 10, 0.01),
    crop_range: tuple = (0, 15000),
    pc_threshold: float = 50,
    an_threshold: float = 0.1,
    pc_binning_range: tuple = (0, 50),
    pc_bin_width: float = 1.,
    range_limits: tuple[float, float] = (0, 10000),
    savefig: bool = False,
    plot_dir: Path = Path.cwd(),
) -> Path:
    """Estimate the optimal dead time for a given list of channels of an specific daily lidar file and save the results in a netcdf file.

    Args:
        file (Path | str): Lidar data file.
        target_pc_channels (list[str]): List of target photon counting channels. Default=None (all channels).
        tau_dir (Path | str | None, optional): Directory to save the netcdf with the optimal dead time values. Defaults to None.
        tau_range (list | np.ndarray[Any, np.dtype[np.float64]], optional): Candidate dead time values. Defaults to np.arange(2, 10, 0.01).
        crop_range (tuple, optional): Range to crop the lidar data. Defaults to (0, 15000).
        pc_threshold (float, optional): Photon counting threshold in MHz. Defaults to 50.
        an_threshold (float, optional): Analog threshold in mV. Defaults to 0.1.
        pc_binning_range (tuple, optional): Range of PC signal. Defaults to (0, 50).
        pc_bin_width (float, optional): Width of the bin. Defaults to 1.0.
        range_limits (tuple[float, float], optional): Range of the plot. Defaults to (0, 10000).
        savefig (bool, optional): Save the plot. Defaults to False.
        plot_dir (Path, optional): Path to save the plot. Defaults to Path.cwd().

    Raises:
        FileNotFoundError: File does not exist.
        TypeError: File is not a netcdf file.
        ValueError: tau_range must be a 1D array.
        ValueError: Error creating {plot_dir}

    Returns:
        Path: Path to the netcdf file with the optimal dead time values.
    """

    # Management file type
    if isinstance(file, str):
        file = Path(file)
    if file.exists() == False:
        raise FileNotFoundError(f"{file} does not exist")
    if file.suffix != ".nc":
        raise TypeError(f"{file} is not a netcdf file")

    # Management tau_dir type
    if isinstance(tau_dir, str):
        tau_dir = Path(tau_dir)
    if tau_dir.exists() == False:
        try:
            tau_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(e)
            raise ValueError(f"Error creating {tau_dir}")

    # Management tau_range type
    if isinstance(tau_range, list):
        tau_range = np.array(tau_range)
    if tau_range.ndim != 1:
        raise ValueError(f"tau_range must be a 1D array")

    # Read
    lidar = preprocess(
        file,
        apply_dt=False,
        save_bg=False,
        save_dc=True,
        apply_bz=True,
        crop_ranges=crop_range,
    )
    target_date = lidar.time.values[1].astype(str).split("T")[0].replace("-", "")
    
    if savefig:
        plot_dir = tau_dir / f"plots_{target_date}"
        if plot_dir.exists() == False:
            try:
                plot_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(e)
                raise ValueError(f"Error creating {plot_dir}")

    # Create tau dictionary
    optimal_taus = {}

    for channel_ in [
        channel_ for channel_ in lidar.channel.values if channel_.endswith("a")
    ]:
        an_signal_channel, pc_signal_channel = channel_, channel_.replace("a", "p")
            
        if pc_signal_channel in lidar.channel:

            if target_pc_channels is not None:                    
                if pc_signal_channel not in target_pc_channels:
                    continue
                           
            optimal_taus[pc_signal_channel] = dead_time_finder_by_channel(
                lidar=lidar,
                an_signal_channel=an_signal_channel,
                pc_signal_channel=pc_signal_channel,
                pc_threshold=pc_threshold,
                an_threshold=an_threshold,
                pc_binning_range=pc_binning_range,
                pc_bin_width=pc_bin_width,
                plot_dir=plot_dir,
                savefig=savefig,
                tau_range=tau_range,
                range_limits=range_limits,
            )

    # Save optimal_taus to a xarray.Dataset 
    tau_dataset = xr.Dataset( { "dead_time": xr.DataArray( list(optimal_taus.values()), coords=[list(optimal_taus.keys())], dims=["channel"], ) } )
    tau_dataset["dead_time"].attrs["units"] = "ns"
    tau_dataset["dead_time"].attrs["long_name"] = "Dead time"
    tau_dataset.attrs["date"] = target_date
    output_file = tau_dir / f"alh_dead-time_{target_date}_2.nc"
    tau_dataset.to_netcdf(output_file)
    return output_file
