import time


from gfatpy.lidar.preprocessing import preprocess
from gfatpy.utils.optimized import best_slope_fit


def test_best_slope_fit(linc_files):
    lidar = preprocess(
        r"./tests/datos/PRODUCTS/mulhacen/1a/2022/08/08/mhc_1a_Prs_rs_xf_20220808_1131.nc",
        channels=["532xpa", "532xpp"],
    )
    # an_norm = lidar.signal_532xpa.values / lidar.signal
    time0 = time.time()
    best_slope_fit(lidar.signal_532xpa.values, lidar.signal_532xpp.values, 30)
    time1 = time.time()
    assert (time1 - time0) < 11.0  # Should take less than 4 seconds for the whole day