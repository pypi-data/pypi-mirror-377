from time import sleep
from pathlib import Path
from datetime import datetime, date, time
from typing import Any

from numpy import isin

# nc_convert imports
from gfatpy.lidar.utils.types import LidarName
from gfatpy.lidar.utils.utils import LIDAR_INFO, licel_to_datetime
from gfatpy.lidar.nc_convert.utils import to_measurements
from gfatpy.lidar.nc_convert._converter import measurements_to_nc

# quicklook imports
from gfatpy.lidar.plot.quicklook import quicklook_from_file

# SCC imports
from loguru import logger
from gfatpy import GFATPY_DIR
from gfatpy.lidar.plot.quicklook import BoundsType
from gfatpy.lidar.scc import scc_access
from gfatpy.lidar.utils.types import MeasurementType
from gfatpy.lidar.nc_convert.measurement import Measurement
from gfatpy.lidar.scc.plot.scc_zip import SCC_zipfile
from gfatpy.utils.io import find_nearest_filepath, read_yaml
from gfatpy.lidar.scc.transfer import check_measurement_id_in_scc
from gfatpy.lidar.scc.licel2scc import licel2scc, licel2scc_depol

RAW_DIR = Path(r"tests\datos\RAW")
PRODUCTS_DIR = Path(r"tests\datos\PRODUCTS")


def nc_convert(lidar_name: str,
               target_date: str | date | None = None,
               raw_dir: str | Path = RAW_DIR,
               products_dir: str | Path = PRODUCTS_DIR
    ) -> str:

    if isinstance(raw_dir, str):
        raw_dir = Path(raw_dir)

    if not raw_dir.exists():
        raise FileNotFoundError(f"{raw_dir} does not exist.")
    
    if isinstance(products_dir, str):
        products_dir = Path(products_dir)

    lidar = LidarName(lidar_name.lower())

    if target_date is None:
        target_date = datetime.now().date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    date_raw_dir = (
        raw_dir
        / lidar.value
        / f"{target_date.year}"
        / f"{target_date.month:02}"
        / f"{target_date.day:02}"
    )

    if not date_raw_dir.exists():
        return f"{date_raw_dir} not found in {raw_dir}."

    measurements = to_measurements(date_raw_dir.glob("RS*"))
    measurements_to_nc(
        measurements,
        lidar_name=lidar,
        raw_dir=raw_dir,
        output_dir=products_dir,
    )
    netcdf_dir = (
        products_dir
        / lidar
        / "1a"
        / f"{target_date.year}"
        / f"{target_date.month:02}"
        / f"{target_date.day:02}"
    )

    return f"nc files created in {netcdf_dir.absolute().as_posix()}."


def quicklook(
    lidar_name: str, 
    channel: str, 
    target_date: str | date | None = None, 
    products_dir: str | Path = PRODUCTS_DIR,
    scale_bounds: BoundsType = 'auto'
) -> str:

    if isinstance(products_dir, str):
        products_dir = Path(products_dir)

    if not products_dir.exists():
        raise FileNotFoundError(f"{products_dir} does not exist.")

    if target_date is None:
        target_date = datetime.now().date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    datestr = target_date.strftime("%Y%m%d")
    year, month, day = target_date.year, target_date.month, target_date.day

    data_dir = (
        products_dir / lidar_name / "1a" / f"{year:04}" / f"{month:02}" / f"{day:02}"
    )
    lidarnick = LIDAR_INFO["metadata"]["name2nick"][lidar_name]
    files = [*data_dir.glob(f"{lidarnick}_1a_Prs_rs_*{year:04}{month:02}{day:02}.nc")]

    if not files:
        return f"No files found in {data_dir}."
    if len(list(files)) > 1:
        return f"More than one RS lidar netcdf file found in {data_dir}."

    quicklook_dir = products_dir / lidar_name / "quicklooks" / channel
    quicklook_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"{files[0].name} measurements found in {data_dir}.")

    quicklook_from_file(
            filepath=files[0], channels=[channel], output_dir=quicklook_dir, scale_bounds=scale_bounds  
        )
    quicklook_file = quicklook_dir / f"quicklook_{lidarnick}_{channel}_{datestr}.png"
    return f"{quicklook_file} created."


