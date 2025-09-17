import pandas as pd

from gfatpy.aeronet.utils import add_interpol_aod, AERONET_INFO


def aod_lidar_wavelengths_all(header: dict, df: pd.DataFrame) -> pd.DataFrame:
    """Adds the AOD at 355, 532 and 1064 nm to the AERONET dataframe.

    Args:

        - header (dict): AERONET header.
        - df (pd.DataFrame): AERONET dataframe.

    Returns:
    
        - pd.DataFrame: AERONET dataframe.
    """

    for wave_ in [355, 532, 1064]:
        aod_str = AERONET_INFO["aod_string_type"][
            header["aeronet_data"].replace(" ", "_")
        ].replace("&", f"{wave_}")
        aod_ = add_interpol_aod(
            header,
            df,
            wave_,
        )
        df[aod_str] = aod_

    return df
