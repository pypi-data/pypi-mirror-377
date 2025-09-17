#!/usr/bin/env python
from math import isclose
from pdb import set_trace
from matplotlib import pyplot as plt
import numpy as np
from xarray import apply_ufunc

from gfatpy.lidar.plot.quicklook import quicklook_dataset, quicklook_xarray
from gfatpy.lidar.preprocessing import preprocess

RS_FL = (
    r"./tests/datos/PRODUCTS/alhambra/1a/2023/08/30/alh_1a_Prs_rs_xf_20230830_0315.nc"
)


def test_preprocessing_alhambra(linc_files: None):
    channels = ["532fta", "532ftp", "532nta", "532ntp"]
    lidar = preprocess(
        RS_FL,
        channels=channels,
        crop_ranges=(0.0, 15000.0),
        gluing_products=True,
        apply_sm=False,
    )

    variables = lidar.keys()

    assert "signal_532fta" in variables
    assert (np.isnan(lidar["signal_532fta"].values) == 0).all()
    assert isclose(lidar["signal_532fta"].values.mean(), 1.17, abs_tol=0.01)

    fig, _ = quicklook_xarray(
        lidar["signal_532ftg"],
        lidar_name="ALHAMBRA",
        is_rcs=False,
        scale_bounds=(0.0, 5e8),
    )
    fig.savefig("tests/figures/test_preprocessing_alhambra_532ftg.png")
    fig, _ = quicklook_xarray(
        lidar["signal_532fta"],
        lidar_name="ALHAMBRA",
        is_rcs=False,
        scale_bounds=(0.0, 1e8),
    )
    fig.savefig("tests/figures/test_preprocessing_alhambra_532fta.png")
    fig, _ = quicklook_xarray(
        lidar["signal_532ftp"],
        lidar_name="ALHAMBRA",
        is_rcs=False,
        scale_bounds=(0.0, 5e8),
    )
    fig.savefig("tests/figures/test_preprocessing_alhambra_532ftp.png")
    plt.close("all")
    lidar.close()

def test_preprocessing_alhambra_moving(linc_files: None):
    channels = ["532fta"]
    lidar = preprocess(
        RS_FL,
        channels=channels,
        crop_ranges=(0.0, 5000.0),
        gluing_products=False,
        apply_sm=True,
        smooth_mode="moving",
        **{"window_sizes": 20.},
    )

    assert "signal_532fta" in lidar.keys()
    lidar.close()


def test_preprocessing_alhambra_sliding(linc_files: None):
    channels = ["532fta"]
    lidar = preprocess(
        RS_FL,
        channels=channels,
        crop_ranges=(0.0, 5000.0),
        apply_sm=True,
        smooth_mode="sliding",
        **{"sliding_maximum_range": 4000.0,
        "window_range": (10, 300)},
    )

    assert "signal_532fta" in lidar.keys()


def test_preprocessing_alhambra_binning(linc_files: None):
    channels = ["532fta"]
    lidar = preprocess(
        RS_FL,
        channels=channels,
        crop_ranges=(0.0, 5000.0),
        apply_sm=True,
        smooth_mode="binning",  
        **{'binning_average_bin': 15}
    )

    assert "signal_532fta" in lidar.keys()
    lidar.close()
