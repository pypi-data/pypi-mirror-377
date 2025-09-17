from math import isclose
from pathlib import Path
import matplotlib.pyplot as plt

from gfatpy.lidar.preprocessing.lidar_preprocessing import preprocess
from gfatpy.lidar.depolarization.retrieval import (
    add_depolarization_products,
)
from gfatpy.lidar.depolarization.calibration import eta_star_reader

RS_FL = Path(
    r"./tests/datos/PRODUCTS/alhambra/1a/2023/08/30/alh_1a_Prs_rs_xf_20230830_0315.nc"
)
ETA_DIR = Path(r"./tests/datos/PRODUCTS/alhambra/QA/depolarization_calibration/")

ETA_FL = Path(
    r"./tests/datos/PRODUCTS/alhambra/QA/depolarization_calibration/alh_eta-star_20230830_0245.nc"
)


def test_reader_depolarization_calibration_532n():

    eta_dataset = eta_star_reader(ETA_FL)
    assert isclose(
        eta_dataset["eta_star_mean_532na"].values.item(), 0.06588, rel_tol=0.005
    )
    eta_dataset.close()


def test_depolarization(linc_files):
    lidar = preprocess(
        RS_FL,
        channels=[
            "355fpa",
            "355fpp",
            "355fsa",
            "355fsp",
            "532npa",
            "532npp",
            "532nsa",
            "532nsp",
            "355npa",
            "355npp",
            "355nsa",
            "355nsp",
        ],
        crop_ranges=(0.0, 15000.0),
    )
    dataset = add_depolarization_products(lidar, depo_calib_dir=ETA_DIR)
    lidar.close()

    # plot linear volume depolarization ratio

    fig_, ax = plt.subplots(ncols=1, nrows=3, figsize=(10, 10), sharex=True)
    dataset["linear_volume_depolarization_ratio_532na"].plot(y="range", ax=ax[0], vmin=0, vmax=0.5, cmap="jet")  # type: ignore
    dataset["linear_volume_depolarization_ratio_355na"].plot(y="range", ax=ax[1], vmin=0, vmax=0.5, cmap="jet")  # type: ignore
    dataset["linear_volume_depolarization_ratio_355fa"].plot(y="range", ax=ax[2], vmin=0, vmax=0.5, cmap="jet")  # type: ignore

    save_dir = Path(r"./tests/datos/PRODUCTS/alhambra/QA/depolarization_calibration/")
    plt.savefig(save_dir / "linear_volume_depolarization_ratio_532na.png")
    plt.close(fig_)

    assert "signal_532nta" in [*dataset.variables]
    assert "signal_355nta" in [*dataset.variables]
    assert "signal_355fta" in [*dataset.variables]
    assert "linear_volume_depolarization_ratio_532na" in [*dataset.variables]
    assert "linear_volume_depolarization_ratio_355na" in [*dataset.variables]
    assert "linear_volume_depolarization_ratio_355fa" in [*dataset.variables]
    dataset.close()