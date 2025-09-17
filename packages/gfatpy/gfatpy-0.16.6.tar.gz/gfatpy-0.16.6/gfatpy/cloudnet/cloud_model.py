import numpy as np
from typing import Any


def HM_model_retrieval(
    Z_linear: np.ndarray,
    delta_h: float,
    model: str = "knist_N",
    lwp: list = None,
    nu: float = 8.7,
    sigma: float = 0.29,
    CDNC: float | None = None,
) -> list[np.ndarray, np.ndarray, np.ndarray]:
    """HM (Cloud Model): Radar Reflectivity-Homogeneous Mixing

    Args:
        Z_linear (np.ndarray): 1D array linear reflectivity
        delta_h (float): resolution in meters
        model (str, optional): approach used. Options: 'knist' | 'frisch'. Defaults to 'knist'.
        lwp (list, optional): Liquid Water Path, Scalar [Required for Knist''s approach]. Defaults to None.
        nu (float, optional): parameter to determine the shape of the log normal distrubion [Required for Knist''s approach]. Defaults to 8.7.
        sigma (float, optional): parameter to determine the width of the the log normal distrubion [Required for Frisch''s approach]. Defaults to 0.29.
        CDNC (float | None, optional): cloud-droplet number concenctration [cm^{-3}] [Required for Frisch''s approach]. Defaults to None.

    Returns:
        list[np.ndarray, np.ndarray, np.ndarray]: [re, N, Opt_Depth]
            - re: Effective radius. 1D array. (in um)
            - N: Droplet concentration. Scalar. (in cm-3). It is CDNC for Frisch''s approach
            - Opt_Depth: Optical Depth (Adimensional). It is empty for Frisch''s approach

    """
    if model == "knist_lwp":
        if len(lwp) > 0:
            WATER_DENSITY = 1e6  # g/m3
            kre = np.power(
                ((nu + 2) ** 3) / ((nu + 3) * (nu + 4) * (nu + 5)), 1.0 / 3.0
            )
            knt = ((nu + 3) * (nu + 4) * (nu + 5)) / (nu * (nu + 1) * (nu + 2))

            Z_linear_root = np.sqrt(Z_linear)
            sumZroot = Z_linear_root.sum(dim="height", skipna=True, min_count=1)
            # effective radius in um
            try:
                re = (
                    kre
                    * (Z_linear ** (1.0 / 6.0))
                    * np.power(
                        (np.pi * WATER_DENSITY * sumZroot * delta_h) / (48 * lwp),
                        1.0 / 3.0,
                    )
                )  # (Eq. 2.57 Knist PhD dissertation) Identical to Frisch et al. 2002 with sigma_x = 0.29 (value from marine Sc, Martin et al 1994)
                re *= 1e6
                # re = substitute_nan(re)
            except:
                re = np.empty(Z_linear.shape)
                re[:] = np.nan
            # droplet concentration in cm-3
            try:
                # N = knt*((6*lwp)/(np.pi*WATER_DENSITY*delta_h*np.nansum(np.sqrt(Z_linear))))**2 #Andrea's version
                N = knt * (
                    (6 * lwp) / np.power(np.pi * WATER_DENSITY * delta_h * sumZroot, 2)
                )
                N *= 1e-6
            except:
                N = np.nan
            # COD
            try:
                Opt_Depth = (
                    (3.0 / (2.0 * kre))
                    * ((48 / np.pi) ** (1.0 / 3.0))
                    * (lwp / np.power(WATER_DENSITY * delta_h * sumZroot), 4.0 / 3.0)
                    * delta_h
                    * np.power(sumZroot, 1.0 / 3.0)
                )
            except:
                Opt_Depth = np.nan
        else:
            print("ERROR: Knist" "s approximation requires lwp array.")
    elif model == "knist_N":
        if CDNC:
            WATER_DENSITY = 1e6  # g/m3
            kre = np.power(
                np.power(nu + 2, 5) / (nu * (nu + 1) * (nu + 3) * (nu + 4) * (nu + 5)),
                1.0 / 6.0,
            )
            # effective radius in um
            try:
                re = (
                    0.5 * kre * np.power(Z_linear / (CDNC * 1e6), 1.0 / 6.0)
                )  # (Eq. 2.56 Knist PhD dissertation) Identical to Frisch et al. 2002 with sigma_x = 0.29 (value from marine Sc, Martin et al 1994)
                re *= 1e6
            except:
                re = np.empty(Z_linear.shape)
                re[:] = np.nan
            # droplet concentration in cm-3
            N = CDNC * np.ones(len(re))
            # COD
            Opt_Depth = np.nan * np.ones(len(re))
        else:
            print("ERROR: Knist_N approximation requires CDNC.")
    elif model == "frisch":
        if CDNC:
            Opt_Depth = []
            # effective radius in um
            try:
                re = (
                    0.5
                    * np.exp(-0.5 * sigma**2)
                    * np.power(Z_linear / (CDNC * 1e6), 1.0 / 6.0)
                )  # (Frisch et al., 2002)
                # re = 0.5*np.power(Z_linear/(CDNC*1e6),1./6.) #(Frisch et al., 2002)
                # re = 0.5*np.exp(-0.5*sigma**2)*np.power(Z_linear/(CDNC*1e6),1./6.) #(Frisch et al., 2002)
                # re = 0.5*sigma*np.power(Z_linear/(CDNC*1e6),1./6.) #(Frisch et al., 2002)
                re *= 1e6
                # re = substitute_nan(re)
            except:
                re = np.empty(Z_linear.shape)
                re[:] = np.nan
            N = CDNC * np.ones(len(re))
        else:
            print("ERROR: Frisch" "s approximation requires lwp array.")
    return re, N, Opt_Depth


