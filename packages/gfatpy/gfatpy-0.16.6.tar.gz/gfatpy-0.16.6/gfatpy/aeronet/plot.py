import os
from typing import Tuple
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt


from gfatpy.aeronet.utils import AERONET_INFO
from gfatpy.utils.plot import color_list

# FIXME: type hinting
def distribution(
    df: pd.DataFrame,
    date_string: list[str] | str,
    type_distribution: str = "volume",
    figure_dir: Path | str | None = None,
    xlims: Tuple[float, float] | str = "auto",
    ylims: Tuple[float, float] | str = "auto",
    dpi: int = 400,
    fig_size: Tuple[float, float] = (8, 6),
) -> Tuple[Figure, plt.Axes, str] | Tuple[list, list, list]:  # type: ignore
    """Distribution() plots all the volume/surface/number size distributions on the date 'date_string'
    
    Args:

        - df (pd.DataFrame): AERONET dataframe loaded with `aeronet.reader`.
        - date_string (str | list[str]): date string or list of date strings in format '%Y-%m-%d'.
        - type_distribution (str [optional]): type of distribution 'volume', 'surface', 'number'
        - figure_dir (str [optional]): file path to save the figure. Directory must exist.
        - xlims (list [optional]): 2D-array with x-axis limits.
        - ylims (list [optional]): 2D-array with y-axis limits.
        - clims (list [optional]): 2D-array with z-axis limits.
        - dpi (int, optional): dots-per-inch figure (higher means larger quality and file size)
    
    Returns:

        - figure handle (matplotlib.figure.Figure): handle of figure | list of figure handles
        - axes handles (matplotlib.axes.Axes): handle of axis | list of axis handles
        - Figure file (str): figure file path | list of figure file paths
    """

    if type(date_string) is str:
        date_string_list = [date_string]
    elif type(date_string) is list:
        date_string_list = date_string
    else:
        raise RuntimeError("Wrong type of `date_string`.")

    if isinstance(figure_dir, str):
        figure_dir = Path(figure_dir)
        if figure_dir.is_dir() is False:
            raise RuntimeError("`figure_dir` not found.")
    elif figure_dir is None:
        figure_dir = Path(".")

    fig_list, axes_list, fig_pathname_list = [], [], []

    df["date"] = [pdate.date() for pdate in df.index.to_pydatetime()]  # type: ignore
    df["time"] = [pdate.time() for pdate in df.index.to_pydatetime()]  # type: ignore

    # min and max column index of the volumne size distribution
    idx_min = df.columns.get_loc("0.050000")
    idx_max = df.columns.get_loc("15.000000")

    # find maximum value
    if ylims == "auto":
        time_condition = np.ones(len(df)) * False
        for date_ in date_string_list:
            time_condition_ = df["date"] == datetime.strptime(date_, "%Y-%m-%d").date()
            time_condition = np.logical_or(time_condition, time_condition_)
        max_dV_dlnr = df.iloc[time_condition.values, np.arange(idx_min, idx_max + 1, 1)].max().max()  # type: ignore # VSD um^3/um^2

        # Found the order of magnitude of the maximum value to round the ylims
        order = np.floor(np.log10(max_dV_dlnr))
        round_max_value: float = np.ceil(max_dV_dlnr / np.power(10, order)) * np.power(
            10, order
        )
        ylims = (0.0, round_max_value)

    for date_ in date_string_list:
        time_condition = df["date"] == datetime.strptime(date_, "%Y-%m-%d").date()
        # Find radius in df header
        radius = np.asarray(AERONET_INFO["radius"])
        df_ = df.loc[time_condition]  # VSD um^3/um^2
        if df_.empty:
            raise RuntimeError(f"No data on {date_}")
        dV_dlnr = df_.iloc[:, np.arange(idx_min, idx_max + 1, 1)]  # VSD um^3/um^2
        if 'Site' in df_.columns:
            site_str = df_["Site"].iloc[0]
        else:
            site_str = df_["AERONET_Site"].iloc[0]
        if len(dV_dlnr) > 0:
            # Figure
            fig, axes = plt.subplots(1, figsize=fig_size)
            # fig.set_figwidth(7)
            # fig.set_figheight(5)
            colors = color_list(len(dV_dlnr))
            for i_ in np.arange(len(dV_dlnr)):
                if type_distribution == "volume":
                    axes.plot(
                        radius,
                        dV_dlnr.iloc[i_, :],
                        label=str(df_["time"].iloc[i_]),
                        c=colors[i_],
                        linewidth=3,
                    )  # type: ignore
                    axes.set_ylabel(r"dV/dlnr, [$\mu$$m^3$/$\mu$$m^2$]")
                elif type_distribution == "surface":
                    Vradius = (4.0 / 3.0) * np.pi * np.power(radius, 3)  # i-bin volume
                    dN_dlnr = dV_dlnr.iloc[i_, :] / Vradius  # NSD #/um^2 # type: ignore
                    Sradius = 4.0 * np.pi * np.power(radius, 2)  # i-bin surface
                    # dSlnr_dlnr = (3 * dV_dlnr.iloc[i_,:] / radius ) #SSD #um^2/um^2
                    dS_dlnr = dN_dlnr * Sradius
                    axes.plot(
                        radius,
                        dS_dlnr,
                        label=df_["time"].iloc[i_],
                        c=colors[i_],
                        linewidth=3,
                    )
                    axes.set_ylabel(r"dS/dlnr, [$\mu$$m^2$/$\mu$$m^2$]")
                elif type_distribution == "number":
                    Vradius = (4.0 / 3.0) * np.pi * np.power(radius, 3)  # i-bin volume
                    dNlnr_dlnr = (
                        dV_dlnr.iloc[i_, :] / Vradius
                    )  # NSD #/um^2 # type: ignore
                    axes.plot(
                        radius,
                        dNlnr_dlnr,
                        label=df_["time"].iloc[i_],
                        c=colors[i_],
                        linewidth=3,
                    )
                    axes.set_ylabel(r"dN/dlnr, [#/$\mu$$m^2$]")
            axes.set_title(f"{site_str} | {date_}")
            axes.set_xlabel(r"radius, [$\mu$m]")
            axes.set_xscale("log")

            if isinstance(xlims, tuple) and len(xlims) > 0:
                axes.set_xlim(*xlims)
            if isinstance(ylims, tuple) and len(ylims) > 0:
                axes.set_ylim(*ylims)
            axes.legend(loc="best")
            axes.grid(axis="y")

            filename = os.path.join(
                figure_dir, f"{type_distribution}_concentration_{date_}.png"
            )
            plt.savefig(filename, dpi=dpi, bbox_inches="tight")
            fig_list.append(fig)
            axes_list.append(axes)
            fig_pathname_list.append(filename)
    if len(date_string_list) == 1:
        fig_output = fig_list[0]
        axes_output = axes_list[0]
        fig_pathname_output = fig_pathname_list[0]
    else:
        fig_output = fig_list
        axes_output = axes_list
        fig_pathname_output = fig_pathname_list

    return fig_output, axes_output, fig_pathname_output  # type: ignore


