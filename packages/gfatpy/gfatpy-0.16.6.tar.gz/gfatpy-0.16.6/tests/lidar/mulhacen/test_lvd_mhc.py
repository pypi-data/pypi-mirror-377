from math import isclose
from pathlib import Path

from matplotlib import pyplot as plt

from gfatpy.lidar.preprocessing.lidar_preprocessing import preprocess
from gfatpy.lidar.depolarization.retrieval import add_depolarization_products
from gfatpy.lidar.depolarization.calibration import eta_star_reader

RS_FL = Path(r"./tests/datos/PRODUCTS/mulhacen/1a/2022/08/08/mhc_1a_Prs_rs_xf_20220808_1131.nc")
ETA_DIR = Path(r"./tests/datos/PRODUCTS/mulhacen/QA/depolarization_calibration/")
ETA_FL = Path(r"./tests/datos/PRODUCTS/mulhacen/QA/depolarization_calibration/mhc_eta-star_20220617_1115.nc")

def test_reader_depolarization_calibration_532n():
    eta_dataset = eta_star_reader(ETA_FL)
    assert isclose(
        eta_dataset["eta_star_mean_532xa"].values.item(), 0.233, rel_tol=1e-2
    )
    eta_dataset.close()


def test_depolarization(linc_files):
    lidar = preprocess(
        RS_FL,
        channels=[
            "532xpa",
            "532xpp",
            "532xsa",
            "532xsp",
        ],
        crop_ranges=(0.0, 15000.0),
    )
    dataset = add_depolarization_products(lidar, depo_calib_dir=ETA_DIR)
    lidar.close()

    # plot linear volume depolarization ratio
    

    fig_, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 5), sharex=True)
    dataset["linear_volume_depolarization_ratio_532xa"].plot(y="range", ax=ax, vmin=0, vmax=0.5, cmap="jet")  # type: ignore

    save_dir = Path(r"./tests/datos/PRODUCTS/mulhacen/QA/depolarization_calibration/")
    fig_.tight_layout()
    plt.savefig(save_dir / "linear_volume_depolarization_ratio_532xa.png")
    plt.close(fig_)

    assert "signal_532xta" in [*dataset.variables]
    assert "linear_volume_depolarization_ratio_532xa" in [*dataset.variables]
    dataset.close()