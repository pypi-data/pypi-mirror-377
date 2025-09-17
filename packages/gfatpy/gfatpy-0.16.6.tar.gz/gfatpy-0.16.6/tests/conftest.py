import os
import shutil
import pytest
import matplotlib
from pathlib import Path
from datetime import date

import rpgpy

from gfatpy.lidar.nc_convert.measurement import (
    info2measurements,    
)

matplotlib.use("Agg")

RAW_DIR = Path(r"./tests/datos/RAW")
OUTPUT_DIR = Path(r"./tests/datos/PRODUCTS")


def pytest_addoption(parser):
    parser.addoption("--runmhc", action="store_true", default=False)
    parser.addoption("--runalh", action="store_true", default=False)
    parser.addoption("--runlinc", action="store_true", default=False)
    parser.addoption("--cleanup", action="store_true", default=False)
    parser.addoption("--runnpl", action="store_true", default=False)
    parser.addoption("--runnbl", action="store_true", default=False)
    parser.addoption("--runradar", action="store_true", default=False)


@pytest.fixture(scope="session")
def run_linc(pytestconfig):
    return pytestconfig.getoption("runlinc")


@pytest.fixture(scope="session")
def run_linc_mhc(pytestconfig):
    return pytestconfig.getoption("runmhc")


@pytest.fixture(scope="session")
def run_linc_alh(pytestconfig):
    return pytestconfig.getoption("runalh")


@pytest.fixture(scope="session")
def cleanup(pytestconfig):
    return pytestconfig.getoption("cleanup")


@pytest.fixture(scope="session")
def run_npl(pytestconfig):
    return pytestconfig.getoption("runnpl")


@pytest.fixture(scope="session")
def run_nbl(pytestconfig):
    return pytestconfig.getoption("runnbl")


@pytest.fixture(scope="session")
def run_radar(pytestconfig):
    return pytestconfig.getoption("runradar")


@pytest.fixture(scope="session")
def linc_files(run_linc, run_linc_mhc, run_linc_alh, cleanup):
    if run_linc:
        run_linc_mhc = True
        run_linc_alh = True

    if run_linc_mhc:
        measurements = info2measurements(
            lidar_name="mulhacen", target_date=date(2022, 8, 8), raw_dir=RAW_DIR
        )
        if measurements is None:
            raise Exception("No measurements found")
        for measurement in measurements:
            measurement.to_nc(by_dates=False, output_dir=OUTPUT_DIR)
            measurement.remove_tmp_unzipped_dir()

        measurements = info2measurements(
            lidar_name="mulhacen", target_date=date(2022, 6, 17), raw_dir=RAW_DIR
        )
        if measurements is None:
            raise Exception("No measurements found")
        for measurement in measurements:
            measurement.to_nc(by_dates=False, output_dir=OUTPUT_DIR)
            measurement.remove_tmp_unzipped_dir()

    if run_linc_alh:
        measurements = info2measurements(
            lidar_name="alhambra", target_date=date(2023, 2, 22), raw_dir=RAW_DIR
        )
        if measurements is None:
            raise Exception("No measurements found")
        for measurement in measurements:
            measurement.to_nc(by_dates=False, output_dir=OUTPUT_DIR)
            measurement.remove_tmp_unzipped_dir()

        measurements = info2measurements(
            lidar_name="alhambra", target_date=date(2023, 8, 30), raw_dir=RAW_DIR
        )
        if measurements is None:
            raise Exception("No measurements found")
        for measurement in measurements:
            measurement.to_nc(by_dates=False, output_dir=OUTPUT_DIR)
            measurement.remove_tmp_unzipped_dir()

    yield  # This yield waits until fixture is out of scope (after running all tests in this case)  # noqa: E501
    if cleanup:
        if run_linc_mhc:
            mhc_rm_path = OUTPUT_DIR / "mulhacen" / "1a" / "2022"
            if mhc_rm_path.exists():
                shutil.rmtree(mhc_rm_path)
        if run_linc_alh:
            alh_rm_path = OUTPUT_DIR / "alhambra" / "1a" / "2023"
            if alh_rm_path.exists():
                shutil.rmtree(alh_rm_path)