def aod(
    df: pd.DataFrame,
    header: dict,
    properties2plot: list[str],
    initial_date: datetime,
    final_date: datetime,
    figure_dir: Path | str,
    xlims: Tuple[float, float] | str = "auto",
    ylims: Tuple[float, float] | str = "auto",
    dpi: int = 400,
) -> Tuple[Figure, Axes, str]:
    """aod() plots all the volume/surface/number size distributions on the date 'date_string'
    
    Args:

        - df (pd.DataFrame): AERONET dataframe loaded from reader_all.
        - header (dict): header of AERONET file.
        - initial_date (str): date string in format '%Y-%m-%d'.
        - final_date (str): date string in format '%Y-%m-%d'.
        - figure_dir (str [optional]): file path to save the figure. Directory must exist.
        - xlims (list [optional]): 2D-array with x-axis limits.
        - ylims (list [optional]): 2D-array with y-axis limits.
        - dpi (int, optional): dots-per-inch figure (higher means larger quality and file size)
    
    Returns:
    
        - figure handle (matplotlib.figure.Figure): handle of figure
        - axes handles (matplotlib.axes.Axes): handle of axis
        - Figure file (str): figure file path
    """

    site_str = header["aeronet_station"]

    if figure_dir is None:
        figure_dir = Path(".")
    elif isinstance(figure_dir, str):
        figure_dir = Path(figure_dir)

    if not figure_dir.exists() or not figure_dir.is_dir():
        raise RuntimeError("`figure_dir` not found.")

    if initial_date > final_date:
        raise RuntimeError("`initial_date` should be lower than `final_date`.")

    df["date"] = [pdate.date() for pdate in df.index.to_pydatetime()]  # type: ignore
    df["time"] = [pdate.time() for pdate in df.index.to_pydatetime()]  # type: ignore

    raws = df.index[
        np.logical_and(
            df["date"] >= initial_date.date(), df["date"] <= final_date.date()
        )
    ]
    columns = properties2plot

    fig, axes = plt.subplots(1, 1, figsize=[10, 5])

    colors = np.flip(color_list(len(columns)), axis=0)

    for idx, property in enumerate(properties2plot):
        df.loc[raws, property].plot(
            marker="o", markersize=5, c=colors[idx, :], linewidth=0, ax=axes
        )
    axes.set_ylabel("AOD, [#]")
    if initial_date == final_date:
        date2show = datetime.strftime(initial_date, "%d/%m/%Y")
    else:
        if initial_date.year == final_date.year:
            if initial_date.month == final_date.month:
                date2show = f"{datetime.strftime(initial_date, '%d')}-{datetime.strftime(final_date, '%d/%m/%Y')}"
            else:
                date2show = f"{datetime.strftime(initial_date, '%d/%m')}-{datetime.strftime(final_date, '%d/%m/%Y')}"
        else:
            date2show = f"{datetime.strftime(initial_date, '%d/%m/%Y')}-{datetime.strftime(final_date, '%d/%m/%Y')}"
    axes.set_title(f"{site_str} | {date2show}")

    if (final_date - initial_date).days < 3:
        myFmt = DateFormatter("%H %d-%m-%y")
        axes.set_xlabel(r"Datetime, [hour day-month-year]")
    elif (final_date - initial_date).days > 3 and (final_date - initial_date).days < 7:
        myFmt = DateFormatter("%d-%m-%y")
        axes.set_xlabel(r"Date, [day-month-year]")
    else:
        myFmt = DateFormatter("%m-%y")
        axes.set_xlabel(r"Date, [month-year]")
    axes.xaxis.set_major_formatter(myFmt)

    if isinstance(xlims, tuple) and len(xlims) > 0:
        axes.set_xlim(*xlims)

    if ylims == "auto":
        max_aod = df.loc[raws, properties2plot].max().max()
        ylims = (0.0, np.round(max_aod * 1.1, 2))

    if isinstance(ylims, tuple) and len(ylims) > 0:
        axes.set_ylim(*ylims)

    axes.legend(loc="best")
    axes.grid()

    if initial_date == final_date:
        figure_pathname = os.path.join(
            figure_dir, f"aod_{str(initial_date.date())}.png"
        )
    else:
        figure_pathname = os.path.join(
            figure_dir, f"aod_{str(initial_date.date())}-{str(final_date.date())}.png"
        )

    plt.savefig(figure_pathname, dpi=dpi, bbox_inches="tight")
    return fig, axes, figure_pathname


