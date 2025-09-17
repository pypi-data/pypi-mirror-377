
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime

from gfatpy.lidar.nc_convert.measurement import Measurement
from gfatpy.generalife.licel import LicelReader

DZ = 7.5
MAX_BINS = 2000

def licel_to_datetime(licel_name: str) -> datetime | None:
    """
    Convert a Licel file name to a datetime object.

    The Licel file name is expected to have a specific format where the last 7 characters
    before the file extension represent the date and time in the following way:
    - The last 2 characters represent the hour and minute.
    - The 3rd and 4th characters from the end represent the day.
    - The 5th character from the end is a hexadecimal digit representing the month.
    - The 6th and 7th characters from the end represent the year.

    Args:
        licel_name (str): The name of the Licel file, including its extension.

    Returns:
        datetime | None: A datetime object representing the date and time extracted from the file name,
                         or None if the file name format is unexpected.
    """
    name, extension = licel_name.split(".")
    try:
        month_decimal = int(name[-5], 16)
        return datetime.strptime(f"{name[-7:-5]}{month_decimal:02d}{name[-4:-2]}T{name[-2:]}{extension[:4]}", r"%y%m%dT%H%M%S")
    except ValueError:
        print(f"Skipping file {licel_name} due to unexpected name format.")
        return None
    

def measurement_to_nc(measurement: Measurement, output_dir: Path):    
    """Converts measurement data to a NetCDF file. The function reads data from the measurement object, processes it, and saves it as a NetCDF file in the specified output directory. The NetCDF file contains raw data, voltages, and metadata attributes such as system name, location, latitude, longitude, altitude, frequency, bin width, number of bins, number of channels, center wavelength, discriminator, bin_corrected, and bcg_corrected.

    Args:
        measurement (Measurement): The measurement object containing data to be converted.
        output_dir (Path): The directory where the output NetCDF file will be saved.

    Raises:
        ValueError: If no files are found in the measurement object.

    """
    files = measurement.get_filepaths()
    
    if files is None or len(files) == 0:
        raise ValueError("No files found.")
    
    times = [licel_to_datetime(file.name) for file in files]
    
    df = pd.read_csv([*files][0].absolute().as_posix(), header=None, skiprows=3, delimiter=' ', encoding='ISO-8859-1', on_bad_lines='skip')
    wavelengths = df[8].dropna().astype(float).values
    voltages = df[6].dropna().astype(float).values

    data = np.empty((len(files), len(wavelengths), MAX_BINS), dtype=float)

    for file_idx, file_path in enumerate(files):
        sp = LicelReader.LicelFileReader(file_path)
        for i, _ in enumerate(wavelengths):
            data[file_idx, i, :] = sp.dataSet[i].physData

    # Create an xarray DataArray from the data array
    raw = xr.DataArray(
        data,
        coords={'wavelength': wavelengths, 'times': times, 'range': DZ*np.arange(MAX_BINS)},
        dims=['times', 'wavelength', 'range']
    )

    voltages = xr.DataArray(
        voltages,
        coords={'wavelength': wavelengths},
        dims=['wavelength']
    )

    center_wavelength = (wavelengths[16] + wavelengths[15]) / 2

    # Create an xarray Dataset from the DataArray
    ds = xr.Dataset({'raw': raw, 'voltages': voltages})

    ds.attrs.update({
            'system name': 'Generalife',  
            'location': 'Granada',
            'latitude': '37.1641° N',
            'longitude': '3.6026° W',
            'altitude': '680 m',
            'frequency': '10 Hz',
            'bin width': '7.5 m',
            'number of bins': '2000',
            'number of channels': '32',
            'center wavelength': center_wavelength,            
            'discriminator' : '4.0',
            'bin_corrected': 'False',
            'bcg_corrected': 'False',
        })

    if isinstance(times[0], datetime):
        datestr = times[0].strftime('%Y%m%d')   
        filename = f"gnl_1a_Prs_rs_ff_{datestr}.nc"
        output_path = output_dir / "generalife" / "1a" / f"{times[0].strftime('%Y')}" / f"{times[0].strftime('%m')}" / f"{times[0].strftime('%d')}" / filename
        ds.to_netcdf(output_path)