@pytest.fixture(scope="session")
def radar_files(run_radar, run_nbl, run_npl, cleanup):
    if run_radar:
        run_nbl = True
        run_npl = True

    if run_npl:
        # Nephele ZEN LV1
        ZEN_FILE = Path(r"tests\datos\RAW\nephele\2024\02\09\240209_015959_P00_ZEN.LV1")
        ZEN_NC = (
            Path(ZEN_FILE.parent.as_posix().replace("RAW", "PRODUCTS"))
            / f"{ZEN_FILE.name}.nc"
        )
        ZEN_NC.parent.mkdir(parents=True, exist_ok=True)
        if ZEN_NC.exists() and ZEN_NC.is_file():
            os.remove(ZEN_NC)
        rpgpy.rpg2nc(ZEN_FILE.as_posix(), ZEN_NC.as_posix())

        # Nephele PPI LV1
        PPI_FILE = Path(r"tests\datos\RAW\nephele\2023\05\17\230517_084500_P00_PPI.LV1")
        PPI_NC = (
            Path(PPI_FILE.parent.as_posix().replace("RAW", "PRODUCTS"))
            / f"{PPI_FILE.name}.nc"
        )
        PPI_NC.parent.mkdir(parents=True, exist_ok=True)
        if PPI_NC.exists() and PPI_NC.is_file():
            os.remove(PPI_NC)

        rpgpy.rpg2nc(PPI_FILE.as_posix(), PPI_NC.as_posix())

        # Nephele RHI LV1
        RHI_FILE = Path(r"tests\datos\RAW\nephele\2024\02\09\240209_022515_P00_RHI.LV1")
        RHI_NC = (
            Path(RHI_FILE.parent.as_posix().replace("RAW", "PRODUCTS"))
            / f"{RHI_FILE.name}.nc"
        )
        RHI_NC.parent.mkdir(parents=True, exist_ok=True)
        if RHI_NC.exists() and RHI_NC.is_file():
            os.remove(RHI_NC)
        rpgpy.rpg2nc(RHI_FILE.as_posix(), RHI_NC.as_posix())

    if run_nbl:
        # Nebula KA ZEN LV1
        KA_ZEN_FILE = Path(
            r"tests\datos\RAW\nebula_ka\2024\03\13\240313_150001_P00_ZEN.LV1"
        )
        KA_ZEN_NC = (
            Path(KA_ZEN_FILE.parent.as_posix().replace("RAW", "PRODUCTS"))
            / f"{KA_ZEN_FILE.name}.nc"
        )
        KA_ZEN_NC.parent.mkdir(parents=True, exist_ok=True)
        if KA_ZEN_NC.exists() and KA_ZEN_NC.is_file():
            os.remove(KA_ZEN_NC)
        rpgpy.rpg2nc(KA_ZEN_FILE.as_posix(), KA_ZEN_NC.as_posix())

        # Nebula W ZEN LV1
        ZEN_FILE = Path(
            r"tests\datos\RAW\nebula_w\2024\03\13\240313_150001_P00_ZEN.LV1"
        )
        W_ZEN_NC = (
            Path(ZEN_FILE.parent.as_posix().replace("RAW", "PRODUCTS"))
            / f"{ZEN_FILE.name}.nc"
        )
        W_ZEN_NC.parent.mkdir(parents=True, exist_ok=True)
        if W_ZEN_NC.exists() and W_ZEN_NC.is_file():
            os.remove(W_ZEN_NC)
        rpgpy.rpg2nc(ZEN_FILE.as_posix(), W_ZEN_NC.as_posix())

        # Nebula KA ZEN LV0
        KA_ZEN_FILE = Path(
            r"tests\datos\RAW\nebula_ka\2024\03\13\240313_150001_P00_ZEN.LV0"
        )
        ZEN_NC = (
            Path(KA_ZEN_FILE.parent.as_posix().replace("RAW", "PRODUCTS"))
            / f"{KA_ZEN_FILE.name}.nc"
        )
        ZEN_NC.parent.mkdir(parents=True, exist_ok=True)
        if ZEN_NC.exists() and ZEN_NC.is_file():
            os.remove(ZEN_NC)
        rpgpy.rpg2nc(KA_ZEN_FILE.as_posix(), ZEN_NC.as_posix())

        # Nebula W ZEN LV0
        ZEN_FILE = Path(
            r"tests\datos\RAW\nebula_w\2024\03\13\240313_150001_P00_ZEN.LV0"
        )
        ZEN_NC = (
            Path(ZEN_FILE.parent.as_posix().replace("RAW", "PRODUCTS"))
            / f"{ZEN_FILE.name}.nc"
        )
        ZEN_NC.parent.mkdir(parents=True, exist_ok=True)
        if ZEN_NC.exists() and ZEN_NC.is_file():
            os.remove(ZEN_NC)
        rpgpy.rpg2nc(ZEN_FILE.as_posix(), ZEN_NC.as_posix())

    yield  # This yield waits until fixture is out of scope (after running all tests in this case)  # noqa: E501
    if cleanup:
        if run_nbl:
            nbl_ka_path = Path(r"tests\datos\PRODUCTS\nebula_ka\1a\2024")
            if nbl_ka_path.exists():
                shutil.rmtree(nbl_ka_path)
            nbl_w_path = Path(r"tests\datos\PRODUCTS\nebula_w\1a\2024")
            if nbl_w_path.exists():
                shutil.rmtree(nbl_w_path)

        if run_npl:
            npl_path_zen = Path(r"tests\datos\PRODUCTS\nephele\1a\2021")
            npl_path_ppi = Path(r"tests\datos\PRODUCTS\nephele\1a\2023")
            npl_path_rhi = Path(r"tests\datos\PRODUCTS\nephele\1a\2024")
            if npl_path_zen.exists():
                shutil.rmtree(npl_path_zen)
            if npl_path_ppi.exists():
                shutil.rmtree(npl_path_ppi)
            if npl_path_rhi.exists():
                shutil.rmtree(npl_path_rhi)


@pytest.fixture(scope="session")
def clean_depo_calibrations():
    calib_dir = {}
    calib_dir["alh"] = Path(
        r"tests\datos\PRODUCTS\alhambra\QA\depolarization_calibration"
    )
    calib_dir["mhc"] = Path(
        r"tests\datos\PRODUCTS\alhambra\QA\depolarization_calibration"
    )
    for calib_dir in calib_dir.values():
        if calib_dir.exists():
            shutil.rmtree(calib_dir)
        calib_dir.mkdir(parents=True)

