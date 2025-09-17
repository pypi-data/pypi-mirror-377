from matplotlib import pyplot as plt
import numpy as np
import xarray as xr
from datetime import datetime
from pathlib import Path

from gfatpy.parsivel.plot.plot import spectrumPlot

DSD_NC = Path(r"tests\datos\PRODUCTS\parsivel\2023\parsivel_20231211.nc")

def test_spectrumPlot():
    dsd = xr.open_dataset(DSD_NC, decode_cf=True)

    # Test case 1: Valid input
    station = "ÁGORA-UGR"
    # date_limits = (datetime(2024, 2, 15, 19, 30, 0), datetime(2024, 2, 15, 19, 45, 0))    
    target_datetime = datetime(2024, 2, 15, 19, 30, 0)
    spectrum = dsd['droplet_number_concentration'].sel(time=target_datetime, method='nearest')
    fig, ax = plt.subplots()
    spectrum.plot(x='dclasses')
    output_path = Path("./tests/figures/test_parsivel_plot_spectrum.png")        
    fig.savefig(output_path)
    breakpoint()

    result = spectrumPlot(station, spectrum, date_limits=date_limits, output_path=output_path)
    assert result == output_path

    # Test case 2: Empty spectrum list
    spectrum_list = []
    output_path = None

    result = spectrumPlot(station, spectrum_list, date_limits, output_path)
    assert result == output_path

    # Test case 3: Invalid date limits
    date_limits = (datetime(2022, 1, 2), datetime(2022, 1, 1))

    try:
        spectrumPlot(station, spectrum_list, date_limits, output_path)
        assert False, "Expected ValueError"
    except ValueError:
        pass

    # Test case 5: Custom kwargs
    kwargs = {"size": 12, "weight": "bold"}
    output_path = "custom_output.png"

    result = spectrumPlot(station, spectrum_list, date_limits, diameter_limits, velocity_limits, output_path, **kwargs)
    assert result == output_path
