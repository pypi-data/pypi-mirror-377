from pathlib import Path
from typing import Tuple
import numpy as np

import xarray as xr
from datetime import datetime
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from gfatpy.lidar.utils.file_manager import channel2info
from gfatpy.lidar.utils.utils import LIDAR_INFO


def plot_rayleigh_fit(
    filepath: Path | list[Path],
    output_dir: Path | str | None = None,
    save_fig: bool = False,
    range_limits: tuple[float, float] | None = None,
) -> tuple[
    list[Figure | None], list[Figure | None]
]:  
    """It plots Rayleigh Fit data.

    Args:

        - filepath (Path | list[Path]): Rayleigh Fit file path.
        - output_dir (Path | str | None, optional): Output directory. Defaults to None (current working directory).
        - save_fig (bool, optional): Save figure. Defaults to False.
        - range_limits (tuple[float, float] | None, optional): Range limits. Defaults to None (all range).

    Raises:

        - ValueError: Filepath must be Path or list[Path].
        - FileNotFoundError: File not found.
        - NotADirectoryError: Directory not found.

    Returns:

        - tuple[ list[Figure | None], list[Figure | None] ]: Figures and axes.
    """    
    # FIXME: warning message due to more than 20 figures open. Consider remove output figure/axes handles.

    if isinstance(filepath, Path):
        files = [filepath]
    elif isinstance(filepath, list):
        files = filepath
    else:
        raise ValueError("filepath must be Path or list[Path]")

    figures, axes = [], []
    for filepath in files:
        if not filepath.exists():
            raise FileNotFoundError(f"{filepath} not found.")

        # read data
        dataset = xr.open_dataset(filepath)

        # info
        lidar_name: str = dataset.attrs["lidar_name"]
        channel = dataset.attrs["channel"]
        wavelength = (channel2info(channel))[0]
        z_min, z_max = dataset.attrs["rayleigh_height_limits"]
        initial_date = datetime.strptime(
            dataset.attrs["datetime_ini"], dataset.attrs["datetime_format"]
        )
        final_date = datetime.strptime(
            dataset.attrs["datetime_end"], dataset.attrs["datetime_format"]
        )
        str(initial_date.year)

        date4filename = datetime.strftime(initial_date, "%Y%m%d-%H%M")
        if initial_date.date() == final_date.date():
            date_str = datetime.strftime(initial_date, "%Y-%m-%d")
            initial_time = datetime.strftime(initial_date, "%H:%M")
            final_time = datetime.strftime(final_date, "%H:%M")
            show_datetime_as = f"{date_str} from {initial_time} to {final_time} UTC"
        else:
            initial_date = datetime.strftime(initial_date, "%H:%M %Y-%m-%d")
            final_date = datetime.strftime(final_date, "%H:%M %Y-%m-%d")
            show_datetime_as = f"{initial_date} to {initial_date}"

        """ FIGURE """
        fig_title = f"{lidar_name} Rayleigh fit - channel {channel} | {show_datetime_as} | Reference height: {z_min}-{z_max} km"
        fig_y_label = "Normalized attenuated backscatter, #"
        if range_limits is not None:
            x_lim = range_limits
        else:
            x_lim = (dataset.range.min(), dataset.range.max())
        y_lim = (1e-2, 50)

        raw_colors = {
            355: mcolors.CSS4_COLORS["aliceblue"],  # type: ignore
            532: mcolors.CSS4_COLORS["honeydew"],  # type: ignore
            530: mcolors.CSS4_COLORS["honeydew"],  # type: ignore
            1064: mcolors.CSS4_COLORS["seashell"],  # type: ignore
        }

        smooth_colors = {355: "b", 530: "g", 532: "g", 1064: "r"}
        if wavelength in smooth_colors:
            raw_color = raw_colors[wavelength]
            smooth_color = smooth_colors[wavelength]
        else:
            raw_color = mcolors.CSS4_COLORS["aliceblue"]  # type: ignore
            smooth_color = "b"

        fig = plt.figure(figsize=(15, 6))
        ax = fig.add_subplot(111)
        ax.grid(which="both", **{"lw": 1})
        dataset["RCS_norm"].plot(ax=ax, x="range", label="raw", color=raw_color)  # type: ignore
        dataset["BCS_norm"].plot(
            ax=ax,
            x="range",
            label=r"$\beta_{att}^{mol}$",
            color="k",
            ls="dashed",
            linewidth=2,
        )  # type: ignore
        dataset["RCS_smooth_norm"].plot(
            ax=ax, x="range", label="smoothed", color=smooth_color
        )  # type: ignore
        ax.set_title(fig_title, fontsize="medium")
        ax.xaxis.get_label().set_fontsize("medium")
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax.set_ylabel(fig_y_label, fontsize="medium")
        ax.set_xlabel("Range, km", fontsize="medium")
        ax.set_xlim(x_lim)
        ax.set_ylim(*y_lim)
        ax.set_yscale("log")
        leg = ax.legend(fontsize="medium")
        frame = leg.get_frame()
        frame.set_edgecolor("black")
        frame.set_facecolor("silver")

        if save_fig:
            # create output_dir
            if output_dir is None:
                output_dir = Path.cwd()
            elif isinstance(output_dir, str):
                output_dir = Path(output_dir)

            if not output_dir.exists() or not output_dir.is_dir():
                raise NotADirectoryError(f"{output_dir} not found.")

            # Create file path
            output_dir.mkdir(parents=True, exist_ok=True)
            fig_fn = output_dir / f"{lidar_name}_RF_{channel}_{date4filename}.png"

            plt.tight_layout()
            plt.savefig(fig_fn, dpi=300, bbox_inches="tight")
        else:
            fig, ax = None, None
        figures.append(fig)
        axes.append(ax)
        plt.close()
    return figures, axes


