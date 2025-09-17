from datetime import datetime, date
from pathlib import Path
from tkinter import N

from gfatpy.lidar.nc_convert.measurement import info2measurements, Measurement
from gfatpy.lidar.utils.types import MeasurementType

RAW_DIR = Path(r"./tests/datos/RAW")
OUTPUT_DIR = Path(r"./tests/datos/PRODUCTS")

lidar_name: str = "alhambra"
target_date = datetime(2023, 8, 30)
data_dir = (
    RAW_DIR
    / "alhambra"
    / f"{target_date.year}"
    / f"{target_date.month:02d}"
    / f"{target_date.day:02d}"
)

measurements = info2measurements(
    lidar_name="alhambra",
    target_date=target_date,
    raw_dir=RAW_DIR,
    measurement_type=MeasurementType("RS"),
)
if measurements is not None and len(measurements) > 0:
    for m in measurements:
        if m.path.name == "RS_20230830_0315.zip":
            measurement = m
            break

def test_measurement_class_properties():
    # file name
    assert type(measurement) == Measurement    
    assert measurement.path == data_dir / "RS_20230830_0315.zip"
    assert measurement.type == "RS"
    assert measurement.session_datetime == datetime(2023, 8, 30, 3, 15, 0)
    assert len(measurement.filenames) == 60
    assert measurement.lidar_name.value == "alhambra"
    assert measurement.telescope == "xf"
    assert measurement.is_zip == True
    assert len(measurement.datetimes) == 60
    assert sorted(measurement.datetimes)[0] == datetime(2023, 8, 30, 3, 15, 18)
    assert sorted(measurement.datetimes)[-1] == datetime(2023, 8, 30, 4, 15, 29)
    assert sorted(measurement.unique_dates)[0] == date(2023, 8, 30)
    assert measurement.sub_dirs[0] == f'{target_date.strftime("%Y%m%d")}'
    assert measurement.has_linked_dc == True
    assert type(measurement.dc) == Measurement
    file_set = measurement.get_filepaths()
    assert file_set is not None
    assert isinstance(file_set, set)
    assert len(file_set) == 60


def test_get_files_within_period():
    # Select files between 06:30 to 06:45 |string format = "RS2322200_*"
    date_ini = datetime(2023, 8, 30, 3, 15)
    date_end = datetime(2023, 8, 30, 3, 20)
    files = measurement.get_filenames_within_datetime_slice(slice(date_ini, date_end))
    assert len(files) == 5
    file_set = measurement.get_filepaths(pattern_or_list = files)
    assert file_set is not None
    assert len(file_set) == 5


def test_remove_unzipped_path():
    filepath = measurement.unzip()
    assert filepath is not None
    assert filepath.exists()
    measurement.remove_tmp_unzipped_dir()
    assert measurement._unzipped_dir is None