from datetime import datetime, time
from pathlib import Path

from gfatpy.lidar.scc import scc_access
from gfatpy.lidar.scc.transfer import check_measurement_id_in_scc
from gfatpy.utils.io import read_yaml

from loguru import logger

info_scc_path_example = Path(r"./gfatpy/env_files/info_scc_example.yml")
info_scc_path = Path(r"./gfatpy/env_files/info_scc_user.yml")
try:
    SCC_INFO = read_yaml(info_scc_path)
except FileNotFoundError:
    logger.error(f"File {info_scc_path} not found. Please use the example file: {info_scc_path_example} to provide your SCC login fields.")
    
RAW_DIR = Path(r"./tests/datos/RAW")
OUTPUT_DIR = Path(r"./tests/datos/PRODUCTS")
SCC_SERVER_SETTINGS = SCC_INFO["server_settings"]

scc_id = 773
# today = datetime.now()
today = datetime(2023, 8, 30)
year, month, day = today.year, today.month, today.day
ini_hour = time(2, 45)
logger.info(f"Today: {today}")
logger.info(f"Year: {year}, Month: {month}, Day: {day}")
logger.info(f"Initial hour: {ini_hour})")
measurement_id = f"{year:04}{month:02}{day:02}gra{ini_hour.strftime('%H%M')}"
logger.info(f"Measurement ID: {measurement_id}")
nc_scc_dir = (
    OUTPUT_DIR
    / "alhambra"
    / "scc"
    / f"scc{scc_id}"
    / f"{year:04}"
    / f"{month:02}"
    / f"{day:02}"
)
nc_scc_dir.mkdir(parents=True, exist_ok=True)

# logger folders
logger.info(f"NC SCC dir: {nc_scc_dir}")


def test_try_upload():
    # Check if the file was created
    if not (nc_scc_dir / f"{measurement_id}.nc").exists():
        raise ValueError("NC file was not created")

    # Upload to SCC
    scc_obj = scc_access.SCC(
        tuple(SCC_SERVER_SETTINGS["basic_credentials"]),
        SCC_SERVER_SETTINGS["output_dir"],
        SCC_SERVER_SETTINGS["base_url"],
    )

    measurement_exists, _ = check_measurement_id_in_scc(
        SCC_SERVER_SETTINGS, measurement_id
    )
    if not measurement_exists:
        scc_obj = scc_access.SCC(
            tuple(SCC_SERVER_SETTINGS["basic_credentials"]),
            None,
            SCC_SERVER_SETTINGS["base_url"],
        )
        scc_obj.login(SCC_SERVER_SETTINGS["website_credentials"])
        measurement_id_from_server = scc_obj.upload_file(
            filename=nc_scc_dir / f"{measurement_id}.nc", system_id=scc_id
        )
        scc_obj.logout()

        assert measurement_id_from_server == measurement_id
    else:
        logger.warning(f"Measurement {measurement_id} already exists in SCC.")
        assert True
