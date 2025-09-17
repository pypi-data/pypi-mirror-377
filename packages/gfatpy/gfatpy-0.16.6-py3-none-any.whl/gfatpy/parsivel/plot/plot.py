#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
from typing import Any
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime
import xarray as xr

from gfatpy.parsivel.plot.utils import DSD_PLOT_INFO
from gfatpy.parsivel.utils import DSD_INFO


def spectrumPlot(
    station: str,
    droplet_spectrum: xr.DataArray,
    date_limits: tuple[datetime, datetime],
    diameter_limits: tuple[float, float] | None = None,
    velocity_limits: tuple[float, float] | None = None,
    output_path: Path | None = None,
    **kwargs,
) -> Path:
    """Generates a plot of the disdrometer spectrum.

    Args:

        - station (str): Station name.
        - droplet_spectrum (list[np.float64]): List of disdrometer spectra.        
        - diameter_limits (tuple[float, float], optional): Diameter axis limits. Defaults to (0, 6.1).
        - velocity_limits (tuple[float, float], optional): Velocity axis limits. Defaults to (0, 12).
        - output_path (Path | None, optional): Directory to save the plot. Defaults to None (current working directory).

    Returns:

        - Path: File path of the generated plot.
    """    

    # Tamaño de la fuente de las etiquetas
    mpl.rc("font", **kwargs)

    # Tamaño de la figura

    # Colormap
    # bounds = DSD_PLOT_INFO['bounds']
    # colors = DSD_PLOT_INFO['colors']
    
    # cm = mpl.colors.ListedColormap(colors)
    # norm = mpl.colors.BoundaryNorm(bounds, cm.N)

    # Mallado del colormap
    # dclasses = np.asarray(DSD_INFO['diameters'],dtype=np.float32)
    # vclasses = np.asarray(DSD_INFO['velocities'],dtype=np.float32)    
    dclasses = droplet_spectrum['dclasses'].values
    vclasses = droplet_spectrum['vclasses'].values

    if diameter_limits is None:
        diameter_limits = (dclasses.min().item(), dclasses.max().item())
    if velocity_limits is None: 
        velocity_limits = (vclasses.min().item(), vclasses.max().item())

    fig, axes = plt.subplots(nrows=1, figsize=(18, 10))
    cmp = droplet_spectrum.plot(x="dclasses", ax=axes, shading="auto") #cmap=cm, norm=norm,
    
    # Etiquetas y rango de visualización
    axes.set_xlabel("Rain-droplet diameter, $m$$m$")
    axes.set_ylabel("Fall velocity, $m/s$")
    breakpoint()
    axes.set_xlim(*diameter_limits)
    axes.set_ylim(*velocity_limits)

    # Dibuja color map    
    cmp.colorbar.set_label("Rain-droplet number concentration, $\#/m^3$")

    # Dibuja el mallado del colormap
    xi, yi = np.meshgrid(dclasses, vclasses)
    axes.plot(xi, yi, "k-", alpha=0.3)  # Dibuja la lineas verticales del mallado
    axes.plot(xi.T, yi.T, "k-", alpha=0.3)  # Dibuja la lineas horizontales del mallado

    d1 = date_limits[0]
    d2 = date_limits[1]
    if d1.date == d2.date:
        period_str = f"{d1.hour} - {d2.hour}"
        date_to_filename = f"{d1.strftime('%y%m%d')}_{d1.strftime('%H%M%S')}-{d2.strftime('%H%M%S')}"
    else: 
        period_str = f"{d1.strftime('%y-%m-%d %H:%M:%S')} - {d2.strftime('%y-%m-%d %H:%M:%S')}"
        date_to_filename = f"{d1.strftime('%y%m%dT%H%M%S')}-{d2.strftime('%y%m%dT%H%M%S')}"

    axes.set_title(f"Disdrometer DSD in {station} | Period: {period_str}")
    
    # Dibuja la linea teórica
    plt.plot(np.asarray(DSD_INFO['gunnKinzer']['diameters']), np.asarray(DSD_INFO['gunnKinzer']['velocities']), "gray")

    if output_path is None:
        output_path = Path.cwd() / f"dsd_spectrum_{date_to_filename}.png"
    
    breakpoint()
    fig.savefig(output_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return output_path
