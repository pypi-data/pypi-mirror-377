import pathlib
import numpy as np
import pandas as pd
from datetime import datetime
from scipy import integrate
from scipy.interpolate import interp1d
from loguru import logger

from gfatpy.utils.io import read_yaml
from gfatpy.utils.utils import parse_datetime

# AERONET SYSTEM INFO
AERONET_INFO_FILE = pathlib.Path(__file__).parent.absolute() / "info.yml"
AERONET_INFO = read_yaml(AERONET_INFO_FILE)


def find_available_aod_wavelengths(header: dict, df: pd.DataFrame) -> list:
    """find available aod wavelengths in AERONET dataframe.

    Args:
        - header (dict): AERONET header
        - df (pd.DataFrame): AERONET dataframe
    Returns:
        - list[int]: available wavelenghts
    """

    available_wavelengths = []
    aeronet_data = header["aeronet_data"].replace(" ", "_")
    for wave_ in AERONET_INFO["wavelengths"][aeronet_data]:
        property2check = AERONET_INFO["aod_string_type"][aeronet_data].replace(
            "&", f"{wave_}"
        )
        if property2check in df.keys():
            available_wavelengths.append(wave_)
    available_wavelengths = np.sort(np.asarray(available_wavelengths)).tolist()
    return available_wavelengths


def find_nearest_wavelength(
    header: dict, df: pd.DataFrame, target_wavelength: float
) -> tuple[float, float]:
    """Find the available wavelength above [`larger_wavelength`] and below [`lower_wavelength`] of the `target_wavelength`.

    Args:
        - header (dict): AERONET header.
        - df (pd.DataFrame): AERONET dataframe.
        - target_wavelength (float): wavelength to be interpolated.

    Returns:
        - list[float]: lower_wavelength, larger_wavelength
    """

    available_wavelengths = find_available_aod_wavelengths(header, df)
    idx_to_be_placed = np.searchsorted(
        available_wavelengths, [target_wavelength], side="left"
    )[0]
    if idx_to_be_placed == 0:  # Extrapolation is required
        bottom_wave = available_wavelengths[0]
        up_wave = available_wavelengths[1]
    elif idx_to_be_placed == len(available_wavelengths):  # Extrapolation is required
        bottom_wave = available_wavelengths[-2]
        up_wave = available_wavelengths[-1]
    else:
        bottom_wave = available_wavelengths[idx_to_be_placed - 1]
        up_wave = available_wavelengths[idx_to_be_placed + 1]
    return bottom_wave, up_wave


def add_interpol_aod(
    header: dict,
    df: pd.DataFrame,
    target_wavelength: int,
    bottom_wavelength: float | None = None,
    up_wavelength: float | None = None,
    allow_search: bool = True,
) -> pd.DataFrame:
    """Add the interpolated aod of `target_wavelength` to the AERONET dataframe.

    Args:

        - header (dict): AERONET header.
        - df (pd.DataFrame): AERONET dataframe.
        - target_wavelength (int): Target wavelength
        - bottom_wavelength (int | None, optional): lower wavelength to make the interpolation. Defaults to None. With None, the nearest lower wavelength available is used.
        - up_wavelength (int | None, optional): lower wavelength to make the interpolation. Defaults to None. With None, the nearest larger wavelength available is used.
        - allow_search (bool | optional): allow to search the best lower and larger wavelength if the provided are not available.
    
    Returns:

        - pd.DataFrame: AERONET dataframe with new interpolated AOD at `target_wavelength`.

    Raises:

        - ValueError: Interpolation not possible since bottom/up wavelengths are not available.
    """
    available_wavelengths = find_available_aod_wavelengths(header, df)

    if (
        bottom_wavelength not in available_wavelengths
        or up_wavelength not in available_wavelengths
    ) and allow_search is False:
        logger.error(
            "Interpolation not possible since bottom/up wavelengths are not available."
        )
        raise ValueError

    if bottom_wavelength is None or up_wavelength is None:
        bottom_wavelength, up_wavelength = find_nearest_wavelength(
            header, df, target_wavelength
        )
    # Property strings
    bottom_property = AERONET_INFO["aod_string_type"][
        header["aeronet_data"].replace(" ", "_")
    ].replace("&", f"{bottom_wavelength}")

    up_property = AERONET_INFO["aod_string_type"][
        header["aeronet_data"].replace(" ", "_")
    ].replace("&", f"{up_wavelength}")

    target_property = bottom_property.replace(
        f"{bottom_wavelength}", f"{target_wavelength}"
    )

    # Retrieve angstrom exponent
    angstrom_exponent = -np.log(
        df[up_property].values / df[bottom_property].values
    ) / np.log(up_wavelength / bottom_wavelength)

    # Interpolation
    if target_wavelength > bottom_wavelength and target_wavelength < up_wavelength:
        df[target_property] = df[bottom_property].values * (
            target_wavelength / bottom_wavelength
        ) ** (-angstrom_exponent)

    # Left-side extrapolation
    if target_wavelength < bottom_wavelength:
        logger.warning("Extrapolation is used.")
        df[target_property] = df[bottom_property].values * (
            target_wavelength / bottom_wavelength
        ) ** (-angstrom_exponent)

    # Right-side extrapolation
    if target_wavelength > up_wavelength:
        logger.warning("Extrapolation is used.")
        df[target_property] = df[up_property].values * (
            target_wavelength / up_wavelength
        ) ** (-angstrom_exponent)

    return df