def plot_telecover_channel(
    rf_ds: xr.Dataset,
    normalization_range: Tuple[float, float] = (1500, 1750),
    rcs_limits: Tuple[float, float] = (0, 6e7),
    norm_rcs_limits: Tuple[float, float] = (0, 20),
    x_limits: Tuple[float, float] = (0, 10),
    output_dir: Path | str | None = None,
    save_fig: bool = False,
) -> Tuple[Figure | None, plt.Axes | None]:
    """Plot telecover for a given channel.

    Args:
        rf_ds (xr.Dataset): Rayleigh Fit dataset.
        normalization_range (Tuple[float, float], optional): _description_. Defaults to (1500, 1750).
        rcs_limits (Tuple[float, float], optional): _description_. Defaults to (0, 6e7).
        norm_rcs_limits (Tuple[float, float], optional): _description_. Defaults to (0, 20).
        x_limits (Tuple[float, float], optional): _description_. Defaults to (0, 10).
        output_dir (Path | str | None, optional): _description_. Defaults to None.
        save_fig (bool, optional): _description_. Defaults to False.

    Raises:
        NotADirectoryError: _description_
        RuntimeError: _description_

    Returns:
        Tuple[Figure | None, plt.Axes | None]: _description_
    """    
    # FIGURE
    # TODO: TO INFO YAML PLOT
    # ydict_rcs = {
    #     "355xta": (0, 2e6),
    #     "355xtp": (0, 3e7),
    #     "532xpa": (0, 3e6),
    #     "532xpp": (0, 6e7),
    #     "532xcp": (0, 2e7),
    #     "532xca": (0, 1e6),
    #     "1064xta": (0, 7e6),
    #     "353xtp": (0, 3e6),
    #     "530xtp": (0, 5e7),
    #     "408xtp": (0, 2e8),
    # }
    # ydict_norm_rcs = {
    #     "355xta": (0, 10),
    #     "355xtp": (0, 10),
    #     "532xpa": (0, 8),
    #     "532xpp": (0, 5),
    #     "532xcp": (0, 4),
    #     "532xca": (0, 10),
    #     "1064xta": (0, 20),
    #     "353xtp": (0, 5),
    #     "530xtp": (0, 2),
    #     "408xtp": (0, 5),
    # }

    if output_dir is None:
        output_dir = Path.cwd()
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    if not output_dir.exists() or not output_dir.is_dir():
        raise NotADirectoryError(f"{output_dir} not found.")

    lidar_name = LIDAR_INFO["metadata"]["nick2name"]
    channel = rf_ds.channel_code

    colorbar = cm.get_cmap("jet", len(rf_ds.sectors))
    colors = colorbar(np.linspace(0, 1, len(rf_ds.sectors)))
    fig = plt.figure(figsize=(15, 10))
    fig_title = "%s telecover - channel %s | %s | Reference height: %3.1f-%3.1f km" % (
        channel,
        datetime.strftime(rf_ds.datetime_ini, "%d.%m.%Y, %H:%MUTC"),
        normalization_range[0] / 1000.0,
        normalization_range[1] / 1000.0,
    )
    # MEAN
    sectors = [sector_ for sector_ in rf_ds.sectors if sector_.find("2") == -1]
    sum_rcs = np.zeros(rf_ds.range.size)
    for sector_ in sectors:
        rcs = rf_ds[sector_]
        try:
            sum_rcs += rcs
        except:
            sum_rcs += rcs.compute()
    mean_rcs = sum_rcs / len(sectors)
    mean_rcs = xr.DataArray((mean_rcs), coords=[rf_ds.range], dims=["range"])
    mean_rcs.name = "M"

    # Normalized
    for sector_ in rf_ds.sectors:
        rf_ds[f"n{sector_}"] = (
            rf_ds[sector_]
            / rf_ds[sector_].sel(range=slice(*normalization_range)).mean()
        )
    norm_mean_rcs = mean_rcs / mean_rcs.sel(range=slice(*normalization_range)).mean()
    norm_mean_rcs.name = "nM"

    # RAW RCS
    ax = fig.add_subplot(311)
    fig_y_label = "RCS, a.u."
    for iter_ in zip(rf_ds.sectors, colors):
        sector_ = iter_[0]
        color_ = iter_[1]
        rf_ds[sector_].plot(ax=ax, x="range", linewidth=2, label=sector_, color=color_)
    mean_rcs.plot(ax=ax, x="range", linewidth=2, label="M", color="k")  # type: ignore
    ax.set_title(fig_title, fontsize="x-large", verticalalignment="baseline")
    ax.set_ylim(*rcs_limits)
    plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 1))
    ax.set_ylabel(fig_y_label, fontsize="large")
    plt.legend(loc=1, fontsize="large")

    # Normalized RCS
    ax = fig.add_subplot(312)
    fig_y_label = "Normalized RCS, a.u."
    for iter_ in zip(rf_ds.sectors, colors):
        sector_ = iter_[0]
        color_ = iter_[1]
        rf_ds[f"n{sector_}"].plot(
            ax=ax, x="range", linewidth=2, label=sector_, color=color_
        )  # type: ignore
    norm_mean_rcs.plot(ax=ax, x="range", linewidth=2, label="nM", color="k")  # type: ignore
    plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 1))
    ax.set_ylim(*norm_rcs_limits)
    ax.set_ylabel(fig_y_label, fontsize="large")
    plt.legend(loc=1, fontsize="large")

    # Diference
    ax = fig.add_subplot(313)
    fig_y_label = "normalized RCS\nrelative difference, %"

    for iter_ in zip(rf_ds.sectors, colors):
        sector_ = iter_[0]
        color_ = iter_[1]
        rf_ds["diff_%s" % sector_] = (
            100 * (rf_ds[f"n{sector_}"] - norm_mean_rcs) / norm_mean_rcs
        )
        rf_ds[f"diff_{sector_}"].plot(
            ax=ax, x="range", linewidth=2, label=sector_, color=color_
        )  # type: ignore
    ax.xaxis.get_label().set_fontsize("large")
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(125))
    ax.set_ylabel(fig_y_label, fontsize="large")
    ax.set_ylim(-100, 100)
    plt.legend(loc=1, fontsize="large")

    for ax in fig.get_axes():
        ax.tick_params(axis="both", labelsize=14)
        ax.set_xlim(*x_limits)
        ax.grid()
        ax.label_outer()

    if save_fig:
        datestr = datetime.strftime(rf_ds.datetime_ini, "%Y%m%d_%H%M")
        figure_file = output_dir / f"telecover_{lidar_name}_{channel}_{datestr}.png"
        plt.savefig(figure_file, dpi=200, bbox_inches="tight")
        if not figure_file.exists():
            raise RuntimeError(f"Figure file {figure_file} not saved")
    return fig, ax
