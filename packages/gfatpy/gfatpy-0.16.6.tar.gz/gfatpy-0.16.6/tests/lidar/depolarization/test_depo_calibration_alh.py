from pathlib import Path
from math import isclose
from pdb import set_trace

from gfatpy.lidar.depolarization.calibration import calibration_factor_files
from gfatpy.lidar.depolarization.plot import plot_eta_star_calib


calib_dir = Path(r"./tests/datos/PRODUCTS/alhambra/QA/depolarization_calibration")
if not calib_dir.exists():
    calib_dir.mkdir(parents=True)    

# TODO: Está todo solo para 532
def test_alhambra_depolarization(linc_files, clean_depo_calibrations):
    # Output files from test conftest.py
    P45_fn = Path(
        r"./tests/datos/PRODUCTS/alhambra/1a/2023/08/30/alh_1a_Pdp+45_rs_xf_20230830_0245.nc"
    )
    N45_fn = Path(
        r"./tests/datos/PRODUCTS/alhambra/1a/2023/08/30/alh_1a_Pdp-45_rs_xf_20230830_0245.nc"
    )

    eta_star_calib = calibration_factor_files(
        P45_fn,
        N45_fn,
        calib_dir=calib_dir,        
        an_calib_limits=(750, 1250.0),
        pc_calib_limits=(750, 1250.0),
    )
    calib_filepath = calib_dir / 'alh_eta-star_20230830_0245.nc'
    eta_star_calib.to_netcdf(calib_filepath)
    output_file = plot_eta_star_calib(
        eta_star_calib, wavelength=532, telescope="n", output_dir=calib_dir
    )

    output_file = plot_eta_star_calib(
        eta_star_calib, wavelength=355, telescope="f", output_dir=calib_dir, **{"signal_ratio_x_lim": (0, 1.5)}
    )

    output_file = plot_eta_star_calib(
        eta_star_calib, wavelength=355, telescope="n", output_dir=calib_dir, **{"calib_factor_x_lim": (0, 1.5)}
    )
    assert calib_filepath.exists()
    assert isclose(eta_star_calib["eta_star_mean_532np"].item(), 0.05774, rel_tol=0.05)
    assert isclose(eta_star_calib["eta_star_mean_355np"].item(), 0.01668, rel_tol=0.05)
    assert isclose(eta_star_calib["eta_star_mean_355fp"].item(), 0.05903, rel_tol=0.05)
    assert isclose(eta_star_calib["eta_star_mean_355fa"].item(), 0.04877, rel_tol=0.05)
    assert isclose(eta_star_calib["eta_star_mean_355na"].item(), 0.01942, rel_tol=0.05)
    assert isclose(eta_star_calib["eta_star_mean_532na"].item(), 0.06466, rel_tol=0.05)

    assert output_file is not None
    assert output_file.exists()
    eta_star_calib.close()
