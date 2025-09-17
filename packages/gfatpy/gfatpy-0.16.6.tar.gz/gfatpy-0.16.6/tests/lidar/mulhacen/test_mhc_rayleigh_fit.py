from pathlib import Path

from gfatpy.lidar.quality_assurance.rayleigh_fit import rayleigh_fit_from_file
from gfatpy.lidar.quality_assurance.plot import plot_rayleigh_fit


def test_rayleigh_fit_from_file(linc_files):
    RS_FL = Path(
        r"./tests/datos/PRODUCTS/mulhacen/1a/2022/08/08/mhc_1a_Prs_rs_xf_20220808_1131.nc"
    )
    output_dir = Path("tests/datos/PRODUCTS/mulhacen/QA/rayleigh_fit/2022/08/08")
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    rayleigh_fit_from_file(
        file=RS_FL,
        channels=["532xpa", "532xpp"],
        initial_hour=20,
        duration=60,
        reference_range=(6000, 7000),
        output_dir=output_dir,
        save_fig=False,
    )

    output_file_532xpa_csv = output_dir / "grRayleighFit532xpa.csv"
    output_file_532xpp_csv = output_dir / "grRayleighFit532xpp.csv"
    
    assert output_file_532xpa_csv.is_file()
    assert output_file_532xpp_csv.is_file()


def test_rayleigh_fit_plot():
    FLS2PLOT = [
        *Path(r"./tests/datos/PRODUCTS/mulhacen/QA/rayleigh_fit/2022/08/08").glob(
            "grRayleighFit*.nc"
        )
    ]
    output_dir = Path("tests/datos/PRODUCTS/mulhacen/QA/rayleigh_fit/2022/08/08")
    plot_rayleigh_fit(
        FLS2PLOT,
        save_fig=True,
        output_dir=output_dir,
    )

    figure_532xpa = output_dir / "grRayleighFit532xpa.csv"
    assert figure_532xpa.is_file()
