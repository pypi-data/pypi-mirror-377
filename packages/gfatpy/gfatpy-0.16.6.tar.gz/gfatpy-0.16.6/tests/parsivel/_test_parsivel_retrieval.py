import numpy as np
import xarray as xr
from datetime import datetime

from gfatpy.parsivel.retrieval import retrieve_dBZe_from_parsivel

DSD_NC = "tests/datos/PRODUCTS/parsivel/2023/parsivel_20231211.nc"


def test_pars2reflec():
    # Test input parameters
    freq = 35.5
    surf_temp = 10.0
    startDate = datetime(2023, 12, 5, 0, 30, 0)
    stopDate = datetime(2023, 12, 5, 1, 30, 0)

    # Call the function
    result = retrieve_dBZe_from_parsivel(DSD_NC, freq, surf_temp, startDate, stopDate)

    # Test the output dataset
    
    assert isinstance(result, xr.Dataset)
    assert "parsZe" in result
    assert "time" in result.coords

    # Test the shape of the output dataset
    assert result["parsZe"].shape == (61,)