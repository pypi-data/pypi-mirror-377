from pathlib import Path

from loguru import logger
from gfatpy.lidar.scc.transfer import check_measurement_id_in_scc, check_scc_connection
from gfatpy.utils.io import read_yaml

info_scc_path_example = Path(r"./gfatpy/env_files/info_scc_example.yml")
info_scc_path = Path(r"./gfatpy/env_files/info_scc_user.yml")
try:
    SCC_INFO = read_yaml(info_scc_path)
except FileNotFoundError:
    logger.error(f"File {info_scc_path} not found. Please use the example file: {info_scc_path_example} to provide your SCC login fields.")
    
SCC_SERVER_SETTINGS = SCC_INFO["server_settings"]


def test_check_scc_connection():
    assert check_scc_connection(SCC_SERVER_SETTINGS)


def test_get_measurement():
    file2check = "20230222gra9999"

    check_flag, meas_obj = check_measurement_id_in_scc(SCC_SERVER_SETTINGS, file2check)

    assert check_flag
    assert meas_obj is not None
    assert meas_obj.id == file2check
