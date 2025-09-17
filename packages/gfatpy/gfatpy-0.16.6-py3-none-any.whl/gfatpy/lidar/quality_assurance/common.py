
import xarray as xr
from loguru import logger

DARK_SUB = {0: "not-dark-subtracted", 1: "dark-subtracted"}


def select_dc(lidar_ds: xr.Dataset, channel: str) -> tuple[xr.Dataset | None, str]:
    """Select dark measurements for a given channel.

    Args:
        lidar_ds (xr.Dataset): Dataset with dark measurements.
        channel (str): Channel to select dark measurements.

    Returns:
        tuple[xr.Dataset | None, str]: Dark measurements and dark subtraction status.
    """    
    """Read Associated Dark Current Measurements, if wanted"""
    ilu_dict = {True: "day", False: "ngt"}
    if channel[-1] == "a":
        if lidar_ds:
            dark_subtracted = lidar_ds[f"signal_{channel}"].dark_corrected
            if dark_subtracted:
                # day/ngt DC measurements
                ilu_flag = (
                    lidar_ds.cosine_sza.mean("time").values > 0.0
                )  # True: day, False: night
                dc = lidar_ds[f"dc_{channel}"].sel(ilu=ilu_dict[ilu_flag])
                dark_subtracted = DARK_SUB[1]
            else:
                dc = None
                dark_subtracted = DARK_SUB[0]
                logger.warning("dark measurement not subtracted.")
        else:
            dc = None
            dark_subtracted = ""
            logger.warning("lidar " "xarray.Dataset" " not provided.")
    else:
        dc, dark_subtracted = None, ""
    return dc, dark_subtracted
