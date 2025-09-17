from loguru import logger
import numpy as np
from datetime import datetime
from pathlib import Path
import pandas as pd
import xarray as xr

from .gamma_distribution import BinnedPSD

def getEdges():

    pars_class = np.zeros(shape=(32, 2))
    bin_edges = np.zeros(shape=(33, 1))

    # pars_class[:,0] : Center of Class [mm]
    # pars_class[:,1] : Width of Class [mm]
    pars_class[0:10, 1] = 0.125
    pars_class[10:15, 1] = 0.250
    pars_class[15:20, 1] = 0.500
    pars_class[20:25, 1] = 1.0
    pars_class[25:30, 1] = 2.0
    pars_class[30:32, 1] = 3.0

    j = 0
    pars_class[0, 0] = 0.062
    for i in range(1, 32):
        if (
            i < 10
            or (i > 10 and i < 15)
            or (i > 15 and i < 20)
            or (i > 20 and i < 25)
            or (i > 25 and i < 30)
            or (i > 30)
        ):
            pars_class[i, 0] = pars_class[i - 1, 0] + pars_class[i, 1]

        const = [0.188, 0.375, 0.75, 1.5, 2.5]
        if i == 10 or i == 15 or i == 20 or i == 25 or i == 30:
            pars_class[i, 0] = pars_class[i - 1, 0] + const[j]
            j = j + 1

        # print pars_class[i,0]
        bin_edges[i + 1, 0] = pars_class[i, 0] + pars_class[i, 1] / 2

    bin_edges[0, 0] = 0.0
    bin_edges[1, 0] = pars_class[0, 0] + pars_class[0, 1] / 2

    return bin_edges


def retrieve_dBZe_from_parsivel(    
    parsFilePath: Path | str,
    freq: float,
    surf_temp: float,
    startDate: datetime,
    stopDate: datetime,
    diameter_resolution: float = 0.01,
) -> xr.Dataset:
    """Converts Parsivel data to reflectivity.

    Args:
        parsFilePath (Path | str): disdrometer file with extension *.nc
        freq (float): Frequency [GHz] of the reflectivity
        surf_temp (float): Surface temperature [C]
        startDate (datetime.date): Start date of the period to be analyzed
        stopDate (datetime.date): Stop date of the period to be analyzed

    Raises:
        FileNotFoundError: If the file does not exist. 

    Returns:
        xr.Dataset: Reflectivity dataset
    """    

    freqstr = "%3.1f" % freq

    # reding meang volume diameter from parsivel
    if isinstance(parsFilePath, str):
        parsFilePath = Path(parsFilePath)
    
    if not parsFilePath.exists():
        raise FileNotFoundError(f"File {parsFilePath} does not exist")

    pasrDS = xr.open_dataset(parsFilePath)

    # Load scattering database
    if surf_temp < 5:
        scattabstr = Path(__file__).parent / "scattering_databases" / f"0.C_{freqstr}GHz.csv"
    elif 5 <= surf_temp < 15:        
        scattabstr = Path(__file__).parent / "scattering_databases" / f"10C_{freqstr}GHz.csv"
    else:
        scattabstr = Path(__file__).parent / "scattering_databases" / f"20C_{freqstr}GHz.csv"
    df = pd.read_csv(scattabstr)

    diameter = "diameter[mm]"
    radarxs = "radarsx[mm2]"
    wavelength = "wavelength[mm]"
    temp = "T[k]"
    extxs = "extxs[mm2]"

    upscale_end = (len(df) + 1.0) / 100.0
    diameter_ups = np.arange(diameter_resolution, upscale_end, diameter_resolution)

    # constants
    T = df.loc[1, temp]
    wavelen = df.loc[1, wavelength]
    K2 = 0.93

    # integration constant
    int_const = wavelen**4 / ((np.pi) ** 5 * K2)

    #select time range    
    before=( pd.to_datetime(startDate,format='%Y-%m-%d %H:%M') < pd.to_datetime(pasrDS["time"].data))
    after = ( pd.to_datetime(stopDate,format='%Y-%m-%d %H:%M') > pd.to_datetime(pasrDS["time"].data))
    mask_time = before & after
                          
    if not any(mask_time):
        print('No rain in this user-provided period.')
        return
    else:
        parstime = pasrDS["time"].sel(time=slice(startDate, stopDate))
        N = pasrDS['droplet_number_concentration'].sel(time=slice(startDate, stopDate)).values
        breakpoint()
        N = 10**N
        #print(N)
        
    #calculating Ze using parsivel SD    
    Zpars = np.zeros(N.shape[0])    
    if freq > 20:        
        #Ze parsivel using T-matrix at "freq" GHz
        for i in range(N.shape[0]):
            PSD = BinnedPSD(getEdges(),N[i])                                        
            y = PSD(diameter_ups)*np.tile(df.loc[:,radarxs], reps=(PSD(diameter_ups).shape[1],1)).T
            Zpars[i] = int_const * y.sum()*diameter_resolution
            logger.info(f"Ze parsivel in Mie regime. Using T-matrix at {freqstr} GHz. Retrieval NOT VALIDATED.")
    else:
        #Ze parsivel in Rayleigh regime
        for i in range(N.shape[0]):
            PSD = BinnedPSD(getEdges(),N[i])
            d6 = PSD(diameter_ups)*df.loc[:,diameter]**6
            Zpars[i] = d6.sum()*diameter_resolution 
      
    parsZe = 10 * np.log10(Zpars)
    pars = xr.Dataset({'parsZe': (['time'],  parsZe)}, coords={'time': parstime})
    return pars