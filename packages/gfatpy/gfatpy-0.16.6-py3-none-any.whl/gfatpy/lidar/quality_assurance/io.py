from pathlib import Path

from datetime import datetime
import xarray as xr
import numpy as np
import pandas as pd
from typing import Any

from gfatpy.lidar.utils.utils import LIDAR_INFO
from gfatpy.atmo.ecmwf import get_ecmwf_temperature_pressure
from gfatpy.atmo.atmo import generate_meteo_profiles
from gfatpy.lidar.utils.file_manager import channel2info


def rayleigh2earlinet(dataset: xr.Dataset, output_dir: Path | str | None) -> tuple[Path, Path]:
    """It converts a Rayleigh Fit dataset to EARLINET format.

    Args:
        dataset (xr.Dataset): Rayleigh Fit dataset.
        output_dir (Path | str | None): Output directory. Defaults to None.

    Raises:
        NotADirectoryError: Directory not found.

    Returns:
        tuple[Path, Path]: NetCDF and CSV filepaths. 
    """    
    # info from dataset
    date = datetime.strptime(
        dataset.attrs["datetime_ini"], dataset.attrs["datetime_format"]
    )
    date_str = datetime.strftime(date, "%d.%m.%Y, %HUTC")
    lidar_name: str = dataset.attrs["lidar_name"].lower()
    lidar_location: str = dataset.attrs["lidar_location"]
    lidar_id: str = dataset.attrs["lidar_id"]
    channel: str = dataset.attrs["channel"]
    detection_mode: str = dataset["detection_mode"].values.item()
    if detection_mode == "a":
        dark_subtracted_str: str = dataset.attrs["dark_subtracted"]
    else:
        dark_subtracted_str: str = ""
    duration = float(dataset.attrs["duration"])
    wavelength, _, polarization_, mode_ = channel2info(channel)
    radiosonde_location = dataset.attrs["radiosonde_location"]
    if dataset.attrs["radiosonde_wmo_id"] is not None:
        radiosonde_wmo_id = dataset.attrs["radiosonde_wmo_id"]
    else:
        radiosonde_wmo_id = -9999
        dataset.attrs["radiosonde_wmo_id"] = radiosonde_wmo_id

    radiosonde_date = datetime.strptime(
        dataset.attrs["radiosonde_datetime"], "%Y-%m-%dT%H-%M-%S"
    )

    pol_str = LIDAR_INFO["metadata"]["code_polarization_str2long_name"][polarization_]  # type: ignore
    mode_str = LIDAR_INFO["metadata"]["code_mode_str2long_name"][mode_]  # type: ignore
    z_min, z_max = dataset.attrs["rayleigh_height_limits"]

    # create output_dir
    if output_dir is None:
        output_dir = Path.cwd()
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    if not output_dir.exists() or not output_dir.is_dir():
        raise NotADirectoryError(f"{output_dir} not found.")

    output_dir.mkdir(parents=True, exist_ok=True)

    rf_nc_fn = output_dir / f"{lidar_id}RayleighFit{channel}.nc"
    dataset.to_netcdf(rf_nc_fn)

    # # Filename
    rf_fn = output_dir / f"{lidar_id}RayleighFit{channel}.csv"

    # Select Columns to write
    cols = ["BCS", "RCS"]
    if detection_mode == "a":  # (if analog)
        cols.append("DC")
    rf_df = dataset[cols].to_dataframe()
    rf_df.columns = [dataset[col].attrs["name"] for col in cols]

    # Write File Earlinet Format
    with open(rf_fn, "w") as f:
        f.write(f"station ID = {lidar_id} ({lidar_location})\n")
        f.write(f"system = {lidar_name}\n")
        f.write(
            f"signal = {wavelength}, {pol_str}, {mode_str}, {dark_subtracted_str}\n"
        )
        f.write(
            f"date of measurement, time, duration of measurement= {date_str}, {duration:.1f} s\n"
        )
        f.write(
            f"location, WMO radiosonde station ID, date of radiosonde = {radiosonde_location}, {radiosonde_wmo_id}, {radiosonde_date}\n"
        )
        f.write(
            f"lower and upper Rayleigh height limits = {np.round(z_min)}, {np.round(z_max)}\n"
        )
    f.close()

    # write in the same file the rest of information
    rf_df.index = rf_df.index.map(lambda x: "%.4f" % x)
    rf_df.to_csv(rf_fn, mode="a", header=True, na_rep="NaN", float_format="%.4e")
    
    #Close file
    del rf_df
    return rf_nc_fn, rf_fn


def get_meteo(
    date: datetime,
    range: np.ndarray[Any, np.dtype[np.float64]],
    meteorology_source: str,
    pressure_surface: float | None = None,
    temperature_surface: float | None = None,
) -> tuple[pd.DataFrame, dict]:
    #TODO: docstring
    #TODO: merge with generate_meteo_profiles
    # get T and P
    info = {}
    info["radiosonde_datetime"] = date.strftime(
        "%Y-%m-%dT%H-%M-%S"
    )  # FIXME: change if other methods are implemented.

    if meteorology_source == "ecmwf":  # TODO: implement other methods
        try:
            meteo_profiles = get_ecmwf_temperature_pressure(date, heights=range)
        except Exception:
            meteorology_source = "standard_atmosphere"
            raise Warning(
                "ECMWF data not available. Use meteorology_source = 'standard_atmosphere' instead."
            )
        info["radiosonde_wmo_id"] = "ecmwf"
        info["radiosonde_location"] = "Granada"
        info["radiosonde_source"] = "ECMWF"

    if meteorology_source == "standard_atmosphere":
        meteo_profiles = generate_meteo_profiles(
            range, pressure=pressure_surface, temperature=temperature_surface
        )
        info["radiosonde_location"] = "Granada"
        if pressure_surface is not None and temperature_surface is not None:        
            info["radiosonde_wmo_id"] = "scaled standard atmosphere"
            info["radiosonde_source"] = "scaled standard atmosphere"
        else:
            info["radiosonde_wmo_id"] = "standard atmosphere"
            info["radiosonde_source"] = "standard atmosphere"
        # FIXME: raise Warning( "ECMWF data not available. Using scaled standard atmosphere with (T, P) = (25, 938)" )
    else:
        raise ValueError(
            "only ecmwf and (scaled) standard_atmosphere methods are currently implemented."
        )
    return meteo_profiles, info
