from datetime import date, datetime, time
from pathlib import Path

from linc import get_config

from gfatpy.lidar.utils.types import LidarName
from gfatpy.lidar.nc_convert.utils import search_config_file
from gfatpy.lidar.nc_convert.measurement import info2measurements

RAW_DIR = Path(r"./tests/datos/RAW")
OUTPUT_DIR = Path(r"./tests/datos/PRODUCTS")
data_dir = RAW_DIR / "alhambra" / "2023" / "08" / "30"
measurements = info2measurements(lidar_name='alhambra', target_date=date(2023, 8, 30), raw_dir=RAW_DIR)


def test_search_config_alh_with_configfile(linc_files):   
    assert measurements is not None
    assert isinstance(measurements, list) 
    target_datetime = datetime.combine(measurements[0].unique_dates[0], time(0, 0))
    config_filepath = search_config_file(
        LidarName.alh,
        target_datetime,
        Path(r".\gfatpy\lidar\nc_convert\configs\ALHAMBRA_20180101.toml"),
    )
    config = get_config(config_filepath)
    assert config.lidar.attrs["system"] == "ALHAMBRA"


def test_search_config_alh_with_datetime(linc_files):
    assert measurements is not None
    assert isinstance(measurements, list)
    target_datetime = datetime.combine(measurements[0].unique_dates[0], time(0, 0))
    config_filepath = search_config_file(
        LidarName.alh,
        target_datetime,
        None,
    )
    config = get_config(config_filepath)
    assert config.lidar.attrs["system"] == "ALHAMBRA"
