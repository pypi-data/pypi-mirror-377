from gfatpy.aeronet.reader import reader
from gfatpy.aeronet import typing
from gfatpy.aeronet import utils

FILEPATH = r"./tests/datos/aeronet/20200701_20200801_Granada.all"
_, AERONET_DF = reader(FILEPATH)


def test_lee():
    # Add Lee's typing
    fine440 = AERONET_DF["AOD_Extinction-Fine[440nm]"]
    total440 = AERONET_DF["AOD_Extinction-Total[440nm]"]
    fmf440 = utils.calculate_fine_mode_fraction(fine440, total440)
    ssa440 = AERONET_DF["Single_Scattering_Albedo[440nm]"]
    lee_typing = typing.aerosol_typing_Lee(fmf440, ssa440)
    assert sum(lee_typing == "DUST") == 8
    assert sum(lee_typing == "MIXTURE") == 15
    assert sum(lee_typing == "HA") == 6
    assert sum(lee_typing == "MA") == 10
    assert sum(lee_typing == "SA") == 4
    assert sum(lee_typing == "NA") == 13
    assert len(lee_typing) == 56


def test_mode():
    # Add mode's typing
    ae_440_870 = AERONET_DF[
        "Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD"
    ].values.astype(float)
    mode_typing = typing.mode_predominance_typing(ae_440_870)
    assert sum(mode_typing == "HYGHLY_COARSE") == 0
    assert sum(mode_typing == "COARSE") == 17
    assert sum(mode_typing == "BIMODAL") == 34
    assert sum(mode_typing == "FINE") == 3
    assert sum(mode_typing == "HIGHLY_FINE") == 0
    assert sum(mode_typing == "UNKNOWN") == 0
    assert len(mode_typing) == 56
