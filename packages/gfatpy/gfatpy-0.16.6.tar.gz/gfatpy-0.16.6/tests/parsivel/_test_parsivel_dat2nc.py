import os
import xarray as xr
from pathlib import Path

import rpgpy

from gfatpy.parsivel.converter import raw2nc

DSD_FILE = Path(r"tests\datos\RAW\parsivel\2023\parsivel_20231211.dat")
DSD_NC = Path(r"tests\datos\PRODUCTS\parsivel\2023\parsivel_20231211.nc")


DSD_NC.parent.mkdir(parents=True, exist_ok=True)


def test_rpgpy_to_netcdf():

    if DSD_NC.exists() and DSD_NC.is_file():
        os.remove(DSD_NC)
    raw2nc([DSD_FILE], DSD_NC.parent)

    data = xr.open_dataset(DSD_NC, decode_cf=True)

    assert "time" in data.variables
    assert data.dims.get("time") == 10069
    assert "droplet_number_concentration" in data.variables
    assert data.droplet_number_concentration.attrs["units"] == "cm-3"
