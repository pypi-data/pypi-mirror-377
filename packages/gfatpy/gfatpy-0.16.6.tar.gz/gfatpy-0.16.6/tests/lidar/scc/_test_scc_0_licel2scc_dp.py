from datetime import datetime, time
import re
from pathlib import Path

from loguru import logger

from gfatpy.lidar.scc.licel2scc import licel2scc_depol
from gfatpy.utils.io import read_yaml, unzip_file

SCC_INFO = read_yaml(Path(r"./gfatpy/env_files/info_scc_example.yml"))
RAW_DIR = Path(r"./tests/datos/RAW")
OUTPUT_DIR = Path(r"./tests/datos/PRODUCTS")
SCC_SERVER_SETTINGS = SCC_INFO["server_settings"]
temperature = 20
pressure = 1013.25
licel_timezone = "UTC"
scc_id = 773
date_ = datetime(2023, 8, 30)
date_str = date_.strftime("%Y%m%d")
year, month, day = date_.year, date_.month, date_.day
ini_hour = time(2, 45)
# sum date_ and ini_hour
datetime_ = datetime.combine(date_, ini_hour)
datetime_str = datetime_.strftime("%Y%m%d_%H%M")
logger.info(f"date_: {date_}")
logger.info(f"Year: {year}, Month: {month}, Day: {day}")
logger.info(f"Initial hour: {ini_hour}")
measurement_id = f"{year:04}{month:02}{day:02}gra{ini_hour.strftime('%H%M')}"
logger.info(f"Measurement ID: {measurement_id}")

scc_config_fn = Path(
    rf".\gfatpy\lidar\scc\scc_configFiles\alh_parameters_scc_{scc_id}_20230721.py"
)

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


def test_scc_convert():
    CustomLidarMeasurement = licel2scc_depol.create_custom_class(
        scc_config_fn.absolute().as_posix(),
        use_id_as_name=True,
        temperature=temperature,
        pressure=pressure,
    )

    tmp_dir = unzip_file(
        Path(
            rf".\tests\datos\RAW\alhambra\{year}\{month:02}\{day:02}\DP_{datetime_str}.zip"
        )
    )
    if tmp_dir is None:
        raise Exception("No P45 files found")
    tmp_dir2 = Path(tmp_dir.name)
    p45_files = [*(tmp_dir2 / f"{date_str}" / "+45").rglob("DP*")]

    if p45_files == []:
        raise Exception("No P45 files found")

    plus45_files = [file_.as_posix() for file_ in p45_files]

    n45_files = [*(tmp_dir2 / f"{date_str}" / "-45").rglob("DP*")]
    if n45_files == []:
        raise Exception("No N45 files found")
    minus45_files = [file_.as_posix() for file_ in n45_files]

    dc_tmp_dir = unzip_file(
        Path(
            rf".\tests\datos\RAW\alhambra\{year}\{month:02}\{day:02}\DC_{datetime_str}.zip"
        )
    )
    if dc_tmp_dir is None:
        raise Exception("No DC files found")
    dc_tmp_dir2 = Path(dc_tmp_dir.name)
    pattern = re.compile(r"^(R|DC)\w+")
    dark_files = [file for file in dc_tmp_dir2.rglob("*.*") if pattern.match(file.name)]

    output_path = Path(
        rf".\tests\datos\PRODUCTS\alhambra\scc\scc{scc_id}\{year}\{month:02}\{day:02}\{measurement_id}.nc"
    )

    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    CustomLidarMeasurement = licel2scc_depol.create_custom_class(
        scc_config_fn, True, temperature, pressure, licel_timezone
    )

    CustomDarkMeasurement = licel2scc_depol.create_custom_dark_class(
        scc_config_fn, True, temperature, pressure, licel_timezone
    )

    measurement = CustomLidarMeasurement(plus45_files, minus45_files)

    if dark_files:
        measurement.dark_measurement = CustomDarkMeasurement(dark_files)  # type: ignore
    else:
        raise Exception("No dark measurement files found.")

    try:
        measurement = measurement.subset_by_scc_channels()
    except ValueError as err:
        raise err

    # Save the netcdf
    measurement.set_measurement_id(output_path.name.split(".")[0])
    measurement.save_as_SCC_netcdf(output_dir=output_path.parent)

    assert output_path.exists()
