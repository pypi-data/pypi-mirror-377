import numpy as np

from gfatpy.utils.calibration import molecular_properties_2d


def test_molecular_properties_2d():
    heights = np.arange(2666) * 7.5
    molecular_properties_2d(
        "2022-08-08",
        wavelength=532,
        heights=heights,
        times=np.arange(
            np.datetime64("2022-08-08T08:00"),
            np.datetime64("2022-08-08T16:00"),
            np.timedelta64(1, "m"),
            dtype="datetime64[ns]",
        ),
    )