# def plot_single_scatter(
#     df,
#     cf_info,
#     wavelength=440,
#     min_radius=50,
#     colorbar_property="Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD",
#     filter_name="",
#     xlims=[],
#     ylims=[],
#     clims=[],
# ):
#     """
#     apc_scatter makes scatter plots of up to three dataframes readed with function reader_all.
#     Input:
#     wavelength: AOD wavelength in nm (e.g., 440)
#     minimum radius: minimum radius to integrate the NSD in nm (e.g., 50)
#     colorbar_property: variable in dataframe for colorbar (e.g., 'Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD' [default])
#     filter_name: Allows to indicate in the figure title in the data are filtered.
#     xlims: set x limits
#     ylims: set y limits
#     clims: set colorbar limits
#     """

#     # Define colorbar label
#     colorbar_label_dict = {
#         "Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD": "AE[440-870nm]",
#         "Sphericity_Factor(%)": "Sphericity Factor(%)",
#         "Depolarization_Ratio[440nm]": "Depol. ratio[440nm]",
#         "Depolarization_Ratio[675nm]": "Depol. ratio[675nm]",
#         "FMF[675nm]": "FMF][675nm]",
#         "Lidar_Ratio[440nm]": "Lidar ratio[440nm]",
#         "Single_Scattering_Albedo[440nm]": "SSA[440nm]",
#     }

