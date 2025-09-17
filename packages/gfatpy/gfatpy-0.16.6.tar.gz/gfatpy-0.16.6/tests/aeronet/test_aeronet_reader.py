#!/usr/bin/env python
import pandas as pd


from gfatpy.aeronet.reader import reader, header

FILEPATH = r"./tests/datos/aeronet/20200701_20200801_Granada.all"
FILEPATH = r"./tests/datos/aeronet/20200701_20200801_Granada.all"
FILEPATH_LEV15 = r"./tests/datos/aeronet/20200701_20200801_Granada.lev15"
FILEPATH_ONEILL_LEV15 = r"./tests/datos/aeronet/20200701_20200801_Granada.ONEILL_lev15"


def test_reader_all():
    _, aeronet_all = reader(FILEPATH)
    assert type(aeronet_all) == pd.DataFrame and len(aeronet_all) == 56


def test_reader_lev15():
    _, aeronet_lev15 = reader(FILEPATH_LEV15)
    assert type(aeronet_lev15) == pd.DataFrame and len(aeronet_lev15) == 222


def test_reader_ONEILL_lev15():
    _, aeronet_ONEILL_lev15 = reader(FILEPATH_ONEILL_LEV15)
    assert (
        type(aeronet_ONEILL_lev15) == pd.DataFrame and len(aeronet_ONEILL_lev15) == 222
    )


def test_reader_header_all():
    header_all = header(FILEPATH)
    assert header_all["aeronet_data"] == "Almucantar Level 1.5 Inversion"


def test_reader_header_lev15():
    header_lev15 = header(FILEPATH_LEV15)
    assert header_lev15["aeronet_data"] == "AOD Level 1.5"


def test_reader_header_oneill_lev15():
    header_oneill_lev15 = header(FILEPATH_ONEILL_LEV15)
    assert header_oneill_lev15["aeronet_data"] == "SDA Retrieval Level 1.5"
