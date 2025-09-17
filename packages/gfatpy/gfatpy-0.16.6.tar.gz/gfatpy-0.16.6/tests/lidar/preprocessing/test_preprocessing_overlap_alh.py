#!/usr/bin/env python

from pdb import set_trace
from gfatpy.lidar.preprocessing import preprocess

RS_FL = (
    r"./tests/datos/PRODUCTS/alhambra/1a/2023/08/30/alh_1a_Prs_rs_xf_20230830_0315.nc"
)


def test_preprocessing_overlap_alhambra(linc_files):
    channels = ["532fta", "532ftp", "355fpa", "355fsa"]
    overlap_path = r"./tests/datos/PRODUCTS/alhambra/QA/overlap/overlap_alh_ff_20230830_0314-0359.nc"
    lidar = preprocess(
        RS_FL,
        channels=channels,
        crop_ranges=(0.0, 15000.0),
        gluing_products=False,
        apply_ov=True,
        overlap_path=overlap_path,
    )

    assert lidar["overlap_corrected"].all()
    lidar.close()


def test_preprocessing_overlap_alhambra_gluing(linc_files):
    lidar = preprocess(
        RS_FL,
        crop_ranges=(0.0, 15000.0),
        gluing_products=False,
        apply_ov=True,
    )
    assert bool(lidar["overlap_corrected"].sel(channel="1064fta").values.item())
    assert bool(lidar["overlap_corrected"].sel(channel="532fta").values.item())
    assert bool(lidar["overlap_corrected"].sel(channel="355fpa").values.item())
    lidar.close()
