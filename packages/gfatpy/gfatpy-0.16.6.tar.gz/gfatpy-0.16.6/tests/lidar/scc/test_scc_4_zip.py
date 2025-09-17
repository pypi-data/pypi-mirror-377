from datetime import datetime
from pathlib import Path
from gfatpy.lidar.scc.plot.product import SCC_elpp

from gfatpy.lidar.scc.plot.scc_zip import SCC_zipfile

scc_id = 781
SCC_DIR = Path(f"./tests/datos/PRODUCTS/alhambra/scc/scc{scc_id}/2023/08/30/products")
OUTPUT_DIR = Path(f"./tests/datos/PRODUCTS/alhambra/scc/scc{scc_id}/2023/08/30/plots")

def test_scc_zip_elpp():
    scc_zipfile = SCC_DIR / "preprocessed_20230830gra0315.zip"

    scc_zip = SCC_zipfile(scc_zipfile)
    assert scc_zip.type == "elpp"
    assert scc_zip.measurementID == "20230830gra0315"
    assert len(scc_zip.products) == 11
    assert type(scc_zip.products[0]) == SCC_elpp
    assert scc_zip.products[0].measurementID == "20230830gra0315"
    assert scc_zip.products[0].station == "gra"
    assert scc_zip.products[0].number1 == 0
    assert scc_zip.products[0].productID == 2365
    assert scc_zip.products[0].datetime_ini == datetime(2023, 8, 30, 3, 14, 0)
    assert scc_zip.products[0].datetime_end == datetime(2023, 8, 30, 3, 44, 0)
    assert scc_zip.products[0].type == "elpp"
    