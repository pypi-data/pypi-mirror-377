from datetime import datetime
import os
import pathlib

import numpy as np

from gfatpy.aeronet.reader import reader
from gfatpy.aeronet import plot

FILEPATH = r"./tests/datos/aeronet/20200701_20200801_Granada.all"
HEADER_ALL, AERONET_ALL = reader(FILEPATH)
FILEPATH = r"./tests/datos/aeronet/20200701_20200801_Granada.lev15"
HEADER_LEV15, AERONET_LEV15 = reader(FILEPATH)

KEEP_FIGURE = True


def test_aeronet_distribution_date():
    # date_dt = datetime(2020, 7, 15)
    date_str = "2020-07-01"
    figure_dir = r"./tests/datos/aeronet/plots"
    _, _, figurepath = plot.distribution(AERONET_ALL, date_str, figure_dir=figure_dir)
    if isinstance(figurepath, str):
        assert pathlib.Path(figurepath).is_file()
        if not KEEP_FIGURE:
            os.remove(figurepath)


def test_distribution_serie():
    date_str = ["2020-07-01", "2020-07-02", "2020-07-03"]
    figure_dir = r"./tests/datos/aeronet/plots"
    _, axes_list, figurepath_list = plot.distribution(
        AERONET_ALL, date_str, figure_dir=figure_dir
    )
    if isinstance(axes_list, list):
        assert np.array(
            [
                axes_list[0].get_ylim()[-1] == 0.2,
                axes_list[1].get_ylim()[-1] == 0.2,
                axes_list[2].get_ylim()[-1] == 0.2,
            ]
        ).all()
    if isinstance(figurepath_list, list):
        assert pathlib.Path(figurepath_list[0]).is_file()
        assert pathlib.Path(figurepath_list[1]).is_file()
        assert pathlib.Path(figurepath_list[2]).is_file()
    if not KEEP_FIGURE:
        for file_ in figurepath_list:
            os.remove(file_)


def test_aod_from_all_dates():
    properties2plot = [
        key_ for key_ in AERONET_ALL.keys() if key_.find("AOD_Coincident") != -1
    ]
    figure_dir = r"./tests/datos/aeronet/plots"
    _, _, figure_pathname = plot.aod(
        AERONET_ALL,
        HEADER_ALL,
        properties2plot,
        datetime(2020, 7, 1),
        datetime(2020, 7, 3),
        figure_dir=figure_dir,
    )
    assert pathlib.Path(figure_pathname).is_file()
    if not KEEP_FIGURE:
        os.remove(figure_pathname)


def test_aod_from_lev15_dates():
    properties2plot = [
        key_
        for key_ in AERONET_LEV15.keys()
        if key_.find("AOD_") != -1 and not (AERONET_LEV15[key_].values == -999).all()
    ]
    figure_dir = r"./tests/datos/aeronet/plots"
    _, _, figure_pathname = plot.aod(
        AERONET_LEV15,
        HEADER_LEV15,
        properties2plot,
        datetime(2020, 7, 1),
        datetime(2020, 7, 7),
        figure_dir=figure_dir,
    )
    assert pathlib.Path(figure_pathname).is_file()
    if not KEEP_FIGURE:
        os.remove(figure_pathname)
