import os

import xarray as xr
import netCDF4 as nc
import numpy as np
from loguru import logger


def cloudnet_reader(cloudnet_fn: str, fields: list | None = None) -> xr.Dataset:
    """Read Cloudnet File

    Parameters
    ----------
    cloudnet_fn: str
        full path of cloudnet file name
    fields: list
        list of variables within the cloudnet dataset

    Returns
    -------
    ds: xarray
        Cloudnet dataset
    """
    try:
        if os.path.isfile(cloudnet_fn):
            with xr.open_dataset(cloudnet_fn, chunks={}) as ds:
                if fields is not None:
                    ds = ds[fields]
        else:
            logger.error("File %s not found" % cloudnet_fn)
            ds = None
    except Exception as e:
        logger.error(str(e))
        ds = None

    return ds


def categorice_reader(list_files: list[str]) -> dict:
    """read categorice data from netCDF files

    Designed to work with netcdf list_files associated to one single day
    """
    logger.warning("to be deprecated")
    print("Reading netCDF files: %s" % list_files)
    data = {}

    if list_files:
        var2load = [
            "lwp",
            "Z",
            "beta",
            "mean_zbeta",
            "temperature",
            "v",
            "pressure",
            "specific_humidity",
            "rainrate",
        ]

        # open all files
        nc_ids = [nc.Dataset(file_) for file_ in list_files]

        # localization of instrument
        data["lat"] = nc_ids[0].variables["latitude"][:]
        data["lon"] = nc_ids[0].variables["longitude"][:]
        data["alt"] = nc_ids[0].variables["altitude"][:]
        data["location"] = nc_ids[0].location

        # read alt (no need to concatenate)
        data["height"] = nc_ids[0].variables["height"][:]
        data["model_height"] = nc_ids[0].variables["model_height"][:]

        # wavelength (no need to concatenate)
        tmp = nc_ids[0].variables["lidar_wavelength"][:]
        data["wavelength"] = tmp
        data["wavelength_units"] = nc_ids[0].variables["lidar_wavelength"].units

        # read time
        units = nc_ids[0].variables["time"].units  # HOURS SINCE %Y-%m-%d 00:00:00 +0:00
        tmp = [nc.num2date(nc_id.variables["time"][:], units) for nc_id in nc_ids]
        data["raw_time"] = np.concatenate(tmp)

        # check if any data available
        # print(date)
        # time_filter = (data['raw_time'] >= date) & (data['raw_time'] < date + dt.timedelta(days=1))
        # if not np.any(time_filter):
        #     return None

        for var in var2load:
            tmp = [nc_id.variables[var][:] for nc_id in nc_ids]
            data[var] = np.ma.filled(np.concatenate(tmp, axis=0), fill_value=np.nan)
            # It is assumed that properties do not change along netcdf files for the same day
            data[var][data[var] == nc_ids[0][var].missing_value] = np.nan

        # Change name to fit real array content
        data["dBZe"] = data["Z"].copy()

        # close all files
        [nc_id.close() for nc_id in nc_ids]

    return data


def classification_reader(list_files: list[str]) -> dict:
    """read data from netCDF files

    Designed to work with netcdf list_files associated to one single day
    """
    """
    0: Clear sky
    1: Cloud liquid droplets only
    2: Drizzle or rain
    3: Drizzle or rain coexisting with cloud liquid droplets
    4: Ice particles
    5: Ice coexisting with supercooled liquid droplets
    6: Melting ice particles
    7: Melting ice particles coexisting with cloud liquid droplets
    8: Aerosol particles, no cloud or precipitation
    9: Insects, no cloud or precipitation
    10: Aerosol coexisting with insects, no cloud or precipitation
    """
    logger.warning("to be deprecated")
    print("Reading netCDF files: %s" % list_files)

    data = {}

    if list_files:
        var2load = ["cloud_base_height", "cloud_top_height", "target_classification"]
        # open all files
        nc_ids = [nc.Dataset(file_) for file_ in list_files]

        # localization of instrument
        data["lat"] = nc_ids[0].variables["latitude"][:]
        data["lon"] = nc_ids[0].variables["longitude"][:]
        data["alt"] = nc_ids[0].variables["altitude"][:]
        data["location"] = nc_ids[0].location

        # read alt (no need to concantenate)
        data["height"] = nc_ids[0].variables["height"][:]

        # read time
        units = (
            nc_ids[0].variables["time"].units
        )  #'days since %s' % dt.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')
        tmp = [nc.num2date(nc_id.variables["time"][:], units) for nc_id in nc_ids]
        data["raw_time"] = np.concatenate(tmp)

        # check if any data available
        # print(date)
        # time_filter = (data['raw_time'] >= date) & (data['raw_time'] < date + dt.timedelta(days=1))
        # if not np.any(time_filter):
        #     return None

        for var in var2load:
            tmp = [nc_id.variables[var][:] for nc_id in nc_ids]
            data[var] = np.ma.filled(np.concatenate(tmp, axis=0), fill_value=np.nan)
            # It is assumed that properties do not change along netcdf files for the same day
            if "missing_value" in nc_ids[0][var].ncattrs():
                data[var][data[var] == nc_ids[0][var].missing_value] = np.nan

        # close all files
        [nc_id.close() for nc_id in nc_ids]

    return data