def convert_scc(
    lidar_name: str,
    scc_id: int,
    temperature: float = 20.0,
    pressure: float = 1013.25,
    target_date: str | date | None = None,
    intervals: list[Any] = [
        (time(3, 15), time(3, 45)),
        (time(3, 45), time(4, 15)),
    ],
    raw_dir: str | Path = RAW_DIR,  
    products_dir: str | Path = PRODUCTS_DIR,    
    **kwargs,
) -> list[str] | str:

    if isinstance(raw_dir, str):
        raw_dir = Path(raw_dir)

    if not raw_dir.exists():
        raise FileNotFoundError(f"{raw_dir} does not exist.")

    if isinstance(products_dir, str):
        products_dir = Path(products_dir)

    if target_date is None:
        target_date = datetime.now().date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    logger.info(f"Launching SCC conversion for {lidar_name} on {target_date}.")

    year, month, day = target_date.year, target_date.month, target_date.day

    nc_scc_files = []
    for ini_hour, end_hour in intervals:

        target_period = (
            datetime.combine(target_date, ini_hour),
            datetime.combine(target_date, end_hour),
        )

        nc_scc_dir = (
            products_dir
            / f"{lidar_name}"
            / "scc"
            / f"scc{scc_id}"
            / f"{year:04}"
            / f"{month:02}"
            / f"{day:02}"
        )
        nc_scc_dir.mkdir(parents=True, exist_ok=True)

        scc_config_dir = Path(
            kwargs.get(
                "scc_config_dir", GFATPY_DIR / "lidar" / "scc" / "scc_configFiles"
            )
        )

        scc_config_fn = find_nearest_filepath(
            scc_config_dir,
            f"alh_parameters_scc_{scc_id}_*.py",
            4,
            target_period[0],
            and_previous=True,
        )
        logger.info(f"Using {scc_config_fn.name} for SCC conversion.")

        # Define custom class for regular lidar measurements
        CustomLidarMeasurement = licel2scc.create_custom_class(
            scc_config_fn.absolute().as_posix(),
            use_id_as_name=True,
            temperature=temperature,
            pressure=pressure,
        )

        data_dir = (
            raw_dir
            / "alhambra"
            / f"{target_date.year:04}"
            / f"{target_date.month:02}"
            / f"{target_date.day:02}"
        )
        measurements = to_measurements(
            data_dir.glob(
                f"RS_{target_date.year:04}{target_date.month:02}{target_date.day:02}*"
            )
        )
        if not measurements:
            logger.warning(f"No measurements found in {data_dir}.")
            continue

        logger.info(f"{len(measurements)} measurements found in {data_dir}.")
        logger.info("First measurement:")
        logger.info(print(measurements[0]))

        for measurement in measurements:
            file_set = set() 
            file_set = measurement.get_filepaths(within_period=target_period)
            if len(file_set) == 0:
                continue
            else:
                logger.info(f"{len(file_set)} files found in {measurement.path.name}.")            

            if len(file_set) < 30:
                logger.warning(
                    f"Interval {ini_hour.strftime('%H:%M')}-{end_hour.strftime('%H:%M')} has less than 30 files."
                )
                continue
            
            #sort file_set 
            file_set = sorted(file_set)

            #Get initial hour from first file in file_set
            first_hour = licel_to_datetime(file_set[0].name)
            
            measurement_id = f"{year:04}{month:02}{day:02}gra{first_hour.strftime('%H%M')}"
            rs_files_slot = sorted([file_.as_posix() for file_ in file_set])

            dc_path = measurement.path.parent / measurement.path.name.replace("RS", "DC")
            if dc_path.exists():
                dc_measurement = Measurement(
                    type=MeasurementType("DC"),
                    path=dc_path,
                )
                logger.info(f"Found coincident DC measurement: {dc_measurement.path.name}.")
            else:
                try:
                    dc_measurement = to_measurements(data_dir.glob("DC*"))[0]
                    logger.info(
                        f"Found non-coincident DC measurement: {dc_measurement.path.name}."
                    )
                except IndexError:
                    logger.warning(f"No DC measurements found in {data_dir}.")
                    continue

            if dc_measurement.is_zip:
                dc_measurement.extract_zip()
                if dc_measurement.unzipped_path is not None:
                    dc_files_patt = (
                        dc_measurement.unzipped_path / "**" / "*.[0-9]*"
                    ).as_posix()
                else:
                    raise ValueError(f"Error extracting {dc_measurement.path}.")
            else:
                dc_files_patt = dc_measurement.path.as_posix()

            licel2scc.convert_to_scc(
                CustomLidarMeasurement,
                rs_files_slot,
                dc_files_patt,
                measurement_id,
                output_dir=nc_scc_dir,
            )
            if not (nc_scc_dir / f"{measurement_id}.nc").exists():
                logger.warning(f"Error converting {measurement_id} to SCC.")
                continue
            else:
                logger.info(f"{measurement_id}.nc created.")
                nc_scc_files.append(nc_scc_dir / f"{measurement_id}.nc")
    if nc_scc_files == []:
        return f"No SCC files created for {lidar_name} on {target_date}."
    return [nc.name for nc in nc_scc_files]


