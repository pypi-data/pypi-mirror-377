#!/usr/bin/env python
import os
import glob
import pathlib
from pdb import set_trace
import warnings

import datetime as dt
import numpy as np
import xarray as xr
from loguru import logger

from gfatpy import utils
from gfatpy.lidar.utils.file_manager import add_required_channels, filename2info
from gfatpy.utils.io import read_yaml_from_info
from gfatpy.lidar.utils.utils import LIDAR_INFO

warnings.filterwarnings("ignore")


__author__ = "Bravo-Aranda, Juan Antonio"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Bravo-Aranda, Juan Antonio"
__email__ = "jabravo@ugr.es"
__status__ = "Production"

""" DEFAULT AUXILIAR INFO
"""
# Root Directory (in NASGFAT)  according to operative system


def reader_xarray(
    filelist: list[str] | str | pathlib.Path,
    date_ini: str | None = None,
    date_end: str | None = None,
    ini_range: float | None = None,
    end_range: float | None = None,
    percentage_required: int = 80,
    channels: list[str] = [],
) -> xr.Dataset:
    """
    Lidar data reader using xarray module.
    Inputs:
    - filelist: String with pattern for create a List of lidar files (i.e, '/drives/c/*.nc') (str)
                List of lidar files (list)
                Pathlib.Path object (pathlib.Path)
    - date_ini: 'yyyymmddThhmmss'
    - date_end: 'yyyymmddThhmmss'
    - ini_range: int/float (m)
    - end_range: int/float (m)
    - percentage_required= percentage of the time period required to continue the process. Default 80%  (int)
    - channels: list of channel number (e.g., [0, 1, 5]) or [] to load all of them
    Output:
    - lidar: dictionary or 'None' in case of error.
    """

    """ Aux Functions
    """

    #Global Variables within this function
    global INFO
    
    def select_channels(dataset: xr.Dataset, channels: list | str) -> xr.Dataset:
        """select_channels function creates a new dataset with 'signal_CHANNEL' defined in 'channels' (list).

        Args:
            dataset (xr.Dataset): lidar dataset
            channels (list | str): list of lidar channel names

        Returns:
            xr.Dataset: lidar dataset
        """

        if len(channels) > 0:
            if isinstance(channels, str):
                channels = [channels]
            if isinstance(channels, np.ndarray):
                channels = channels.tolist()

            # find variables: signal related to channel
            _vars = ["signal"]
            real_channels = []
            for _channel in dataset["channel"].values.tolist():
                if _channel not in channels:
                    for _var in _vars:
                        varname = "%s_%s" % (_var, _channel)
                        dataset = dataset.drop_vars(varname)
                else:
                    real_channels.append(_channel)
            dataset = dataset.sel(channel=real_channels)
            dataset = dataset.assign_coords(channel=real_channels)
        return dataset

    def check_minimum_profiles(
        times: np.ndarray,
        date_ini: dt.datetime,
        date_end: dt.datetime,
        percentage_required: float,
    ) -> bool:
        """Check Lidar Data has enough profiles

        Args:
            times ([type]): [description]
            date_ini ([type]): [description]
            date_end ([type]): [description]
            percentage_required ([type]): [description]
        """

        check = True
        time_resolution = float(
            np.median(np.diff(times)) / np.timedelta64(1, "s")
        )  # FIXME: typing error
        interval_duration = (date_end - date_ini).total_seconds()
        Nt = np.round(
            interval_duration / time_resolution
        )  # Theoretical Number of profiles
        Nm = (percentage_required / 100) * Nt  # Minimum number of profiles
        Np = len(times)  # Number of actual profiles
        if Np > Nm:
            logger.info(
                f"Data loaded from {date_ini.isoformat()} to {date_end.isoformat()}"
            )
        else:
            logger.warning(
                f"Not enough data found ({Np}<{Nm}) in the user-required period ({interval_duration} s.)"
            )
            check = False

        return check

    """ The Reader
        The Reader does:
        1. concatenate along time dimension
        2. merge channels comming from different telescopes (ALHAMBRA), assuming same range coordinate
    """
    logger.info("Start Reader ...")

    # Find Files to Read    
    try:
        if isinstance(filelist, str):            
            i_ = pathlib.Path(filelist)
            if i_.is_file():
                files2load = [str(i_.absolute())]
            else:
                file_list_ = [*i_.parent.rglob(i_.name)]
                files2load = [str(i_.absolute()) for i_ in file_list_]                
        elif isinstance(filelist, pathlib.Path):
            files2load = [str(filelist.absolute())]
        elif isinstance(filelist, list):        
            files2load = filelist
        else:            
            raise ValueError("filelist must be a string, pathlib.Path or list of strings.")
    except Exception as e:        
        files2load = []
        logger.warning(str(e))
        logger.warning(f"Files in {filelist} not found.")
    
    if len(files2load) > 0:
        logger.info(files2load)
        lidartemp = None        

        # Get lidar info from filename
        lidar_nick, _, _, _, _, date  = filename2info(pathlib.Path(files2load[0]).name)
        
        INFO = read_yaml_from_info(lidar_nick, date)


        if lidar_nick is None:
            logger.critical("Lidar nick not in lidar systems availables.")

        try:
            # Add required channels to the channel list to obtain product channel:
            channels = add_required_channels(lidar_nick, channels, date)

            # Loop over modules: 1) concat time; 2) merge module
            lidar_ = None
            for fn in files2load:
                with xr.open_dataset(
                    fn, chunks={}
                ) as _dx:  # chunks={"time": 600, "range": 1000})
                    _dx = select_channels(_dx, channels)
                if not lidar_:
                    lidar_ = _dx
                else:
                    # concat only variables that have "time" dimension.
                    # rest of variables keep values from first dataset
                    try:
                        lidar_ = xr.concat(
                            [lidar_, _dx],
                            dim="time",
                            data_vars="minimal",
                            coords="minimal",
                            compat="override",
                        )
                    except Exception as e:
                        logger.critical("Dataset in {fn} not concatenated")
                        raise e
            # Sort Dataset by Time
            if lidar_ is not None:
                lidar_ = lidar_.sortby(lidar_["time"])
            else:
                raise ValueError("lidarmod is None.")
            # Merge Module
            if not lidartemp:
                lidartemp = lidar_
            else:
                try:
                    lidartemp = xr.merge([lidartemp, lidar_])
                except Exception as e:
                    logger.critical(f"{e}")
                    logger.critical(f"Datasets not merged")
                    raise e
        except Exception as e:
            logger.critical(f"{e}")
            logger.critical("Files not concatenated")
            raise e

        if lidartemp:
            # Selection time window and Check Enough Profiles
            if np.logical_and(date_ini is not None, date_end is not None):
                if np.logical_and(isinstance(date_ini, str), isinstance(date_end, str)):
                    # Times Formatting

                    date_ini_dt = utils.utils.str_to_datetime(date_ini)  # type: ignore
                    date_end_dt = utils.utils.str_to_datetime(date_end)  # type: ignore

                    # Time Selection
                    min_time_resol = dt.timedelta(seconds=0.1)
                    lidar = lidartemp.sel(
                        time=slice(
                            date_ini_dt - min_time_resol, date_end_dt + min_time_resol
                        )
                    )

                    # Check selection
                    ok = check_minimum_profiles(
                        lidar["time"].values,
                        date_ini_dt,
                        date_end_dt,
                        percentage_required,
                    )
                    if not ok:
                        lidar = None
                else:
                    lidar = lidartemp
            else:
                lidar = lidartemp
            del lidartemp

            # Complete lidar dataset
            if lidar:
                # Range Clip
                if ini_range is not None and end_range is not None:
                    if end_range > ini_range:
                        lidar = lidar.sel(range=slice(ini_range, end_range))
                    else:
                        raise ValueError("ini_range is larger than end_range.")

                # add background ranges
                if "BCK_MIN_ALT" not in lidar.attrs.keys():
                    lidar.attrs["BCK_MIN_ALT"] = 75000
                if "BCK_MAX_ALT" not in lidar.attrs.keys():
                    lidar.attrs["BCK_MAX_ALT"] = 105000

                # Extract information from filename
                try:
                    lidar.attrs["lidarNick"] = os.path.basename(files2load[0]).split(
                        "_"
                    )[0]
                    lidar.attrs["dataversion"] = os.path.basename(files2load[0]).split(
                        "_"
                    )[1]
                except:
                    lidar.attrs["lidarNick"] = "Unknown"
                    lidar.attrs["dataversion"] = "Unknown"

            else:
                lidar = None
        else:
            logger.error("Impossible to load found files.")
            lidar = None
    else:
        logger.error("Files not found.")
        lidar = None

    if lidar is None:
        # set_trace()
        logger.error("No dataset created.")
        raise RuntimeError("No dataset created.")

    logger.info("End Reader")
    return lidar
