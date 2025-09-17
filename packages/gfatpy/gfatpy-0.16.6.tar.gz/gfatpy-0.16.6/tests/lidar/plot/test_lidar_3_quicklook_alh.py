#!/usr/bin/env python
from datetime import datetime
from pathlib import Path

from gfatpy.lidar.plot.quicklook import (
    quicklook_from_date,
    quicklook_from_file,    
)

PRODUCTS_DIR = Path(r"./tests/datos/PRODUCTS/")

def test_quicklook_from_file_alhambra(linc_files):
    ALH_FL = Path(
        r"./tests/datos/PRODUCTS/alhambra/1a/2023/08/30/alh_1a_Prs_rs_xf_20230830_0315.nc"
    )
    if not ALH_FL.exists():
        raise FileNotFoundError(f"File {ALH_FL} does not exist")
    output_dir_ = PRODUCTS_DIR / "alhambra/quicklooks/1064fta"
    if not output_dir_.exists():
        output_dir_.mkdir(parents=True, exist_ok=True)

    channels = ["1064fta"]

    quicklook_from_file(
        ALH_FL, channels=channels, output_dir=output_dir_, scale_bounds=(0, 2.5e7)
    )

    output_file = output_dir_ / "quicklook_alh_1064fta_20230830_0315.png"

    assert output_file.exists()