def LWC_model_HM(
    Z_linear: np.ndarray, LWP: float, delta_h: float
) -> np.ndarray[Any, np.dtype[np.float64]]:
    """HM (Cloud Model): Radar Reflectivity-Homogeneous Mixing

    Args:
        Z_linear (np.ndarray): linear reflectivity.
        LWP (float):Liquid Water Path.
        delta_h (float): resolution in meters.

    Returns:
        np.ndarray[Any, np.dtype[np.float64]]: Liquid Water Content in g/m^2.
    """
    Z_linear_root = np.sqrt(Z_linear)
    sumZroot = Z_linear_root.sum(dim="height", skipna=True, min_count=1)
    LWC = LWP * (Z_linear_root / (sumZroot * delta_h))
    return LWC


def VU_model_retrieval(
    linear_Z: np.ndarray, lwp: np.ndarray, delta_H: np.ndarray, nu: float = 8.7
) -> list[np.ndarray]:
    """Vertical Uniform Model.

    Args:
        linear_Z (np.ndarray): linear reflectivity in m^3
        lwp (np.ndarray): Liquid Water Path in g·m^-2
        delta_H (np.ndarray): cloud thickness (m)
        nu (float, optional): droplet distribution parameter. Defaults to 8.7.

    Returns:
        list[np.ndarray]: [re, N, Opt_Depth]
            - re: Effective radius (in um)
            - N: Droplet concentration (in cm-3)
            - Opt_Depth: Optical Depth (Adimensional)
    """

    WATER_DENSITY = 1e6  # g/m3
    kre = ((nu + 2) ** 3 / ((nu + 3) * (nu + 4) * (nu + 5))) ** (1.0 / 3.0)
    knt = (nu + 3) * (nu + 4) * (nu + 5) / (nu * (nu + 1) * (nu + 2))

    # effective radius in um
    try:
        re = kre * ((np.pi * WATER_DENSITY * delta_H * linear_Z) / (48 * lwp)) ** (
            1.0 / 3.0
        )
        re *= 1e6
    except:
        re = np.nan

    # droplet concentration in cm-3
    try:
        N = (knt / linear_Z) * ((6 * lwp) / (np.pi * WATER_DENSITY * delta_H)) ** 2
        N *= 1e-6
    except:
        N = np.nan

    # optical depth (adimensional)
    try:
        Opt_Depth = (3.0 / 2.0) * (lwp / (WATER_DENSITY * (re / 1000000)))

    except:
        Opt_Depth = np.nan

    return re, N, Opt_Depth


def SAS_model_retrieval(
    Z_avg_linear: np.ndarray,
    lwp: float,
    height: np.ndarray,
    delta_H: float,
    nu: float = 8.7,
) -> list[np.ndarray, np.ndarray, np.ndarray]:
    """SCALED ADIABATIC STRATIFIED CLOUD MODEL

    Args:
        Z_avg_linear (np.ndarray): linear) Z in cloud for each profile
        lwp (float): liquid water path in g·m^-2
        height (np.ndarray): height in m.
        delta_H (float): cloud thickness (m)
        nu (float, optional): droplet distribution parameter. Defaults to 8.7.

    Returns:
        list[np.ndarray, np.ndarray, np.ndarray]: [re, N, Opt_Depth]
            - re: Effective radius (in um)
            - N: Droplet concentration (in cm-3)
            - Opt_Depth: Optical Depth (Adimensional)
    """

    WATER_DENSITY = 1000000  # g/m3
    kre = ((nu + 2) ** 3 / ((nu + 3) * (nu + 4) * (nu + 5))) ** (1.0 / 3.0)
    knt = (nu + 3) * (nu + 4) * (nu + 5) / (nu * (nu + 1) * (nu + 2))

    # effective radius in um

    try:
        re = (
            height ** (1.0 / 3.0)
            * kre
            * ((np.pi * WATER_DENSITY * Z_avg_linear) / (32 * lwp)) ** (1.0 / 3.0)
        )  # um
        re *= 1e6
    except:
        re = np.nan

    # Maximum radius
    re_max = np.nanmax(re)

    # Optical_Depth (adimensional)
    try:
        Opt_Depth = (9.0 / 5.0) * (lwp / (WATER_DENSITY * (re_max / 1000000)))
    except:
        Opt_Depth = np.nan

    # droplet concentration in cm-3
    try:
        N = (
            (4.0 / 3.0)
            * (knt / Z_avg_linear)
            * ((6 * lwp) / (np.pi * WATER_DENSITY * delta_H)) ** 2
        )
        N *= 1e-6
    except:
        N = np.nan

    return re, N, Opt_Depth
