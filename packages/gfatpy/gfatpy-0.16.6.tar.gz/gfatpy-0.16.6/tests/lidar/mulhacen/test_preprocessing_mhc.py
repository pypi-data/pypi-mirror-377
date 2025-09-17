#!/usr/bin/env python
import numpy as np

from gfatpy.lidar.preprocessing import preprocess

RS_FL = r"./tests/datos/PRODUCTS/mulhacen/1a/2022/08/08/mhc_1a_Prs_rs_xf_20220808_1131.nc"
DC_FL = r"./tests/datos/PRODUCTS/mulhacen/1a/2022/08/08/mhc_1a_Pdc_rs_xf_20220808_1131.nc"

def test_preprocessing_mulhacen_532(linc_files):
    channels = ["532xpa", "532xpp", "532xsa", "532xsp"]
    lidar = preprocess(
        RS_FL, channels=channels, crop_ranges=(0.0, 15000.0), gluing_products=False
    )
    variables = lidar.keys()
    assert "signal_532xpa" in variables
    assert "signal_532xpp" in variables
    assert "signal_532xsa" in variables
    assert "signal_532xsp" in variables
    assert "signal_1064xta" not in variables
    assert (np.isnan(lidar["signal_532xpa"].values) == 0).all()
    assert (lidar["signal_532xpa"].values.mean() > 0.4) & (
        lidar["signal_532xpa"].values.mean() < 1.0
    )
    lidar.close()


# def test_preprocessing_mulhacen_532xta(linc_files):
#     channels = ["532xta", "532xtp"]
#     lidar = preprocess(RS_FL, dc_fl=DC_FL, channels=channels)
#     variables = lidar.keys()
#     assert "signal_532xta" in variables
#     assert "signal_532xtp" in variables
#     # assert np.round(lidar["signal_532xta"].mean().mean().values, 2) == 0.15
#     # assert np.round(lidar["signal_532xtp"].mean().mean().values, 2) == 7.32
