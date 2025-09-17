import os

import numpy as np
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt
from loguru import logger


def plotQuicklook(data: xr.Dataset, plt_conf: xr.Dataset, saveImageFlag: bool = False):

    logger.warning("to be deprecated. Use cloudnetpy instead")
    """
    Inputs:
    - data: from categorice_reader()
    - plt_conf: plot configuration dictionary as follows:
        plt_conf =  {
            'mainpath': "Y:\\datos\\CLOUDNET\\juelich\\quicklooks",
            'coeff': COEFF,
            'gapsize': HOLE_SIZE,
            'dpi': dpi,
            'fig_size': (16,5),
            'font_size': 16,
            'y_min': 0,
            'y_max': range_limit,
            'rcs_error_threshold':1.0, }
    - saveImageFlag [Boolean]: to save png-figure or print in command screen.
    """
    var2plot = {0: "dBZe", 1: "v", 2: "beta"}  # , 2: 'sigma' , 3: 'sigma', 4: 'kurt'
    # Dictionary for the vmax and vmin of the plot
    Vmin = {0: -55, 1: -1.5, 2: 0}  # , 2: 0 , 3: -3, 4: -3
    Vmax = {0: -20, 1: 1.5, 2: 10}  # , 2: 5 , 3: 3, 4: 3
    Vn = {0: 16, 1: 7, 2: 10}
    scale = {0: 1, 1: 1, 2: 1e6}
    titleStr = {
        0: "Reflectivity",
        1: "Vertical mean velocity",
        2: "Backscatter coeff.",
    }  # , 2: 'spectral width'
    cblabel = {
        0: "$Z_e, dBZe$",
        1: "$V_m, m/s$",
        2: r"$\beta$, $Mm^-1$",
    }  # , 2: 'spectral width'
    datestr = data["raw_time"][0].strftime("%Y%m%d")
    for idx in var2plot.keys():
        _var = var2plot[idx]
        # print(idx)
        print(_var)
        _fig, _axes = plt.subplots(nrows=1, figsize=(15, 6))
        _axes.set_facecolor("whitesmoke")
        cmap = mpl.cm.jet
        bounds = np.linspace(Vmin[idx], Vmax[idx], Vn[idx])
        #        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        range_km = data["height"] / 1000.0
        q = _axes.pcolormesh(
            data["raw_time"],
            range_km,
            scale[idx] * data[_var].T,
            cmap=cmap,
            vmin=Vmin[idx],
            vmax=Vmax[idx],
        )
        q.cmap.set_over("white")
        q.cmap.set_under("darkblue")
        cb = plt.colorbar(q, ax=_axes, ticks=bounds, extend="max")
        cb.set_label(cblabel[idx])
        _axes.set_xlabel("Time, UTC")
        _axes.set_ylabel("Height, Km asl")
        _axes.set_title("%s on  %s" % (titleStr[idx], datestr))
        xmin = datetime.strptime(datestr, "%Y%m%d")
        xmax = xmin + timedelta(days=1)
        _axes.set_xlim(xmin, xmax)
        _axes.set_ylim(0, 2)
        if saveImageFlag:
            figstr = "%s_%s_%s.png" % ("cloudnet", var2plot[idx], datestr)
            finalpath = os.path.join(plt_conf["mainpath"], _var, figstr)
            print("Saving %s" % finalpath)
            final_dir_path = os.path.split(finalpath)[0]
            if not os.path.exists(final_dir_path):
                os.makedirs(final_dir_path)
            plt.savefig(finalpath, dpi=100, bbox_inches="tight")
            if os.path.exists(finalpath):
                print("Saving %s...DONE!" % finalpath)
            else:
                print("Saving %s... error!" % finalpath)
            plt.close(_fig)
        else:
            plt.show()


def plotLWP(data, mainpath, saveImageFlag):
    """
    Inputs:
    - data: from categorice_reader()
    - mainpath: "Y:\\datos\\CLOUDNET\\juelich\\quicklooks",
    - saveImageFlag [Boolean]: to save png-figure or print in command screen.
    """
    logger.warning("to be deprecated. Use cloudnetpy instead")
    datestr = data["raw_time"][0].strftime("%Y%m%d")
    fig, axes = plt.subplots(nrows=1, figsize=(15, 6))
    axes.set_facecolor("whitesmoke")
    plt.plot(data["raw_time"], data["lwp"])
    axes.set_xlabel("Time, UTC")
    axes.set_ylabel("LWP, $g/m^2$")
    axes.set_title("LWP on  %s" % datestr)
    xmin = datetime.strptime(datestr, "%Y%m%d")
    xmax = xmin + timedelta(days=1)
    axes.set_xlim(xmin, xmax)
    if saveImageFlag:
        figstr = "%s_%s_%s.png" % ("cloudnet", "lwp", datestr)
        finalpath = os.path.join(mainpath, "LWP", figstr)
        print("Saving %s" % finalpath)
        final_dir_path = os.path.split(finalpath)[0]
        if not os.path.exists(final_dir_path):
            os.makedirs(final_dir_path)
        plt.savefig(finalpath, dpi=100, bbox_inches="tight")
        if os.path.exists(finalpath):
            print("Saving %s...DONE!" % finalpath)
        else:
            print("Saving %s... error!" % finalpath)
        plt.close(fig)
    else:
        plt.show()
