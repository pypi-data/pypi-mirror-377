#!/usr/bin/env python
# coding: utf-8
import os
import glob
from pathlib import Path
from loguru import logger
import numpy as np
import pandas as pd
import datetime as dt

from gfatpy.parsivel.utils import DSD_INFO
import xarray as xr
import numpy as np
import datetime as dt
import xarray as xr
import xarray as xr
import numpy as np
from gfatpy.parsivel.utils import DSD_INFO

__version__ = '1.0.0'
__author__ = 'Juan Antonio Bravo-Aranda'

# script description
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROG_NAME = 'disdrometerConverter'
PROG_DESCR = 'converting raw data to netCDF files.'

def dat2nc(dat_path: Path, output_path: Path | None) -> None:
    """It convers *.dat parsivel disdrometer data to netcdf file.

    Args:
        dat_path (Path): Disdrometer file with extension *.dat
        output_path (Path): Filepath of the netcdf file to be generated. If None, it will be created in the current working directory.

    Returns:
        None
    """

    if not dat_path.exists():
        breakpoint()
        raise FileNotFoundError(f'{dat_path} does not exist')
    
    if not output_path:
        output_path = Path.cwd() / dat_path.replace('.dat', '.nc')

    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    if os.path.isfile(dat_path):
        
        df = pd.read_csv(dat_path,skiprows=0,header=1,parse_dates=["TIMESTAMP"],low_memory=False)
        df = df.drop([0, 1])
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
        df.set_index('TIMESTAMP', inplace=True)

        # Number of droplets per volume equivalent diameter class and velocity class center
        spectrum_array = df.iloc[:, -1024:].to_numpy(dtype=np.float64)

        #Replace different possible fill values: NAN, -9.999, -999, -9999
        fill_values = [-9.999, -999, -9999, -99999, 'NAN']
        for fill_value in fill_values:
            spectrum_array[spectrum_array == fill_value] = np.nan
        
        spectrum_matrix = np.array([np.split(spectrum, 32) for spectrum in spectrum_array])

        ds = xr.Dataset(
            {
                'time': xr.DataArray(df.index.to_pydatetime(), dims=['time']),
                'dclasses': xr.DataArray(DSD_INFO['diameters'], dims=['dclasses']),
                'vclasses': xr.DataArray(DSD_INFO['velocities'], dims=['vclasses'])
            }
        )

        ds.time.encoding['units'] = "seconds since 2000-01-01 00:00:00"
        ds.time.encoding['calendar'] = "proleptic_gregorian"

        # DEFINE ATRIBUTOS GLOBALES:
        ds.attrs['Title'] = "Parsivel disdrometer data"
        ds.attrs['Institution'] = 'ANDALUSIAN INSTITUTE FOR EARTH SYSTEM RESEARCH (Granada, Spain)'
        ds.attrs['Contact_person'] = 'Dr. Juan Bravo (jabravo@ugr.es )'
        ds.attrs['Source'] = 'NETCDF4'
        ds.attrs['History'] = 'Data processed on python.'
        ds.attrs['Dependencies'] = 'external'
        ds.attrs['Conventions'] = "CF-1.6 where applicable"
        ds.attrs['Processing_date'] = dt.datetime.today().strftime('%Y-%m-%d,%H:%m:%S')
        ds.attrs['Author'] = 'Irving Juanico (iejuv@ier.unam.mx)'
        ds.attrs['Comments'] = ''
        ds.attrs['Licence'] = 'For non-commercial use only. These data are the property of IISTA, their use is strictly prohibited without the authorization of the institute'

        # Assign values to variables
        ds['droplet_number_concentration'] = xr.DataArray(spectrum_matrix, dims=['time', 'dclasses', 'vclasses'], attrs={'units': 'cm-3', 'long_name': 'number of droplets per volume equivalent diameter class and velocity class center'})
        ds['record_number'] = xr.DataArray(df['RECORD'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': '#', 'long_name': 'File record number.'})
        ds['rain_intensity'] = xr.DataArray(df['rain_intensity'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': 'mm h-1', 'long_name': 'Intensity rain precipitation'})
        ds['snow_intensity'] = xr.DataArray(df['snow_intensity'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': 'mm h-1', 'long_name': 'Intensity snow precipitation'})
        ds['wmo_code_WaWa'] = xr.DataArray(df['weather_code_wawa'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': '-', 'long_name': 'weather code according to WMO SYNOP 4680'})
        ds['radar_reflectivity'] = xr.DataArray(df['radar_reflectivity'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': 'dbZ', 'long_name': 'Radar reflectivity'})
        ds['visibility_mor'] = xr.DataArray(df['mor_visibility'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': 'm', 'long_name': 'MOR visibility in the precipitation'})
        ds['signal_amplitude'] = xr.DataArray(df['signal_amplitude'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': '#', 'long_name': 'Signal amplitude of Laserband'})
        ds['detected_droplets'] = xr.DataArray(df['number_particles'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': '#', 'long_name': 'Number of detected particles'})
        ds['sensor_temperature'] = xr.DataArray(df['sensor_temperature'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': 'ºC', 'long_name': 'Temperature in sensor'})
        ds['heating_current'] = xr.DataArray(df['heating_current'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': 'A', 'long_name': 'Heating current'})
        ds['sensor_voltage'] = xr.DataArray(df['sensor_voltage'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': 'V', 'long_name': 'Sensor Voltage'})
        ds['kinetic_energy'] = xr.DataArray(df['kinetic_energy'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': 'J', 'long_name': 'Kinetic energy'})
        ds['sensor_status'] = xr.DataArray(df['sensor_status'].to_numpy(dtype=np.float64), dims=['time'], attrs={'units': '0: OK/ON  and   1: FUCK  2: OFF', 'long_name': 'Sensor status'})
        
        ds.to_netcdf(path=output_path)
        ds.close()                
    return None

def rawfile2nc(disdro_path: Path, output_path: Path | None) -> None:
        
    extension = disdro_path.suffix
    if extension == '.mis':            
        logger.info('Converting mis-file: %s' % disdro_path)
        mis2nc(disdro_path, output_path)
    elif extension == '.dat':
        logger.info('Converting dat-file: %s' % disdro_path)
        dat2nc(disdro_path, output_path)    
    else:
        raise ValueError(f'File extension unknown: {disdro_path}')
    return


def raw2nc(list_files: list[Path], output_dir: Path | None) -> None:
    """It conver raw disdrometer files to netcdf files.

    Args:
        list_files (list[Path]): List of disdrometer files with extension *.mis or *.dat
        output_dir (Path): Directory where the netcdf files will be generated. If None, it will be created in the current working directory.
    """        

    if output_dir.is_file():
        raise ValueError(f'{output_dir} is a file, not a directory')

    if not output_dir:
        output_dir = Path.cwd()
    for file_ in list_files:
        output_filepath = output_dir / file_.name.replace(file_.suffix, '.nc')
        rawfile2nc(file_, output_filepath)

    return None


#TODO: Implement mis2nc function
def mis2nc(mis_path: Path, output_path: Path | None) -> None:
    pass