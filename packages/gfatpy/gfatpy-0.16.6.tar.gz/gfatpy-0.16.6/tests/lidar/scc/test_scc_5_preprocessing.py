from pathlib import Path

from gfatpy.lidar.scc.plot.scc_zip import SCC_zipfile
from gfatpy.lidar.scc.plot.product import SCC_raw

scc_id = 781
SCC_DIR = Path(f"./tests/datos/PRODUCTS/alhambra/scc/scc{scc_id}/2023/08/30/products")
OUTPUT_DIR = Path(f"./tests/datos/PRODUCTS/alhambra/scc/scc{scc_id}/2023/08/30/plots")

def test_scc_raw_preprocessing():
    scc_zipfile = SCC_DIR / "raw_20230830gra0315.zip"
    scc_zip = SCC_zipfile(scc_zipfile)
    scc_file = scc_zip.products[0]
    
    assert isinstance(scc_file, SCC_raw)

    if isinstance(scc_file, SCC_raw):    
        data = scc_file.scc_preprocessing()        
    assert any(['Raw_Lidar_Data_dc' in data.variables.keys()])
    data.close()
    
    