import numpy as np
import xarray as xr
from pathlib import Path
from loguru import logger
from datetime import datetime, time

from gfatpy.lidar.scc.licel2scc import licel2scc
from gfatpy.lidar.utils.types import MeasurementType
from gfatpy.utils.io import find_nearest_filepath, read_yaml
from gfatpy.lidar.nc_convert.measurement import info2measurements


info_scc_path_example = Path(r"./gfatpy/env_files/info_scc_example.yml")
info_scc_path = Path(r"./gfatpy/env_files/info_scc_user.yml")
try:
    SCC_INFO = read_yaml(info_scc_path)
except FileNotFoundError:
    logger.error(f"File {info_scc_path} not found. Please use the example file: {info_scc_path_example} to provide your SCC login fields.")
    
RAW_DIR = Path(r"./tests/datos/RAW")
OUTPUT_DIR = Path(r"./tests/datos/PRODUCTS")
SCC_SERVER_SETTINGS = SCC_INFO["server_settings"]

scc_id = 781
# today = datetime.now()
today = datetime(2023, 8, 30)
year, month, day = today.year, today.month, today.day
ini_hour, end_hour = time(3, 15), time(3, 45)
logger.info(f"Today: {today}")
logger.info(f"Year: {year}, Month: {month}, Day: {day}")
logger.info(f"Initial hour: {ini_hour}, End hour: {end_hour}")
measurement_id = f"{year:04}{month:02}{day:02}gra{ini_hour.strftime('%H%M')}"
logger.info(f"Measurement ID: {measurement_id}")
target_period = slice(
    datetime.combine(today, ini_hour), datetime.combine(today, end_hour)
)
logger.info(f"Target period: {target_period}")
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


def test_licel2scc():
    # Convert RS measurement to SCC
    # Find nearest scc config file
    scc_config_dir = Path(r".\gfatpy\lidar\scc\scc_configFiles")
    scc_config_fn = find_nearest_filepath(
        scc_config_dir, f"alh_parameters_scc_{scc_id}_*.py", 4, today, and_previous=True
    )

    # Logger scc config file name
    logger.info(f"SCC config file: {scc_config_fn.name}")

    temperature = 20
    pressure = 1013.25

    CustomLidarMeasurement = licel2scc.create_custom_class(
        scc_config_fn.absolute().as_posix(),
        use_id_as_name=True,
        temperature=temperature,
        pressure=pressure,
    )

    measurements = info2measurements(
        lidar_name="alhambra",
        target_date=today,
        raw_dir=RAW_DIR,
        measurement_type=MeasurementType("RS"),
    )
    assert measurements is not None

    file_set = set()
    for measurement in measurements:
        logger.info(f"Searching files in {measurement.path.name}")
        files_ = measurement.get_filenames_within_datetime_slice(target_period)
        if files_ is None or len(files_) == 0:
            continue
        file_set = measurement.get_filepaths(pattern_or_list=files_)
        if file_set is None or len(file_set) == 0:
            continue
        else:
            logger.info(f"Files found: {len(file_set)}")
            break

    if file_set is None or len(file_set) == 0:
        raise ValueError("No files found in provided measurements.")

    rs_files_slot = sorted([file_.as_posix() for file_ in file_set])

    # Logger with the first and last name of the files
    logger.info(f"First file: {rs_files_slot[0].split('/')[-1]}")
    logger.info(f"Last file: {rs_files_slot[-1].split('/')[-1]}")

    # First search corresponding DC measurement
    if measurement.dc is not None:
        logger.info(f"Coincident DC measurement path: {measurement.dc.path}")
        dc_measurement = measurement.dc
    else:
        # otherwise, search for the nearest DC measurement in the same day
        dc_measurement = info2measurements(
            lidar_name="alhambra",
            target_date=today,
            raw_dir=RAW_DIR,
            measurement_type=MeasurementType("DC"),
        )
        if dc_measurement is None:
            raise FileNotFoundError(
                "No DC measurements found in provided measurements."
            )
        elif len(dc_measurement) == 0:  # type: ignore
            raise FileNotFoundError(
                "No DC measurements found in provided measurements."
            )
        else:
            dc_measurement = dc_measurement[0]
            logger.info(
                f"Nearest not-coincident DC measurement path: {dc_measurement.path}"
            )

    if dc_measurement.is_zip:
        unzipped_path = dc_measurement.unzip()
        if unzipped_path is None:
            raise FileNotFoundError("DC measurement could not be unzipped")
        dc_files_patt = (unzipped_path / "**" / "*.[0-9]*").as_posix()
    else:
        dc_files_patt = (dc_measurement.path / "**" / "*.[0-9]*").as_posix()

    licel2scc.convert_to_scc(
        CustomLidarMeasurement,
        rs_files_slot,
        dc_files_patt,
        measurement_id,
        output_dir=nc_scc_dir,
    )

    # Check if the file was created
    if not (nc_scc_dir / f"{measurement_id}.nc").exists():
        raise ValueError("NC file was not created")

    data = xr.open_dataset(nc_scc_dir / f"{measurement_id}.nc")
    assert "Background_Profile" in data
    data["channels"] = data["channel_ID"].values

    # Check 532fta
    background_profile_mean = (
        data["Background_Profile"]
        .sel(channels=2204)
        .mean(dim="time_bck")
        .sel(points=slice(0, 1000))
        .mean(dim="points")
        .item()
    )

    assert np.isclose(background_profile_mean, 5.2114, atol=0.01)

    # for measurement in measurements:
    #     if measurement.is_zip:
    #         measurement.remove_tmp_unzipped_dir()
