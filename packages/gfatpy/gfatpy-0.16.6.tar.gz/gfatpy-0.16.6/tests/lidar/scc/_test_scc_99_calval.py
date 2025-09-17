
from datetime import datetime, time
from pathlib import Path
from gfatpy.lidar.nc_convert.measurement import Measurement, to_measurements

from gfatpy.lidar.scc import SCC_INFO, scc_access
from gfatpy.lidar.scc.licel2scc import licel2scc
from gfatpy.lidar.scc.plot.scc_zip import SCC_zipfile
from gfatpy.lidar.scc.transfer import check_measurement_id_in_scc
from gfatpy.lidar.utils.types import MeasurementType
from gfatpy.utils.io import find_nearest_filepath

from loguru import logger

RAW_DIR = Path(r"./tests/datos/RAW")
OUTPUT_DIR = Path(r"./tests/datos/PRODUCTS")
SCC_SERVER_SETTINGS = SCC_INFO["server_settings"]

scc_id=781 
# today = datetime.now()
today = datetime(2023, 2, 22)
year, month, day = today.year, today.month, today.day
ini_hour, end_hour = time(0, 43), time(0, 52)
logger.info(f"Today: {today}")
logger.info(f"Year: {year}, Month: {month}, Day: {day}")
logger.info(f"Initial hour: {ini_hour}, End hour: {end_hour}")
measurement_id = f"{year:04}{month:02}{day:02}gra{ini_hour.strftime('%H%M')}"
logger.info(f"Measurement ID: {measurement_id}")
target_period = (datetime.combine(today, ini_hour), datetime.combine(today, end_hour))
logger.info(f"Target period: {target_period}")
nc_scc_dir = OUTPUT_DIR / "alhambra" / "scc" / f"scc{scc_id}" / f"{year:04}" / f"{month:02}" / f"{day:02}"
nc_scc_dir.mkdir(parents=True, exist_ok=True)
product_scc_dir = OUTPUT_DIR / "alhambra" / "scc" / f"scc{scc_id}" / f"{year:04}" / f"{month:02}" / f"{day:02}" / "products"
product_scc_dir.mkdir(parents=True, exist_ok=True)
plot_scc_dir = OUTPUT_DIR / "alhambra" / "scc" / f"scc{scc_id}" / f"{year:04}" / f"{month:02}" / f"{day:02}" / "plots"
plot_scc_dir.mkdir(parents=True, exist_ok=True)

#logger folders
logger.info(f"NC SCC dir: {nc_scc_dir}")
logger.info(f"Product SCC dir: {product_scc_dir}")
logger.info(f"Plot SCC dir: {plot_scc_dir}")

def test_calval():
    #Convert RS measurement to SCC
        #Find nearest scc config file
    scc_config_dir = Path(".\gfatpy\lidar\scc\scc_configFiles")
    scc_config_fn = find_nearest_filepath(
    scc_config_dir,
    f"alh_parameters_scc_{scc_id}_*.py",
    4,
    today,
    and_previous=True
    )

    #Logger scc config file name
    logger.info(f"SCC config file: {scc_config_fn.name}")

    temperature = 20
    pressure = 1013.25

    CustomLidarMeasurement = licel2scc.create_custom_class(
        scc_config_fn.absolute().as_posix(),
        use_id_as_name=True,
        temperature=temperature,
        pressure=pressure,
    )

    data_dir = RAW_DIR / "alhambra" / f"{today.year:04}" / f"{today.month:02}" / f"{today.day:02}"
    measurements = to_measurements(data_dir.glob(f"RS_{today.year:04}{today.month:02}{today.day:02}*"))
    file_set = set()
    for measurement in measurements:
        file_set = measurement.get_filepaths(within_period=target_period)
        if len(file_set) == 0:
            continue
        else:
            break

    if len(file_set) == 0:  
        raise ValueError("No files found in provided measurements.")
    
    rs_files_slot = sorted([file_.as_posix() for file_ in file_set])

    #Logger with the first and last name of the files 
    logger.info(f"First file: {rs_files_slot[0].split('/')[-1]}")
    logger.info(f"Last file: {rs_files_slot[-1].split('/')[-1]}")

    #First search corresponding DC measurement
    dc_path = measurement.path.parent / measurement.path.name.replace("RS", "DC")
    if dc_path.exists():
        dc_measurement = Measurement(
                type=MeasurementType('DC'),
                path=dc_path,
            )
        #logger with the DC measurement path
        logger.info(f"Coincident DC measurement path: {dc_measurement.path}")
    else:
        #otherwise, search for the nearest DC measurement in the same day
        dc_measurement = to_measurements(data_dir.glob("DC*"))[0]
        logger.info(f"Nearest not-coincident DC measurement path: {dc_measurement.path}")
    
    if dc_measurement.is_zip:
        dc_measurement.extract_zip()
        dc_files_patt = (dc_measurement.unzipped_path / '**' / "*.[0-9]*").as_posix()
    else:
        dc_files_patt =dc_measurement.path.as_posix()
    
    licel2scc.convert_to_scc(
        CustomLidarMeasurement,
        rs_files_slot,
        dc_files_patt,
        measurement_id,
        output_dir=nc_scc_dir,
    )

    #Check if the file was created
    if not (nc_scc_dir / f"{measurement_id}.nc").exists():
        raise ValueError("NC file was not created")

    #Upload to SCC
    scc_obj = scc_access.SCC(
        tuple(SCC_SERVER_SETTINGS["basic_credentials"]),
        SCC_SERVER_SETTINGS["output_dir"],
        SCC_SERVER_SETTINGS["base_url"],
    )

    measurement_exists, _ = check_measurement_id_in_scc(SCC_SERVER_SETTINGS, measurement_id)
    
    if not measurement_exists:
        scc_obj = scc_access.SCC( tuple(SCC_SERVER_SETTINGS["basic_credentials"]), None, SCC_SERVER_SETTINGS["base_url"], )
        scc_obj.login(SCC_SERVER_SETTINGS["website_credentials"]) 
        measurement_id_from_server = scc_obj.upload_file( filename=nc_scc_dir / f"{measurement_id}.nc", system_id=scc_id )
        scc_obj.logout()
        if not measurement_id_from_server:
            raise ValueError(f"{measurement_id} was not uploaded to SCC.")
        else:
            logger.info(f"{measurement_id} was uploaded to SCC with id {measurement_id_from_server}.")
    
    #Download products
    logger.info(f"Downloading products for {measurement_id} from SCC in {product_scc_dir}.")
    SCC_SERVER_SETTINGS['output_dir'] = product_scc_dir

    scc_obj = scc_access.SCC( tuple(SCC_SERVER_SETTINGS["basic_credentials"]), SCC_SERVER_SETTINGS["output_dir"], SCC_SERVER_SETTINGS["base_url"], )

    scc_obj.login(SCC_SERVER_SETTINGS["website_credentials"])
    _ = scc_obj.monitor_processing(measurement_id)

    scc_obj.logout()    


    #Plot scc products        
    for product in [*product_scc_dir.glob(f"*{measurement_id}*.zip")]:
        print(product.as_posix())
        try:
            scc_zip = SCC_zipfile(product)
        except Exception as e:
            print(e)                      
        scc_zip.plot(output_dir=plot_scc_dir, dpi=150, range_limits=(0, 10))

    assert True