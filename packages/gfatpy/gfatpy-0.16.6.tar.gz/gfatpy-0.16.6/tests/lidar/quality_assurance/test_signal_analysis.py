from datetime import datetime
from pathlib import Path

import numpy as np

from gfatpy.lidar.preprocessing.lidar_preprocessing import preprocess
from gfatpy.lidar.utils.get_reference_range import get_reference_range
from gfatpy.atmo.ecmwf import get_ecmwf_temperature_pressure
from gfatpy.atmo.atmo import generate_meteo_profiles


def test_get_reference_height(linc_files: None):
    RS_FL = Path(
        r"tests\datos\PRODUCTS\alhambra\1a\2023\08\30\alh_1a_Prs_rs_xf_20230830_0315.nc"
    )
    output_dir = Path("tests/datos/PRODUCTS/alhambra/QA/rayleigh_fit/2023/08/30")
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # Preprocessing lidar data
    rf_dataset = preprocess(RS_FL, apply_dc=True)
    is_dask = rf_dataset["signal_532fta"].data.dask

    initial_date, final_date = datetime(2023, 8, 30, 3, 15, 0), datetime(
        2023, 8, 30, 3, 30, 0
    )

    # Meteo profiles from ECMWF
    meteo_profiles = get_ecmwf_temperature_pressure(
        initial_date, initial_date.hour, rf_dataset.range.values
    )
    meteo_profiles = generate_meteo_profiles(
        rf_dataset.range.values,
        meteo_profiles["pressure"],  # type: ignore
        meteo_profiles["temperature"],  # type: ignore
    )

    if is_dask:
        signal = (
            rf_dataset["signal_532fta"]
            .sel(time=slice(initial_date, final_date))
            .compute()
            .mean("time")
        )
    else:
        signal = (
            rf_dataset["signal_532fta"]
            .sel(time=slice(initial_date, final_date))
            .mean("time")
        )

    final_reference_range = get_reference_range(
        channel="532fta",
        signal=signal,
        meteo_profiles=meteo_profiles,
        reference_candidate_limits=(4000, 8000),
    )

    assert final_reference_range == (6500, 7500)
