#!/usr/bin/env python
from pathlib import Path
import numpy as np

from gfatpy.lidar.preprocessing.lidar_preprocessing import preprocess
from gfatpy.lidar.quality_assurance.dead_time_assesment import (
    dead_time_assesment_by_channel,
)

RS_FL = Path(
    r"./tests/datos/PRODUCTS/alhambra/1a/2023/08/30/alh_1a_Prs_rs_xf_20230830_0315.nc"
)
OUTPUT_DIR = Path(r"./tests/datos/PRODUCTS/alhambra/QA/dead_time_assesment")


def test_assesment_dead_time():

    # Management file type
    if RS_FL.exists() == False:
        raise FileNotFoundError(f"{RS_FL} does not exist")
    if RS_FL.suffix != ".nc":
        raise TypeError(f"{RS_FL} is not a netcdf file")

    # Management output_dir type
    if OUTPUT_DIR.exists() == False:
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(e)
            raise ValueError(f"Error creating {OUTPUT_DIR}")

    datadir = Path(RS_FL)
    data = preprocess(
        datadir,
        apply_dc=True,
        apply_dt=False,
        apply_bg=True,
        apply_bz=True,
        crop_ranges=(0, 15000),
    )  # crop range copied from lidar_dead_time.estimate_deadly_deadtime()

    best_tau, _ = dead_time_assesment_by_channel(
        lidar=data,
        an_signal_channel="532fta",
        pc_signal_channel="532ftp",
        ini_corr_time="2023-08-30T03:15:18",
        end_corr_time="2023-08-30T03:20:24",
        savefig=False,
        debugging=False,
        output_dir=OUTPUT_DIR,
        tau_range=np.arange(2, 10, 0.1),
    )
    data.close()
    #assert best_tau != None
