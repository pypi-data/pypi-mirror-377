import numpy as np

from datetime import datetime

from gfatpy.aeronet.reader import reader
from gfatpy.aeronet import typing
from gfatpy.aeronet import utils

FILEPATH = r"./tests/datos/aeronet/20200701_20200801_Granada.all"
HEADER_ALL, AERONET_ALL = reader(FILEPATH)
FILEPATH_LEV15 = r"./tests/datos/aeronet/20200701_20200801_Granada.lev15"
HEADER_LEV15, AERONET_LEV15 = reader(FILEPATH_LEV15)
FILEPATH_ONEILL_LEV15 = r"./tests/datos/aeronet/20200701_20200801_Granada.ONEILL_lev15"
HEADER_ONEILL_LEV15, AERONET_ONEILL_LEV15 = reader(FILEPATH_ONEILL_LEV15)


def test_distribution_to_total_concentration():
    aeronet_all = utils.distribution_to_total_concentration(
        AERONET_ALL, concentration_type="number", reference_radius_nm=100
    )
    assert "number_concentration_above_100" in aeronet_all.keys()


def test_add_logAOD():
    aeronet_all = utils.add_logAOD(HEADER_ALL, AERONET_ALL)
    assert "lnAOD440" in aeronet_all.keys()


def test_resample_logradius_distribution():
    idx_min = AERONET_ALL.columns.get_loc("0.050000")
    idx_max = AERONET_ALL.columns.get_loc("15.000000")

    assert type(idx_min) == int and type(idx_max) == int

    dV_dlnr = AERONET_ALL.iloc[0, np.arange(idx_min, idx_max + 1)]  # VSD um^3/um^2
    (
        resample_distribution,
        resample_radius,
        resample_lnr,
        resample_resol_lnr,
    ) = utils.resample_logradius_distribution(dV_dlnr)
    assert np.round(resample_resol_lnr, 4) == np.round(np.diff(resample_lnr)[0], 4)
    assert len(resample_distribution) == 211


def test_calculate_fine_mode_fraction():
    fmf = utils.calculate_fine_mode_fraction(
        AERONET_ALL["AOD_Extinction-Fine[440nm]"],
        AERONET_ALL["AOD_Extinction-Total[440nm]"],
    )
    assert len(fmf) > 0
    assert not (fmf > 1).any()
    assert type(AERONET_ALL["AOD_Extinction-Total[440nm]"]) == type(fmf)


def test_filter_df():
    # Add Lee's typing
    fine440 = AERONET_ALL["AOD_Extinction-Fine[440nm]"]
    total440 = AERONET_ALL["AOD_Extinction-Total[440nm]"]
    fmf440 = utils.calculate_fine_mode_fraction(fine440, total440)
    ssa440 = AERONET_ALL["Single_Scattering_Albedo[440nm]"]
    lee_typing = typing.aerosol_typing_Lee(fmf440, ssa440)
    typing_df = AERONET_ALL.copy()
    typing_df["aerosol_type"] = lee_typing

    # Add mode's typing
    ae_440_870 = AERONET_ALL[
        "Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD"
    ].values.astype(float)
    mode_typing = typing.mode_predominance_typing(ae_440_870)
    typing_df["mode_predominance"] = mode_typing
    dust_df = utils.filter_df(typing_df, {"aerosol_type": "DUST"})
    highlyCoarse_df = utils.filter_df(typing_df, {"mode_predominance": "HIGHLY_COARSE"})
    highlyCoarse_to_dust_df = utils.filter_df(
        dust_df, {"mode_predominance": "HIGHLY_COARSE"}
    )
    once_highlyCoarse_dust_df = utils.filter_df(
        typing_df, {"aerosol_type": "DUST", "mode_predominance": "HIGHLY_COARSE"}
    )
    assert len(dust_df) == 8
    assert len(highlyCoarse_df) == 2
    assert len(once_highlyCoarse_dust_df) == len(highlyCoarse_to_dust_df)


def test_find_aod_in_all():
    target_datetime = datetime(2020, 7, 1, 8, 0, 15)
    found_aod, measure_datetime = utils.find_aod(
        HEADER_ALL, AERONET_ALL, 532, target_datetime, allowed_time_gap_hour=0.5
    )
    assert found_aod != None
    assert measure_datetime != None
    assert np.round(found_aod, 5) == 0.06754
    assert (measure_datetime - target_datetime).total_seconds() == 840


def test_find_aod_in_lev15():
    target_datetime = datetime(2020, 7, 1, 8, 0, 15)
    found_aod, measure_datetime = utils.find_aod(
        HEADER_LEV15, AERONET_LEV15, 532, target_datetime, allowed_time_gap_hour=0.5
    )
    assert found_aod != None
    assert measure_datetime != None
    assert np.round(found_aod, 5) == 0.06732
    assert (measure_datetime - target_datetime).total_seconds() == 783


def test_find_aod_in_oneill_lev15():
    target_datetime = datetime(2020, 7, 1, 8, 0, 15)
    found_aod, measure_datetime = utils.find_aod(
        HEADER_ONEILL_LEV15,
        AERONET_ONEILL_LEV15,
        532,
        target_datetime,
        allowed_time_gap_hour=0.5,
    )
    assert found_aod != None
    assert measure_datetime != None
    assert np.round(found_aod, 5) == 0.06732
    assert (measure_datetime - target_datetime).total_seconds() == 783
