#!/usr/bin/env python
from pathlib import Path
import warnings

import numpy as np
from gfatpy.lidar.quality_assurance.dead_time import estimate_daily_dead_time

RS_FL = (
    r"./tests/datos/PRODUCTS/alhambra/1a/2023/08/30/alh_1a_Prs_rs_xf_20230830_0315.nc"
)
OUTPUT_DIR = Path(r"./tests/datos/PRODUCTS/alhambra/QA/dead_time")


def test_study_dead_time():
    warnings.simplefilter('ignore', RuntimeWarning)
    dead_time_path = estimate_daily_dead_time(
        RS_FL,
        target_pc_channels=["532ftp"],
        tau_range=np.arange(2, 10, 0.1),
        tau_dir=OUTPUT_DIR,
        savefig=True,
        plot_dir=OUTPUT_DIR,
    )
    warnings.resetwarnings()
    assert dead_time_path.exists()