#     if not (colorbar_property in colorbar_label_dict.keys()):
#         colorbar_label_dict[colorbar_property] = colorbar_property

#     # Define y label
#     lnAOD = "lnAOD%d" % wavelength
#     lnN = "ln_n%d" % min_radius
#     ylabel_string = "$ln(N_{%d})$" % min_radius
#     xlabel_string = "$ln(AOD[%d nm])$" % wavelength

#     # Figure
#     fig, axes = plt.subplots(1, 1)
#     fig.set_figwidth(10)
#     fig.set_figheight(6)

#     # Scatter
#     ax_mappable = axes.scatter(df[lnAOD], df[lnN], c=df[colorbar_property])

#     # Linear fit
#     exponent, exponent_error, intercept, intercept_error, R2 = cf_info
#     m, error_m, n, error_n, R2 = (
#         exponent,
#         exponent_error,
#         np.log(intercept),
#         intercept_error / intercept,
#         R2,
#     )
#     plt.plot(
#         df[lnAOD],
#         m * df[lnAOD] + n,
#         "r",
#         label="y=(%.4f $\pm$ %.4f)x + (%.4f $\pm$ %.4f) [R=%.2f]"
#         % (m, error_m, n, error_n, np.sqrt(R2)),
#     )

#     # Axes format
#     if len(filter_name) > 0:
#         axes.set_title(
#             "%s | Filter: %s | data[#]: %d " % (df["Site"][0], filter_name, len(df))
#         )
#     else:
#         axes.set_title("%s | data[#]: %d " % (df["Site"][0], len(df)))
#     axes.legend()
#     axes.set_xlabel(xlabel_string)
#     axes.set_ylabel(ylabel_string)
#     if len(xlims) > 0:
#         ax_mappable.axes.set_xlim(xlims)
#     if len(ylims) > 0:
#         ax_mappable.axes.set_ylim(ylims)
#     if len(clims) > 0:
#         ax_mappable.set_clim(clims)
#     fig.colorbar(ax_mappable, label=colorbar_label_dict[colorbar_property], ax=axes)
#     fig.tight_layout()
#     return fig, axes


# def plot_scatter(
#     df_tuple,
#     x="lnAOD440",
#     y="ln_n50",
#     colorbar_property="Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD",
#     filter_name="",
#     xlims=[],
#     ylims=[],
#     clims=[],
# ):
#     """
#     apc_scatter makes scatter plots of up to three dataframes readed with function reader_all.
#     Input:
#     x: variable in dataframe (e.g., 'Depolarization_Ratio[440nm]')
#     y: variable in dataframe (e.g., 'Lidar_Ratio[440nm]')
#     colorbar_property: variable in dataframe for colorbar (e.g., 'Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD' [default])
#     filter_name: Allows to indicate in the figure title in the data are filtered.
#     xlims: set x limits
#     ylims: set y limits
#     clims: set colorbar limits
#     """
#     SMALL_SIZE = 12
#     MEDIUM_SIZE = 14
#     BIGGER_SIZE = 18

