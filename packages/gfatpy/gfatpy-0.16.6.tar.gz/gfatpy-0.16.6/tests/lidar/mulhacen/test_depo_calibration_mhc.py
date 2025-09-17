from pathlib import Path
from math import isclose
from pdb import set_trace

from gfatpy.lidar.depolarization.calibration import calibration_factor_files
from gfatpy.lidar.depolarization.plot import plot_eta_star_calib


calib_dir = Path(r"./tests/datos/PRODUCTS/mulhacen/QA/depolarization_calibration")
if not calib_dir.exists():
    calib_dir.mkdir(parents=True)


# TODO: Está todo solo para 532
def test_mulhacen_depolarization(linc_files, clean_depo_calibrations):
    #Output files from test conftest.py

    P45_fn = Path(
        r"./tests/datos/PRODUCTS/mulhacen/1a/2022/06/17/mhc_1a_PdpP45_rs_xf_20220617_1115.nc"
    )
    N45_fn = Path(
        r"./tests/datos/PRODUCTS/mulhacen/1a/2022/06/17/mhc_1a_PdpN45_rs_xf_20220617_1115.nc"
    )
    eta_star_calib = calibration_factor_files(P45_fn, N45_fn, calib_dir=calib_dir)
    calib_filepath =  calib_dir / 'mhc_eta-star_20220617_1115.nc'
    eta_star_calib.to_netcdf(calib_filepath)
    output_file = plot_eta_star_calib(eta_star_calib, output_dir=calib_dir)
    
    assert calib_filepath.exists()
    assert isclose(eta_star_calib["eta_star_mean_532xa"].item(), 0.233, rel_tol=0.05)
    assert isclose(eta_star_calib["eta_star_mean_532xp"].item(), 0.4914, rel_tol=0.05)    
    assert output_file is not None
    assert output_file.exists()
    eta_star_calib.close()