def add_logAOD(header: dict, df: pd.DataFrame) -> pd.DataFrame:
    """Add colums in the DataFrame with natural logarithyms of AODs.

    Args:

        - df (pd.DataFrame): Aeronet DataFrame from gfatpy.aeronet.reader()

    Returns:
        - df (pd.DataFrame):  Aeronet DataFrame with new columns
    """

    # Ln applied to AOD
    waves = find_available_aod_wavelengths(header, df)
    for wave_ in waves:
        aod_var = AERONET_INFO["aod_string_type"][
            header["aeronet_data"].replace(" ", "_")
        ].replace("&", f"{wave_}")

        df["lnAOD%d" % wave_] = np.log(df[aod_var])
    return df


def resample_logradius_distribution(
    distribution: np.ndarray | pd.Series,
    factor: int = 10,
    interpolation_kind: str = "quadratic",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Resample a logaritmic distribution.

    Args:

        - distribution (np.ndarray): Aeronet DataFrame from `gfatpy.aeronet.reader()`
        - factor (int, optional): Increase the resolution by dividing the current resolution by this factor. Defaults to 10.
        - interpolation_kind (str, optional): Method of interpolation. Defaults to "quadratic".

    Returns:

        - list[np.ndarray]:
            + Resampled distribution.
            + Resampled radius.
            + Resampled logarithmic radius.
            + New logarithmic radius resolution.
    """
    radius = np.asarray(AERONET_INFO["radius"])
    lnr = np.log(radius)
    resol_lnr = np.diff(lnr).mean()
    resample_resol_lnr = resol_lnr / factor
    resample_lnr = np.arange(lnr[0], lnr[-1] + resol_lnr / factor, resol_lnr / factor)
    resample_radius = np.exp(resample_lnr)

    # Increase resolution to improve the fitting
    resample_function = interp1d(
        radius, distribution, kind=interpolation_kind, bounds_error=True
    )
    resample_distribution_scipy = resample_function(resample_radius)
    resample_distribution_numpy = np.interp(
        resample_radius, radius, distribution.astype(float)
    )
    resample_distribution = np.concatenate(
        (
            resample_distribution_scipy[resample_radius < 11.432287],
            resample_distribution_numpy[resample_radius >= 11.432287],
        )
    )
    return resample_distribution, resample_radius, resample_lnr, resample_resol_lnr


def filter_df(df: pd.DataFrame, conditions_dict: dict) -> pd.DataFrame:
    """Filter the aeronet dataframe according to the conditions specified in `conditions_dict`

    Args:

        - df (pd.DataFrame): Aeronet DataFrame from `gfatpy.aeronet.reader()`
        - conditions_dict (dict): condition dictionary.
            + [Keys: Values]
            + 'aerosol_type': ['DUST', 'HA', 'MA', 'SA', 'MIXTURE'] from `gfatpy.aeronet.classification.aerosol_type_classification_Lee()`
            + 'mode_predominance': [HYGHLY_COARSE, COARSE, BIMODAL, FINE, HIGHLY_FINE, UNKNOWN] from `gfatpy.aeronet.classification.mode_predominance_classification()`
            + 'If_Retrieval_is_L2(without_L2_0.4_AOD_440_threshold)': [1, 0]

    Returns:

        pd.DataFrame: Filtered Aeronet DataFrame
    """

    conditions = True * np.ones(len(df.index))
    for key_ in conditions_dict.keys():
        condition_ = df[key_] == conditions_dict[key_]
        conditions = np.logical_and(conditions, condition_)
    df_ = df[conditions]
    return df_


def calculate_fine_mode_fraction(
    aod_fine: np.ndarray | pd.Series,
    aod_total: np.ndarray | pd.Series,
) -> np.ndarray | pd.Series:
    """Calculate_fine_mode_fraction retrieves the fine mode fraction as the fine-to-total AOD ratio.

    Args:
    
        - aod_fine (np.ndarray): Fine AOD
        - aod_total (np.ndarray): Total AOD

    Raise:

        - ValueError: 'Length of arrays must be the same.'

    Returns:

        - np.ndarray: fine mode fraction
    """

    if len(aod_fine) != len(aod_total):
        logger.error("Length of arrays must be the same.")
        raise ValueError

    return aod_fine / aod_total


def distribution_to_total_concentration(
    df: pd.DataFrame,
    concentration_type: str = "number",
    reference_radius_nm: int | None = None,
    integral_towards: str = "positive",
) -> pd.DataFrame:
    """Retrieve the total concentration (and natural logarithm) in two radius ranges: [r_min, r_reference] and [r_reference, r_max].

    Args:

        - df (pd.DataFrame): AERONET dataframe from *.all file.
        - concentration_type (str): ['surface', 'number']
        - reference_radius_nm (int | None): minimum radius value to retrieve the concentration. If None, inflection radius is used.
        - integral_towards (str): Direction of the integration ['positive': towards the maximum radius, 'negative': towards the minimum radius , 'both': both are retrieved and saved]. Defaults 'positive'.


    Returns:

        - df (pd.DataFrame): dataframe with number/surface concentration and its natural logarithm 'lnN'.

    Raises:

        - ValueError: Dataframe is empty.
        - ValueError: integral_towardds is not one of the following options: ['positive', 'negative', 'both'].
    """

    if len(df) == 0:
        logger.error("Dataframe is empty.")
        raise ValueError

    # Initializing variables
    # Radius
    radius = np.asarray(AERONET_INFO["radius"])  # um¡

    # Positive
    if integral_towards == "both":
        do_positive, do_negative = True, True
    elif integral_towards == "positive":
        do_positive, do_negative = True, False
    elif integral_towards == "negative":
        do_positive, do_negative = False, True
    else:
        logger.error("Value of integral_towards not allowed.")
        raise AttributeError

        # Variables to storage concentrations
    conc_up = np.zeros(len(df))
    conc_down = np.zeros(len(df))
    if reference_radius_nm is not None:
        # Convert from nanomter to micrometer
        reference_radius_used_microm = reference_radius_nm / 1000.0
        conc_up_str = (
            f"{concentration_type}_concentration_above_{reference_radius_nm:d}"
        )
        conc_down_str = (
            f"{concentration_type}_concentration_below_{reference_radius_nm:d}"
        )
    else:
        conc_up_str = "COARSE"
        conc_down_str = "FINE"

        # Indexes of the radius in the Dataframe.
    idx_min = df.columns.get_indexer(["0.050000"])
    idx_max = df.columns.get_indexer(["15.000000"])

    # Stablising the concentration_factor (number Vs surface concentration)
    if concentration_type == "number":
        concentration_factor = 1.0
    else:
        concentration_factor = (
            4 * np.pi * radius[radius >= reference_radius_used_microm] ** 2
        )

    # Selection of the VSD
    radius_as_key = [f"{r:.6f}" for r in AERONET_INFO['radius']]
    dV_dlnr = df[radius_as_key].values

    # Retrieve NSD
    Vradius = (4.0 / 3.0) * np.pi * np.power(radius, 3)  # i-bin volume  um^3
    delta_lnr = np.diff(np.log(radius)).mean()  # resoluticon um
    dN_dlnr_serie = dV_dlnr / Vradius  # NSD #/um^2

    if do_positive:
        for idx in np.arange(len(df)):
            if reference_radius_nm is None:
                inflection_radius = df[
                    "Inflection_Radius_of_Size_Distribution(um)"
                ].iloc[idx]
                reference_radius_used_microm = inflection_radius / 1000.0

            dN_dlnr_ = dN_dlnr_serie[idx, :]

            conc_up[idx] = integrate.simpson(
                dN_dlnr_[radius >= reference_radius_used_microm] * concentration_factor,
                dx=delta_lnr,
            )

        # Save arrays in DATAFRAME
        df[conc_up_str] = conc_up
        df[f"ln_{conc_up_str}"] = np.log(conc_up)

    if do_negative:
        for idx in np.arange(len(df)):
            if reference_radius_nm is None:
                inflection_radius = df[
                    "Inflection_Radius_of_Size_Distribution(um)"
                ].iloc[idx]
                reference_radius_used_microm = inflection_radius / 1000.0

            dN_dlnr_ = dN_dlnr_serie[idx, :]

            conc_down[idx] = integrate.simpson(
                dN_dlnr_[radius < reference_radius_used_microm] * concentration_factor,
                dx=delta_lnr,
            )

        # Save arrays in DATAFRAME
        df[conc_down_str] = conc_down
        df[f"ln_{conc_down_str}"] = np.log(conc_down)
    return df


def find_aod(
    header: dict,
    df: pd.DataFrame,
    target_wavelength: int,
    target_datetime: datetime,
    allowed_time_gap_hour: float = 1,
    allowed_interpolation: bool = True,
) -> tuple[float | None, datetime | None]:
    """Find the aod value at `wavelength` close to the `datetime` as much as determined by `allowed_time_gap_hour`.

    Args:
        - header (dict): AERONET header from `gfatpy.aeronet.reader()`
        - df (pd.DataFrame): AERONET dataframe from `gfatpy.aeronet.reader()`
        - target_wavelength (float): wavelength of the aod requiered. If not found, it will be interpolated with the available ones.
        - target_datetime (datetime): datetime
        - allowed_time_gap_hour (int, optional): allowed time gap between the mesured and required datetime. Defaults to 1. Provides None if requirement not fulfilled.
        - allowed_interpolation (bool, optional):it allows wavelength interpolation.


    Returns:
        - tuple[float | None, float | None]: measured_aod, measured_datetime

            Raises:
        - RuntimeWarning: Time gap found to be larger than allowed by the user with `allowed_time_gap_hour`
        - RuntimeWarning: "Extra- inter-polation required but not allowed by the user (`allowed_interpolation` is `False`).
    """
    # Set default avaiable data flag
    go = False

    # Set result to None by default
    measured_datetime, measured_aod = None, None

    # Finde the nereast datetime
    nearest_datetime = parse_datetime(df.index[df.index.get_indexer([target_datetime], method="nearest")][0])

    # Check distance between both
    if target_datetime > nearest_datetime:
        time_gap = target_datetime - nearest_datetime
    else:
        time_gap = nearest_datetime - target_datetime
    time_gap_hour = time_gap.seconds / 60.0 / 60.0

    if time_gap_hour > allowed_time_gap_hour:
        logger.warning(
            "Time gap found to be larger than allowed by the user with `allowed_time_gap_hour`."
        )
        raise RuntimeWarning
    property = AERONET_INFO["aod_string_type"][
        header["aeronet_data"].replace(" ", "_")
    ].replace("&", f"{target_wavelength}")

    if (
        property not in df.keys() and not allowed_interpolation
    ):  # extrapolation required
        logger.warning(
            "Extra- inter-polation required but not allowed by the user (`allowed_interpolation` is `False`)."
        )
        raise RuntimeWarning

    # Extrapolation allowed
    try:
        bottom_wave, up_wave = find_nearest_wavelength(header, df, target_wavelength)
        df = add_interpol_aod(header, df, target_wavelength, bottom_wave, up_wave)
        go = True
    except Exception as e:
        logger.error("Extra- inter-polatization not finished.")
        raise RuntimeError

    if go:
        row = df.iloc[df.index.get_indexer([target_datetime], method="nearest")]
        measured_aod = row[property].values[0]
        measured_datetime = nearest_datetime

    return measured_aod, measured_datetime