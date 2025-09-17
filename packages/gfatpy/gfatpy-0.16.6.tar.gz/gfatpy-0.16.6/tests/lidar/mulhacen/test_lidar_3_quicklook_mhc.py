#!/usr/bin/env python
from datetime import datetime
from pathlib import Path

from gfatpy.lidar.plot.quicklook import (
    quicklook_from_date,
)

PRODUCTS_DIR = Path(r"./tests/datos/PRODUCTS/")


def test_quicklook_mulhacen(linc_files):
    output_dir_ = PRODUCTS_DIR / "mulhacen" / "quicklooks" / "1064xta"
    if not output_dir_.exists():
        output_dir_.mkdir(parents=True, exist_ok=True)
    paths = quicklook_from_date(
        lidar_name="mulhacen",
        channels=["1064xta"],
        target_date=datetime(2022, 8, 8),
        product_dir=PRODUCTS_DIR,
        output_dir=output_dir_,
        scale_bounds="from_info",        
    )
    assert isinstance(paths, list)    
    assert paths[0].exists()
    
