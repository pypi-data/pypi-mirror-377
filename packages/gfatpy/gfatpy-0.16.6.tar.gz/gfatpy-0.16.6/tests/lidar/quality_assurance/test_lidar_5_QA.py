import numpy as np
from datetime import datetime

from gfatpy.lidar.quality_assurance.io import get_meteo


def test_get_meteo():
    date_ = datetime(2021, 1, 1)
    heights = np.arange(2666) * 7.5
    meteo_profiles, _ = get_meteo(
        date_, heights, meteorology_source="standard_atmosphere"
    )
    assert "pressure" in meteo_profiles.keys()
    assert meteo_profiles["pressure"][0] == 101325.0
    assert "temperature" in meteo_profiles.keys()
    assert meteo_profiles["temperature"][0] == 288.15
    assert "height" in meteo_profiles.keys()
