import os, glob
import pandas as pd
from typing import Tuple

from loguru import logger


def header(file_wildcard: str) -> dict:
    """Read all types of aeronet files (*.levX, *.ONEILL_levX, *.tot_levX, and *.all). It accepts wildcard (please use '*' to create wildcard smartly).

    Args:

        - file_wildcard (str): File path wildcard.

    Raises:

        - RuntimeError: 'None or more than one file found. file_wildcard must fit only one file.'

    Return:

        - header (dict): dictionary with fields: `aeronet_version`, `aeronet_station`, `aeronet_data`, `PI_name` and `PI_email`.
    """
    fl = glob.glob(file_wildcard)

    if len(fl) != 1:
        logger.error(
            "None or more than one file found. file_wildcard must fit only one file."
        )
        raise RuntimeError

    # Check same type of file
    head = None
    if len(set([os.path.splitext(fni)[1] for fni in fl])) == 1:
        for f in fl:
            if os.path.isfile(f):
                # open file in read mode
                with open(f, "r") as myfile:
                    head = [next(myfile) for x in range(6)]

    if head is None:
        raise RuntimeError("Header not found.")

    version_, data_ = head[2].split(": ")
    header = {
        "aeronet_version": version_,
        "aeronet_station": head[1][:-1],
        "aeronet_data": data_[:-1],
        "PI_name": head[4].split("PI=")[-1].split(";")[0].replace("_", " "),
        "PI_email": head[4].split("PI Email=")[-1].split(" ")[0],
    }

    return header


def reader(file_wildcard: str) -> Tuple[dict, pd.DataFrame]:
    """Read all types of aeronet files (*.levX, *.ONEILL_levX, *.tot_levX, and *.all). It accepts wildcard (please use '*' to create wildcard smartly). It concatenates data by Datetime Index

    Args:

        - file_wildcard (str): File path wildcard.

    Raises:

        - ValueError: No file found.
        - ValueError: More than onr type of files found. Please, restrict the file_wildcard.

    Returns:
    
        - pd.DataFrame: AERONET database.
    """
    fl = glob.glob(file_wildcard)

    if len(fl) == 0:
        logger.critical("No file found.")
        raise ValueError

    # Check same type of file
    if len(set([os.path.splitext(fni)[1] for fni in fl])) > 1:
        logger.critical(
            "More than onr type of files found. Please, restrict the file_wildcard. Exit"
        )
        raise ValueError

    header_dict = header(file_wildcard)
    df = []
    for f in fl:
        if os.path.isfile(f):
            dfi = pd.read_csv(f, skiprows=6)
            try:
                dfi["Datetime"] = pd.to_datetime(
                    dfi["Date(dd:mm:yyyy)"] + " " + dfi["Time(hh:mm:ss)"],
                    format="%d:%m:%Y %H:%M:%S",
                )
                for key_ in [
                        "Date(dd:mm:yyyy)",
                        "Time(hh:mm:ss)",
                        "Day_of_Year",
                        "Day_of_Year(Fraction)",
                    ]:
                    if key_ in dfi.keys():
                        dfi = dfi.drop(key_, axis=1)
            except Exception:                
                dfi["Datetime"] = pd.to_datetime(
                    dfi["Date_(dd:mm:yyyy)"] + " " + dfi["Time_(hh:mm:ss)"],
                    format="%d:%m:%Y %H:%M:%S",
                )
                try:
                    for key_ in [
                            "Date_(dd:mm:yyyy)",
                            "Time_(hh:mm:ss)",
                            "Day_of_Year",
                            "Day_of_Year(fraction)",
                        ]:
                        if key_ in dfi.keys():
                            dfi = dfi.drop(key_, axis=1)
                except Exception:
                    pass
            dfi.set_index("Datetime", inplace=True)
        else:
            raise ValueError("read_csv failed to open.")

        df.append(dfi)

    df = pd.concat(df)

    # Remove non available properties
    for key_ in df.keys():
        if (df[key_].values == -999).all():
            df = df.drop(key_, axis=1)

    return header_dict, df
