import numpy as np
import pandas as pd
from typing import Any
from loguru import logger


# TODO: verificar que aerosol_typing_Lee y aerosol_typing son iguales y fusionarlos.
def aerosol_typing_Lee(
    fmf_550: np.ndarray | pd.Series, ssa_440: np.ndarray | pd.Series
) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Typing according to Lee's method.

    Args:

        - fmf_550 (np.ndarray): fine mode fraction at 550nm.
        - ssa_440 (np.ndarray): single scattering albedo at 440nm.

    Raises:

        - ValueError: Length of inputs must be identical.

    Returns:

        - aerosol_type (np.ndarray[str]): aerosol types [MIXTURE, DUST, HA, MA, SA]
    
    References:
        - Lee et al., 2010.
    """

    if len(fmf_550) != len(ssa_440):
        logger.error("Length of inputs must be identical.")
        raise ValueError

    n = len(fmf_550)
    aerosol_type = ["MIXTURE"] * n

    # DUST
    fmfmin_threshold, fmfmax_threshold = 0, 0.4
    ssamin_threshold, ssamax_threshold = 0.0, 0.95
    dust_condition = np.logical_and.reduce(
        (
            ssa_440 > ssamin_threshold,
            ssa_440 < ssamax_threshold,
            fmf_550 > fmfmin_threshold,
            fmf_550 < fmfmax_threshold,
        )
    )
    aerosol_type = np.where(dust_condition, "DUST", aerosol_type)
    # HA
    fmfmin_threshold, fmfmax_threshold = 0.6, 1.0
    ssamin_threshold, ssamax_threshold = 0.0, 0.85
    ha_condition = np.logical_and.reduce(
        (
            ssa_440 > ssamin_threshold,
            ssa_440 < ssamax_threshold,
            fmf_550 > fmfmin_threshold,
            fmf_550 < fmfmax_threshold,
        )
    )
    aerosol_type = np.where(ha_condition, "HA", aerosol_type)

    # MA
    fmfmin_threshold, fmfmax_threshold = 0.6, 1.0
    ssamin_threshold, ssamax_threshold = 0.85, 0.90
    ma_condition = np.logical_and.reduce(
        (
            ssa_440 > ssamin_threshold,
            ssa_440 < ssamax_threshold,
            fmf_550 > fmfmin_threshold,
            fmf_550 < fmfmax_threshold,
        )
    )
    aerosol_type = np.where(ma_condition, "MA", aerosol_type)

    # SA
    fmfmin_threshold, fmfmax_threshold = 0.6, 1.0
    ssamin_threshold, ssamax_threshold = 0.9, 0.95
    sa_condition = np.logical_and.reduce(
        (
            ssa_440 > ssamin_threshold,
            ssa_440 < ssamax_threshold,
            fmf_550 > fmfmin_threshold,
            fmf_550 < fmfmax_threshold,
        )
    )
    aerosol_type = np.where(sa_condition, "SA", aerosol_type)

    # NA
    fmfmin_threshold, fmfmax_threshold = 0.6, 1.0
    ssamin_threshold, ssamax_threshold = 0.95, 1.0
    na_condition = np.logical_and.reduce(
        (
            ssa_440 > ssamin_threshold,
            ssa_440 < ssamax_threshold,
            fmf_550 > fmfmin_threshold,
            fmf_550 < fmfmax_threshold,
        )
    )
    aerosol_type = np.where(na_condition, "NA", aerosol_type)
    return aerosol_type


def aerosol_typing(df: pd.DataFrame):
    """Aerosol typing according to Lee's method.

    Args:

        - df (pd.DataFrame): DataFrame load from aeronet file.

    Returns:

        - df (pd.DataFrame): DataFrame with new column "aeronet_type". Aerosol types [MIXTURE, DUST, HA, MA, SA]
    
    References:

        - Lee, J., Kim, J., Song, C. H., Kim, S. B., Chun, Y., Sohn, B. J., &#38; Holben, B. N. (2010).
    Characteristics of aerosol types from AERONET sunphotometer measurements. <i>Atmospheric Environment</i>, <i>44</i>(26),
    3110–3117. https://doi.org/10.1016/j.atmosenv.2010.05.035</div>
    """

    df["aerosol_type"] = "MIXTURE"

    # DUST
    fmfmin_threshold, fmfmax_threshold, ssamin_threshold, ssamax_threshold = (
        0,
        0.4,
        0.0,
        0.95,
    )
    dust_condition = np.logical_and.reduce(
        (
            df["Single_Scattering_Albedo[440nm]"] > ssamin_threshold,
            df["Single_Scattering_Albedo[440nm]"] <= ssamax_threshold,
            df["FMF"] > fmfmin_threshold,
            df["FMF"] < fmfmax_threshold,
        )
    )
    df.loc[dust_condition, "aerosol_type"] = "DUST"

    # NA
    fmfmin_threshold, fmfmax_threshold, ssamin_threshold, ssamax_threshold = (
        0.6,
        1.0,
        0.95,
        1.0,
    )
    na_condition = np.logical_and.reduce(
        (
            df["Single_Scattering_Albedo[440nm]"] > ssamin_threshold,
            df["Single_Scattering_Albedo[440nm]"] < ssamax_threshold,
            df["FMF"] > fmfmin_threshold,
            df["FMF"] < fmfmax_threshold,
        )
    )
    df.loc[na_condition, "aerosol_type"] = "NA"

    # HA
    fmfmin_threshold, fmfmax_threshold, ssamin_threshold, ssamax_threshold = (
        0.6,
        1.0,
        0.0,
        0.85,
    )
    ha_condition = np.logical_and.reduce(
        (
            df["Single_Scattering_Albedo[440nm]"] > ssamin_threshold,
            df["Single_Scattering_Albedo[440nm]"] < ssamax_threshold,
            df["FMF"] > fmfmin_threshold,
            df["FMF"] < fmfmax_threshold,
        )
    )
    df.loc[ha_condition, "aerosol_type"] = "HA"
    # SA
    fmfmin_threshold, fmfmax_threshold, ssamin_threshold, ssamax_threshold = (
        0.6,
        1.0,
        0.9,
        0.95,
    )
    sa_condition = np.logical_and.reduce(
        (
            df["Single_Scattering_Albedo[440nm]"] > ssamin_threshold,
            df["Single_Scattering_Albedo[440nm]"] <= ssamax_threshold,
            df["FMF"] > fmfmin_threshold,
            df["FMF"] < fmfmax_threshold,
        )
    )
    df.loc[sa_condition, "aerosol_type"] = "SA"

    df["mode_predominance"] = "MIXTURE"

    # COARSE
    aemax_threshold = 0.6
    coarse_condition = (
        df["Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD"] <= aemax_threshold
    )
    df.loc[coarse_condition, "mode_predominance"] = "COARSE"

    # HIGHLY COARSE
    aemax_threshold = 0.2
    hcoarse_condition = (
        df["Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD"] <= aemax_threshold
    )
    df.loc[hcoarse_condition, "mode_predominance"] = "HIGHLY_COARSE"

    # NONE
    aemin_threshold, aemax_threshold = 0.6, 1.4
    none_condition = np.logical_and(
        df["Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD"] > aemin_threshold,
        df["Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD"] < aemax_threshold,
    )
    df.loc[none_condition, "mode_predominance"] = "NONE"

    # FINE
    aemin_threshold = 1.4
    fine_condition = (
        df["Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD"] >= aemin_threshold
    )
    df.loc[fine_condition, "mode_predominance"] = "FINE"

    # HIGHLY_FINE
    aemin_threshold = 1.8
    fine_condition = (
        df["Angstrom_Exponent_440-870nm_from_Coincident_Input_AOD"] >= aemin_threshold
    )
    df.loc[fine_condition, "mode_predominance"] = "HIGHLY_FINE"
    return df


def mode_predominance_typing(
    ae_440_870: np.ndarray | pd.Series,
) -> np.ndarray | pd.Series:
    """Typing according to the mode predominance.

    Args:

        - ae_440_870 (np.ndarray): Angstrom exponent between 440 and 870 nm.
    
    Returns:
    
        - mode_predominance (np.ndarray[str]): aerosol typing according to mode predominance in the volume particle distribution [HYGHLY_COARSE, COARSE, BIMODAL, FINE, HIGHLY_FINE, UNKNOWN]
    """

    try:
        n = len(ae_440_870)
        mode_predominance = ["UNKNOWN"] * n

        # COARSE
        aemin_threshold, aemax_threshold = 0.2, 0.6
        coarse_condition = np.logical_and(
            ae_440_870 > aemin_threshold, ae_440_870 <= aemax_threshold
        )
        mode_predominance = np.where(coarse_condition, "COARSE", mode_predominance)

        # HIGHLY COARSE
        aemin_threshold, aemax_threshold = -1000.0, 0.2
        hcoarse_condition = np.logical_and(
            ae_440_870 >= aemin_threshold, ae_440_870 <= aemax_threshold
        )
        mode_predominance = np.where(
            hcoarse_condition, "HIGHLY_COARSE", mode_predominance
        )

        # NONE
        aemin_threshold, aemax_threshold = 0.6, 1.4
        none_condition = np.logical_and(
            ae_440_870 >= aemin_threshold, ae_440_870 <= aemax_threshold
        )
        mode_predominance = np.where(none_condition, "BIMODAL", mode_predominance)

        # FINE
        aemin_threshold, aemax_threshold = 1.4, 1.8
        fine_condition = np.logical_and(
            ae_440_870 >= aemin_threshold, ae_440_870 < aemax_threshold
        )
        mode_predominance = np.where(fine_condition, "FINE", mode_predominance)

        # HIGHLY FINE
        aemin_threshold, aemax_threshold = 1.8, 1000.0
        hfine_condition = np.logical_and(
            ae_440_870 >= aemin_threshold, ae_440_870 < aemax_threshold
        )
        mode_predominance = np.where(hfine_condition, "HIGHLY_FINE", mode_predominance)
    except Exception as e:
        logger.error("Mode Predominance not Calculated")
        mode_predominance = None

    return mode_predominance