#     plt.rc("font", size=MEDIUM_SIZE)  # controls default text sizes
#     plt.rc("axes", titlesize=MEDIUM_SIZE)  # fontsize of the axes title
#     plt.rc("axes", labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
#     plt.rc("xtick", labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
#     plt.rc("ytick", labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
#     plt.rc("legend", fontsize=MEDIUM_SIZE)  # legend fontsize
#     plt.rc("figure", titlesize=BIGGER_SIZE)  # fontsize of the figure title
#     # Define colorbar label
#     colorbar_label_dict = {
#         "Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD": "AE[440-870nm]",
#         "Sphericity_Factor(%)": "Sphericity Factor(%)",
#         "Depolarization_Ratio[440nm]": "Depol. ratio[440nm]",
#         "Depolarization_Ratio[675nm]": "Depol. ratio[675nm]",
#         "FMF[675nm]": "FMF][675nm]",
#         "Lidar_Ratio[440nm]": "Lidar ratio[440nm]",
#         "Single_Scattering_Albedo[440nm]": "SSA[440nm]",
#     }

#     if not (colorbar_property in colorbar_label_dict.keys()):
#         colorbar_label_dict[colorbar_property] = colorbar_property

#     # Define y label
#     ylabel_dic = {
#         "lnN_fine": "$ln(N_{fine})$",
#         "lnN_coarse": "$ln(N_{coarse}$)",
#         "lnN": "$ln(N)$",
#     }
#     if not y in ylabel_dic.keys():
#         ylabel_dic[y] = y

#     xlabel_dic = {"lnAOD440": "$ln(AOD[440nm])$"}
#     if not x in xlabel_dic.keys():
#         xlabel_dic[x] = x

#     # Figure
#     fig, axes = plt.subplots(1, len(df_tuple))
#     fig.set_figwidth(15)
#     fig.set_figheight(3)

#     for axes_idx in np.arange(len(df_tuple)):
#         df = df_tuple[axes_idx]
#         # Scatter
#         ax_mappable = axes[axes_idx].scatter(
#             df[x], df[y], c=df[colorbar_property], cmap="YlOrRd"
#         )

#         # Linear fit
#         m, error_m, n, error_n, R2 = linrest(df[x], df[y])
#         axes[axes_idx].plot(
#             df[x],
#             m * df[x] + n,
#             "r",
#             lw=3,
#             label="AERONET | R=%.2f | m=%.3f$\pm$%.3f | n=%.3f$\pm$%.3f"
#             % (np.sqrt(R2), m, error_m, n, error_n),
#         )
#         # Axes format
#         if len(filter_name) > 0:
#             # axes[axes_idx].set_title('%s | data[#]: %d | %s\n R=%.2f | m=%.3f$\pm$%.3f | n=%.3f$\pm$%.3f' % (filter_name, len(df), df['Site'][0], np.sqrt(R2), m, error_m, n, error_n))
#             axes[axes_idx].set_title(
#                 "%s | data[#]: %d | %s" % (filter_name, len(df), df["Site"][0])
#             )
#         else:
#             axes[axes_idx].set_title("%s" % (df["Site"][0]))
#             # axes[axes_idx].set_title('%s\n R=%.2f | m=%.2f$\pm$%.2f | n=%.2f$\pm$%.2f' % (df['Site'][0], np.sqrt(R2), m, error_m, n, error_n))
#             # axes[axes_idx].set_title('%s\n $R$=%.2f |alpha=%.2f | C=%.2f' % (df['Site'][0], R, m, np.exp(n)))
#         axes[axes_idx].set_facecolor("gainsboro")
#         axes[axes_idx].set_xlabel(xlabel_dic[x])
#         axes[axes_idx].legend()
#         if axes_idx == 0:
#             axes[axes_idx].set_ylabel(ylabel_dic[y])

#         if len(clims) > 1:
#             ax_mappable.set_clim(clims)
#         else:
#             if axes_idx == 0:
#                 clims = ax_mappable.get_clim()
#         if len(xlims) > 0:
#             ax_mappable.axes.set_xlim(xlims)
#         if len(ylims) > 0:
#             ax_mappable.axes.set_ylim(ylims)
#         fig.colorbar(
#             ax_mappable, label=colorbar_label_dict[colorbar_property], ax=axes[axes_idx]
#         )
#     return fig, axes
