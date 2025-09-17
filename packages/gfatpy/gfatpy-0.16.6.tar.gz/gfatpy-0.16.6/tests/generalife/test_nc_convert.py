from datetime import date
from pathlib import Path

from gfatpy.lidar.nc_convert.measurement import info2measurements
from gfatpy.generalife.io import measurement_to_nc

RAW_DIR = Path(r".\tests\datos\RAW")
OUTPUT_DIR = Path(r".\tests\datos\PRODUCTS")

def test_to_measurements():
    data_dir = RAW_DIR / "generalife" / "2024" / "05" / "20"
    
    measurements = info2measurements(lidar_name="generalife", target_date=date(2024,5,20), raw_dir=RAW_DIR)
    
    # Crear directorios faltantes
    output_path = OUTPUT_DIR / "generalife" / "1a" / "2024" / "05" / "20" / "gnl_1a_Prs_rs_xf_20240520_0910.nc"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # measurements_to_nc(measurements, lidar_name=LidarName.gnl, raw_dir=RAW_DIR, output_dir=OUTPUT_DIR)
    assert isinstance(measurements, list)
    measurements[0].to_nc(output_dir=OUTPUT_DIR)

    assert output_path.exists()