from pathlib import Path
import xarray as xr

# from gfatpy.radar.rpg import rpg
from gfatpy.radar.rpg_binary import rpg

ZEN_LV0 = Path(r"tests\datos\RAW\nebula_ka\2024\03\13\240313_150001_P00_ZEN.LV0")

def test_init_zen():
    radar = rpg(ZEN_LV0)
    raw = radar.raw
    header = radar.header

    assert radar.type == "ZEN"
    assert isinstance(raw, dict)
    assert isinstance(header, dict)

def test_load_data():
    radar = rpg(ZEN_LV0)    
    data = radar.dataset
    assert isinstance(data, xr.Dataset)
