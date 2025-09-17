#!/usr/bin/env python
from pdb import set_trace
from gfatpy.lidar.reader import reader_xarray
from gfatpy.lidar.utils.utils import LIDAR_INFO


def test_reader_xarray(linc_files):
    filelist = r"./tests/datos/PRODUCTS/mulhacen/1a/2022/08/08/*Prs*.nc"
    date_ini = "2022-08-08"
    channels = ["532xta"]
    lidar = reader_xarray(filelist, date_ini=date_ini, channels=channels)
    lidar_name = lidar.attrs["system"].lower()    
    assert lidar_name in LIDAR_INFO["lidars"]
    lidar.close()
