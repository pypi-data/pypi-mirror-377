#!/usr/bin/env python
from pathlib import Path

from gfatpy.lidar.retrieval.overlap import retrieve_ff_overlap as overlap_ff

ALH_FL = (
    r"./tests/datos/PRODUCTS/alhambra/1a/2023/08/30/alh_1a_Prs_rs_xf_20230830_0315.nc"
)


def test_overlap_alhambra(linc_files):
    ovpath = overlap_ff(
        ALH_FL,
        hour_range=(3, 4),
        output_dir=Path(r"./tests/datos/PRODUCTS/alhambra/QA/overlap/"),
        force_to_one_when_full_overlap=False,
    )
    assert ovpath is not None
    assert ovpath.exists()
