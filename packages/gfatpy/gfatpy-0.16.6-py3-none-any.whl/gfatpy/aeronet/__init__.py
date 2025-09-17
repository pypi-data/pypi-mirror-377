import matplotlib.pyplot as plt

from gfatpy.aeronet import reader, aeronet4lidar, plot, typing, utils

# Plot volumne size Distribution
SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 18

plt.rc("font", size=MEDIUM_SIZE)  # controls default text sizes
plt.rc("axes", titlesize=MEDIUM_SIZE)  # fontsize of the axes title
plt.rc("axes", labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc("ytick", labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
plt.rc("legend", fontsize=SMALL_SIZE)  # legend fontsize
plt.rc("figure", titlesize=BIGGER_SIZE)  # fontsize of the figure title


# __all__ = [AERONET_INFO, SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE]

__all__ = ["reader", "aeronet4lidar", "plot", "typing", "utils"]

__doc__ = """
This modules allows to manage downloadted AERONET database files from AERONET webpage. 

First, read data and header with `gfatpy.aeronet.reader.reader` and `gfatpy.aeronet.reader.header`, respectively.

"""
