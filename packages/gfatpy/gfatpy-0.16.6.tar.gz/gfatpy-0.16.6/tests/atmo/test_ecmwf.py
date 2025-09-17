from datetime import datetime
import numpy as np

from gfatpy.atmo.ecmwf import get_data_as_ascii, get_ecmwf_temperature_pressure


def test_ecmwf_temperature_pressure():
    meteo_df = get_ecmwf_temperature_pressure("2022-08-08", heights=[20, 30, 40])

    assert sorted(meteo_df.columns.tolist()) == ["height", "pressure", "temperature"]
    assert not meteo_df.isnull().values.any()
    assert meteo_df.temperature.dtype == np.float64
    assert meteo_df.pressure.dtype == np.float64

def test_get_data_as_ascii():
    
    file_ecmwf = get_data_as_ascii(datetime(2023, 5, 10 , 2, 0, 0))

    assert file_ecmwf.exists()
    assert file_ecmwf.suffix == ".txt"
    assert file_ecmwf.name == "20230510_0200_ecmwf.txt"

  # TODO: ECMWF_day
# def test_ecmwf_day():

#     dataset = get_ecmwf_day("2021-07-05", heights=np.array([20, 30, 40]), times= )
#     assert not dataset.pressure.isnull().values.any()
#     assert not dataset.temperature.isnull().values.any()