def convert_scc_dp(
    lidar_name: str,
    scc_id: int,
    temperature: float = 20.0,
    pressure: float = 1013.25,
    target_date: str | date | None = None,
    licel_timezone: str = "UTC",
    raw_dir: str | Path = RAW_DIR,
    products_dir: str | Path = PRODUCTS_DIR,
    **kwargs,
) -> list[str] | str:

    if isinstance(raw_dir, str):
        raw_dir = Path(raw_dir)
    
    if not raw_dir.exists():
        raise FileNotFoundError(f"{raw_dir} does not exist.")

    if isinstance(products_dir, str):
        products_dir = Path(products_dir)

    if target_date is None:
        target_date = datetime.now().date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    year, month, day = target_date.year, target_date.month, target_date.day
    date_str = target_date.strftime("%Y%m%d")

    scc_config_dir = Path(
        kwargs.get("scc_config_dir", GFATPY_DIR / "lidar" / "scc" / "scc_configFiles")
    )
    scc_config_fn = find_nearest_filepath(
        scc_config_dir,
        f"alh_parameters_scc_{scc_id}_*.py",
        4,
        datetime.combine(target_date, time(0, 0)),
        and_previous=True,
    )
    logger.info(f"Using {scc_config_fn.name} for SCC conversion.")

    CustomLidarMeasurement = licel2scc_depol.create_custom_class(
        scc_config_fn.absolute().as_posix(),
        use_id_as_name=True,
        temperature=temperature,
        pressure=pressure,
    )

    # Find DP measurements
    data_dir = raw_dir / lidar_name / f"{year}" / f"{month:02}" / f"{day:02}"
    measurements = to_measurements(data_dir.glob(f"DP_{date_str}*.zip"))
    if not measurements:
        logger.warning(f"No measurements found in {data_dir}.")
        return f"No measurements found in {data_dir}."
    logger.info(f"{len(measurements)} measurements found in {data_dir}.")
    output_paths = []
    for measurement in measurements:
        if measurement.is_zip:
            measurement.extract_zip()
            if measurement.unzipped_path is not None:
                plus45_files = [
                    file_.as_posix()
                    for file_ in measurement.unzipped_path.rglob(f"{date_str}/+45/*.*")
                ]
                minus45_files = [
                    file_.as_posix()
                    for file_ in measurement.unzipped_path.rglob(f"{date_str}/-45/*.*")
                ]
            else:
                raise ValueError(f"Error extracting {measurement.path}.")
        else:
            plus45_files = [
                file_.as_posix()
                for file_ in measurement.path.rglob(f"{date_str}/+45/*.*")
            ]
            minus45_files = [
                file_.as_posix()
                for file_ in measurement.path.rglob(f"{date_str}/-45/*.*")
            ]

        if plus45_files == []:
            raise Exception("No P45 files found")

        if plus45_files == []:
            raise Exception("No N45 files found")

        if measurement.has_dc:
            dc_tmp_path = measurement.dc_path
            if dc_tmp_path is not None:
                dc_measurement = to_measurements(data_dir.glob(dc_tmp_path.name))[0]
                if dc_measurement.is_zip:
                    dc_measurement.extract_zip()

                    if dc_measurement.unzipped_path is not None:
                        dark_files = [
                            file_.as_posix()
                            for file_ in dc_measurement.unzipped_path.rglob(
                                f"{date_str}/[RD]*.*"
                            )
                        ]
                    else:
                        raise ValueError(f"Error extracting {dc_measurement.path}.")
                else:
                    dark_files = [
                        file_.as_posix()
                        for file_ in dc_measurement.path.rglob(f"{date_str}/[RD]*.*")
                    ]
        hour_str = measurement.path.name.split(".")[0].split("_")[-1]
        measurement_id = f"{year:04}{month:02}{day:02}gra{hour_str}"
        output_path = (
            products_dir
            / lidar_name
            / "scc"
            / f"scc{scc_id}"
            / f"{year}"
            / f"{month:02}"
            / f"{day:02}"
            / f"{measurement_id}.nc"
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
        output_paths.append(output_path.absolute().as_posix())
    return output_paths


def send_to_scc(
    lidar_name: str,
    scc_id: int,
    info_scc_config_path: str | Path,
    target_date: str | date | None = None,
    products_dir: str | Path = PRODUCTS_DIR,
    **kwargs,
) -> list[str] | str:
    
    if isinstance(products_dir, str):
        products_dir = Path(products_dir)

    # Check if the environment variable is set
    if isinstance(info_scc_config_path, str):
        info_scc_config_path = Path(info_scc_config_path)

    config_path = info_scc_config_path

    if not config_path.exists():
        raise ValueError(
            "The environment variable 'SCC_CONFIG_FILE' is not set in the .env"
        )

    logger.info(f"Using {config_path} for SCC conversion.")

    # Construct the file path
    SCC_INFO = read_yaml(config_path)
    SCC_SERVER_SETTINGS = SCC_INFO["server_settings"]

    if target_date is None:
        target_date = datetime.now().date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    year, month, day = target_date.year, target_date.month, target_date.day

    scc_dir = (
        products_dir
        / lidar_name
        / "scc"
        / f"scc{scc_id}"
        / f"{year:04}"
        / f"{month:02}"
        / f"{day:02}"
    )
    if len(list(scc_dir.glob("*.nc"))) == 0:
        return f"No files found in {scc_dir}."
    else:
        files = scc_dir.glob("*.nc")        
    
    succeeded_upload_files = []
    for file_ in files:
        logger.info(f"Launching SCC conversion for {lidar_name} on {target_date}.")
        measurement_id = file_.name.replace(".nc", "")

        scc_obj = scc_access.SCC(
            tuple(SCC_SERVER_SETTINGS["basic_credentials"]),
            SCC_SERVER_SETTINGS["output_dir"],
            SCC_SERVER_SETTINGS["base_url"],
        )

        measurement_exists, _ = check_measurement_id_in_scc(
            SCC_SERVER_SETTINGS, measurement_id
        )

        if measurement_exists:
            logger.info(
                f"Measurement {measurement_id} already exists in SCC: {measurement_exists}."
            )
            continue

        scc_obj.login(SCC_SERVER_SETTINGS["website_credentials"])
        measurement_id_from_server = scc_obj.upload_file(
            filename=file_, system_id=scc_id
        )

        scc_obj.logout()
        if not measurement_id_from_server:
            logger.warning(f"Error uploading {measurement_id}.nc to SCC.")
            continue

        logger.info(f"{measurement_id}.nc uploaded to SCC.")
        succeeded_upload_files.append(file_.name)
    return succeeded_upload_files

def download_from_scc(
    lidar_name: str,
    scc_id: int,
    info_scc_config_path: str | Path,
    target_date: str | date | None = None,
    products_dir: str | Path = PRODUCTS_DIR,
    **kwargs,
) -> list[str] | str:
    
    if isinstance(products_dir, str):
        products_dir = Path(products_dir)

    # Check if the environment variable is set
    if isinstance(info_scc_config_path, str):
        info_scc_config_path = Path(info_scc_config_path)

    config_path = info_scc_config_path

    if not config_path.exists():
        succeeded_upload_files = "No files downloaded."
        raise ValueError(
            "The environment variable 'SCC_CONFIG_FILE' is not set in the .env"
        )

    logger.info(f"Using {config_path} for SCC conversion.")

    # Construct the file path
    SCC_INFO = read_yaml(config_path)
    SCC_SERVER_SETTINGS = SCC_INFO["server_settings"]
    
    if target_date is None:
        target_date = datetime.now().date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    year, month, day = target_date.year, target_date.month, target_date.day

    scc_dir = (
        products_dir
        / lidar_name
        / "scc"
        / f"scc{scc_id}"
        / f"{year:04}"
        / f"{month:02}"
        / f"{day:02}"
    )

    product_scc_dir = scc_dir / "products"
    product_scc_dir.mkdir(parents=True, exist_ok=True)
    SCC_SERVER_SETTINGS["output_dir"] = product_scc_dir

    succeeded_upload_files = []
    for file_ in scc_dir.glob(f"{year:04}{month:02}{day:02}*.nc"):
        logger.info(f"Downloading {file_.name} from SCC.")
        measurement_id = file_.name.replace(".nc", "")

        scc_obj = scc_access.SCC(
            tuple(SCC_SERVER_SETTINGS["basic_credentials"]),
            SCC_SERVER_SETTINGS["output_dir"],
            SCC_SERVER_SETTINGS["base_url"],
        )

        scc_obj.login(SCC_SERVER_SETTINGS["website_credentials"])

        # Manejo de reintentos
        retries = 5
        for attempt in range(retries):
            try:
                scc_obj.monitor_processing(measurement_id)
                succeeded_upload_files.append(file_.name)
                logger.info(f"{file_.name} products downloaded from SCC.")
                break
            except TimeoutError:
                if attempt < retries - 1:
                    # Esperar un tiempo antes de reintentar
                    sleep(60)
                else:
                    logger.warning(
                        f"Process was queued too long after {retries} attempts."
                    )
                    continue

        scc_obj.logout()
        
        if succeeded_upload_files == []:
            succeeded_upload_files = f"No files downloaded."
            
    return succeeded_upload_files

def plot_scc(
    lidar_name: str,
    scc_id: int,
    target_date: str | date | None = None, 
    products_dir: str | Path = PRODUCTS_DIR
) -> list[str] | str:
    
    def flatten_list(nested_list):
        flattened = []
        for item in nested_list:
            if isinstance(item, list):
                flattened.extend(flatten_list(item))
            else:
                flattened.append(item)
        return flattened

    if isinstance(products_dir, str):
        products_dir = Path(products_dir)

    if not products_dir.exists():
        raise FileNotFoundError(f"{products_dir} does not exist.")

    if target_date is None:
        target_date = datetime.now().date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    year, month, day = target_date.year, target_date.month, target_date.day

    scc_dir = (
        products_dir
        / lidar_name
        / "scc"
        / f"scc{scc_id}"
        / f"{year:04}"
        / f"{month:02}"
        / f"{day:02}"
        / "products"
    )

    if not scc_dir.exists():
        return f"{scc_dir} does not exist."

    logger.info(f"Searching for products in {scc_dir}.")
    products = [*scc_dir.glob("*.zip")]
    logger.info(f"{len(products)} products found in {scc_dir}.")

    # Plotting scc results
    plot_scc_dir = scc_dir / "plots"
    plot_scc_dir.mkdir(parents=True, exist_ok=True)

    if not products:
        return f"No SCC files found in {scc_dir}."
    plot_paths = []
    for product in products:
        logger.info(f"Plotting {product.name}.")
        try:
            scc_zip = SCC_zipfile(product)
        except Exception as e:
            logger.warning(f"Error reading {product} as SCC zipfile.")
            continue
        plot_paths_ = scc_zip.plot(
            output_dir=plot_scc_dir, dpi=150, range_limits=(0, 10)
        )
        if isinstance(plot_paths_, list):
            plot_paths.extend(plot_paths_)
        else:
            plot_paths.append(plot_paths_)

    flattened_list = flatten_list(plot_paths)

    plot_names = [plot.name for plot in flattened_list]
    return plot_names
