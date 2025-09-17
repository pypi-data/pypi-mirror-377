from pathlib import Path

from matplotlib.axes import Axes
import numpy as np
import matplotlib.pyplot as plt

from gfatpy.atmo.ecmwf import get_ecmwf_temperature_pressure
from gfatpy.atmo.rayleigh import molecular_properties
from gfatpy.lidar.preprocessing.lidar_preprocessing import preprocess
from gfatpy.lidar.retrieval.klett import (
    get_calibration_factor,
    iterative_beta,
    klett_rcs,
    quasi_beta,
)
from gfatpy.lidar.retrieval.synthetic.generator import synthetic_signals
from gfatpy.lidar.utils.utils import signal_to_rcs


def test_retrieve_klett():
    z = np.arange(3.75, 20000, 3.75)

    P_elastic, _, params = synthetic_signals(
        z,
        532,
        synthetic_beta=(3e-6, 9e-6),
        ae=(1.5, 0.5),
        lr=(80.0, 45.0),
        sigmoid_edge=(2500.0, 5000.0),
        apply_overlap=False,
    )
    P_elastic, _, params = synthetic_signals(
        z,
        532,
        synthetic_beta=(3e-6, 9e-6),
        ae=(1.5, 0.5),
        lr=(80.0, 45.0),
        sigmoid_edge=(2500.0, 5000.0),
        apply_overlap=False,
    )

    # lr_part = params["particle_alpha"] / params["particle_beta"]
    lr_part = np.divide(
        params["particle_alpha"],
        params["particle_beta"],
        out=np.full_like(params["particle_alpha"], 0.0),  # Default output
        where=params["particle_beta"] != 0  # Only divide where beta is nonzero
        )
    # lr_part[np.isnan(lr_part)] = 0.0
    rcs = signal_to_rcs(P_elastic, z)
    reference_height = (8009, 8011)  # (8000, 8500)
    klett_beta_gfatpy = klett_rcs(
        rcs,
        range_profile=z,
        beta_mol_profile=params["molecular_beta"],
        lr_part=lr_part,
        reference=reference_height,  # (8000, 8500)
    )

    fig, ax = plt.subplots(ncols=3, nrows=1, figsize=(10, 5), sharey=True)

    if isinstance(ax, Axes):
        ax = [ax]

    # Plot RCS
    ax[0].plot(P_elastic * z**2, z, lw=2, label="elastic")
    ax[0].set_xscale("log")
    ax[0].set_xlim(1e1, 1e6)
    ax[0].set_ylim(0, 9000)
    ax[0].set_xlabel("RCS, [a.u.]")
    ax[0].legend()

    ax[1].plot(1e6 * params["particle_beta"], z, lw=4, color="black", label="synthetic")
    ax[1].plot(1e6 * klett_beta_gfatpy, z, lw=2, color="lightgreen", label="GFATPY")
    ax[1].set_xscale("linear")
    ax[1].set_xlim(-0.5, 25)
    ax[1].set_xlabel(r"$\beta_{p} [Mm^{-1}\cdot sr^{-1}]$")
    ax[1].legend()

    ax[2].plot(
        100 *np.divide((klett_beta_gfatpy - params["particle_beta"]), params["particle_beta"],  
                out=np.full_like(params["particle_beta"], 0.0),  # Default output
        where=params["particle_beta"] != 0),  # Only divide where beta is nonzero
        z,
        lw=4,
        color="black",
    )
    # plot vertical line at 0
    ax[2].axvline(x=0, color="black", linestyle="--")
    ax[2].set_xscale("linear")
    ax[2].set_xlim(-0.005, 0.005)
    # scientific notation in x axis
    ax[2].ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
    ax[2].set_xlabel(r"$\varepsilon_{\beta_{p}}$ [%]")

    fig.tight_layout()

    test_figures_dir = Path("./tests/figures")
    if not test_figures_dir.exists():
        test_figures_dir.mkdir(parents=True)
    fig.savefig(test_figures_dir / "test_retrieve_klett.png")
    plt.close(fig)
    test_figures_dir = Path("./tests/figures")
    if not test_figures_dir.exists():
        test_figures_dir.mkdir(parents=True)
    fig.savefig(test_figures_dir / "test_retrieve_klett.png")
    plt.close(fig)

    # plot histogram of the values in the calibration range.
    fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(5, 5))
    if isinstance(ax, Axes):
        ax = [ax]

    calib_range = np.where((z > reference_height[0]) & (z < reference_height[1]))
    ax[0].hist(rcs[calib_range], bins=20, color="lightgreen", alpha=0.75, label="RCS")
    # add vertical line at the middle of the calibration range
    ax[0].axvline(
        x=float(np.mean(rcs[calib_range])), color="red", linestyle="--", label="Mean RCS"
    )
    # add exact value at the middle of the calibration range
    middle_height = (reference_height[0] + reference_height[1]) / 2
    middle_range_idx = int(middle_height / (z[1] - z[0]))
    ax[0].axvline(
        x=rcs[middle_range_idx],
        color="black",
        linestyle="--",
        label=f"RCS@{middle_height} m",
    )
    ax[0].set_ylabel("Counts")
    ax[0].set_xlabel("RCS [a.u.]")
    ax[0].legend()
    ax[1].hist(
        params["molecular_beta"][calib_range],
        bins=20,
        color="blue",
        alpha=0.75,
        label="Molecular",
    )
    ax[1].axvline(
        x=float(np.mean(params["molecular_beta"][calib_range])),
        color="red",
        linestyle="--",
        label="Mean Molecular",
    )
    ax[1].axvline(
        x=params["molecular_beta"][middle_range_idx],
        color="black",
        linestyle="--",
        label=f"RCS@{middle_height} m",
    )
    ax[1].set_xlabel(r"$\beta_{m} [Mm^{-1}\cdot sr^{-1}]$")
    mean_ratio = np.mean(
        rcs[calib_range] / np.mean(params["molecular_beta"][calib_range])
    )
    ax[0].set_title(f"Mean: {mean_ratio:.3e}")
    exact_ratio = rcs[middle_range_idx] / params["molecular_beta"][middle_range_idx]
    rel_diff = 100* np.abs((mean_ratio - exact_ratio.values)/ exact_ratio.values)  
                
    ax[1].set_title(f"@{middle_height} m: {exact_ratio:.3e}\n Diff: {rel_diff:.2f}%")

    fig.tight_layout()
    fig.savefig(test_figures_dir / "test_retrieve_klett_histogram.png")
    plt.close(fig)

    assert np.isclose(rel_diff, 0.0042, atol=1e-4)


def test_retrieve_quasi_beta():
    z = np.arange(3.75, 20000, 3.75)

    P_elastic, _, params = synthetic_signals(
        z,
        532,
        synthetic_beta=(1e-7, 0.0),
        ae=(1.5, 0.5),
        lr=(40.0, 45.0),
        sigmoid_edge=(4000.0, 5000.0),
        apply_overlap=False,
    )

    # lr_part = params["particle_alpha"] / params["particle_beta"]
    lr_part = np.divide(
        params["particle_alpha"],
        params["particle_beta"],
        out=np.full_like(params["particle_alpha"], 0.0),  # Default output
        where=params["particle_beta"] != 0  # Only divide where beta is nonzero
        )
    # lr_part[np.isnan(lr_part)] = 0.0
    k_lidar = params["k_lidar"]
    if isinstance(k_lidar, tuple):
        elastic_k_lidar = k_lidar[0]
    else: 
        elastic_k_lidar = k_lidar
    klett_beta_gfatpy = quasi_beta(
        signal_to_rcs(P_elastic, z),
        calibration_factor=elastic_k_lidar,
        range_profile=z,
        params=params,
        lr_part=lr_part,
        full_overlap_height=1300.0,
    )

    fig, ax = plt.subplots(ncols=3, nrows=1, figsize=(10, 5), sharey=True)
    if isinstance(ax, Axes):
        ax = [ax]
    # Plot RCS
    ax[0].plot(P_elastic * z**2, z, lw=2, label="elastic")
    ax[0].set_xscale("log")
    ax[0].set_xlim(1e3, 1e5)
    ax[0].set_ylim(0, 9000)
    ax[0].set_xlabel("RCS, [a.u.]")
    ax[0].legend()

    ax[1].plot(1e6 * params["particle_beta"], z, lw=4, color="black", label="synthetic")
    ax[1].plot(1e6 * klett_beta_gfatpy, z, lw=2, color="lightgreen", label="GFATPY")
    ax[1].set_xscale("linear")
    ax[1].set_xlim(-0.05, 0.25)
    ax[1].set_xlabel(r"$\beta_{p} [Mm^{-1}\cdot sr^{-1}]$")
    ax[1].legend()

    relative_error = 100 *np.divide((klett_beta_gfatpy - params["particle_beta"]), params["particle_beta"],  
                out=np.full_like(params["particle_beta"], 0.0),  # Default output
        where=params["particle_beta"] != 0)  # Only divide where beta is nonzero
    
    relative_error[z > 4000.0] = np.nan
    ax[2].plot(
        relative_error,
        z,
        lw=4,
        color="black",
    )
    # plot vertical line at 0
    ax[2].axvline(x=0, color="black", linestyle="--")
    ax[2].set_xscale("linear")
    ax[2].set_xlim(-15, 15)
    # scientific notation in x axis
    # ax[2].ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
    ax[2].set_xlabel(r"$\varepsilon_{\beta_{p}}$ [%]")

    fig.tight_layout()

    test_figures_dir = Path("./tests/figures")
    if not test_figures_dir.exists():
        test_figures_dir.mkdir(parents=True)
    fig.savefig(test_figures_dir / "test_retrieve_quasi_beta.png")
    plt.close(fig)

    idx = np.where(np.logical_and(z> 3000., z < 4000.0))
    # Check relative difference lower than 10%

    assert np.allclose(klett_beta_gfatpy[idx], params["particle_beta"][idx], rtol=0.1)


def test_retrieve_iterative_beta():
    z = np.arange(3.75, 20000, 3.75)

    P_elastic, _, params = synthetic_signals(
        z,
        532,
        synthetic_beta=(5e-6, 0.0),
        ae=(1.5, 0.5),
        lr=(40.0, 45.0),
        sigmoid_edge=(4000.0, 5000.0),
        apply_overlap=False,
    )

    # lr_part = params["particle_alpha"] / params["particle_beta"]
    lr_part = np.divide(
        params["particle_alpha"],
        params["particle_beta"],
        out=np.full_like(params["particle_alpha"], 0.0),  # Default output
        where=params["particle_beta"] != 0  # Only divide where beta is nonzero
        )
    # lr_part[np.isnan(lr_part)] = 0.0
    
    k_lidar = params["k_lidar"]
    if isinstance(k_lidar, tuple):
        elastic_k_lidar = k_lidar[0]
    else: 
        elastic_k_lidar = k_lidar

    klett_beta_gfatpy = iterative_beta(
        signal_to_rcs(P_elastic, z),
        calibration_factor=elastic_k_lidar,
        range_profile=z,
        params=params,
        lr_part=lr_part,
        full_overlap_height=1300.0,
        free_troposphere_height=4000.0,
        debug=True,
    )
    fig, ax = plt.subplots(ncols=3, nrows=1, figsize=(10, 5), sharey=True)
    if isinstance(ax, Axes):
        ax = [ax]
    # Plot RCS
    ax[0].plot(P_elastic * z**2, z, lw=2, label="elastic")
    ax[0].set_xscale("log")
    ax[0].set_xlim(1e3, 1e5)
    ax[0].set_ylim(0, 9000)
    ax[0].set_xlabel("RCS, [a.u.]")
    ax[0].legend()
    # Plot beta
    ax[1].plot(1e6 * params["particle_beta"], z, lw=4, color="black", label="synthetic")
    ax[1].plot(1e6 * klett_beta_gfatpy, z, lw=2, color="lightgreen", label="GFATPY")
    ax[1].set_xscale("linear")
    ax[1].set_xlim(-0.5, 25)
    ax[1].set_xlabel(r"$\beta_{p} [Mm^{-1}\cdot sr^{-1}]$")
    ax[1].legend()
    # Plot relative error
    relative_error = 100 *np.divide((klett_beta_gfatpy - params["particle_beta"]), params["particle_beta"],  
            out=np.full_like(params["particle_beta"], 0.0),  # Default output
            where=params["particle_beta"] != 0)  # Only divide where beta is nonzero

    relative_error[z > 4000.0] = np.nan
    ax[2].plot(relative_error, z, lw=4, color="black")
    # plot vertical line at 0
    ax[2].axvline(x=0, color="black", linestyle="--")
    ax[2].set_xscale("linear")
    ax[2].set_xlim(-15, 15)
    ax[2].set_xlabel(r"$\varepsilon_{\beta_{p}}$ [%]")

    fig.tight_layout()
    test_figures_dir = Path("./tests/figures")
    if not test_figures_dir.exists():
        test_figures_dir.mkdir(parents=True)
    fig.savefig(test_figures_dir / "test_retrieve_iterative_beta.png")
    plt.close(fig)


def test_get_calibration():
    lidar_file = Path(
        r"tests\datos\PRODUCTS\alhambra\1a\2023\08\30\alh_1a_Prs_rs_xf_20230830_0315.nc"
    )
    lidar = preprocess(
        lidar_file, crop_ranges=(0, 15000.0), apply_dc=True, apply_ov=False
    )

    P_elastic = (
        lidar["signal_532fta"]
        .sel(time=slice("20230830T031500.0", "20230830T034500.0"))
        .mean("time")
        .values
    )
    z = lidar.range.values
    lr_part = 45.0

    # Read ECMWF data
    atmo = get_ecmwf_temperature_pressure("2023-08-30", hour=3, heights=z)
    params = molecular_properties(
        532.0, atmo["pressure"].values, atmo["temperature"].values, heights=z
    )

    # Retrieve beta particle
    beta_part = klett_rcs(
        signal_to_rcs(P_elastic, z),
        range_profile=z,
        beta_mol_profile=params["molecular_beta"],  # type: ignore
        lr_part=lr_part,
        reference=(7000, 8000),
    )

    mean_calib, std_calib = get_calibration_factor(
        P_elastic=P_elastic,
        range_profile=z,
        params=params,
        beta_part_profile=beta_part,
        lr_part=lr_part,
        full_overlap_height=1300.0,
        range_to_average=(1000.0, 4000.0),
        debug=True,
    )

    assert np.allclose(mean_calib, 3833949980859.2354, atol=1e-2)
    assert np.allclose(std_calib, 17571.88727895536, atol=1e-2)


def test_get_calibration_synthetic():
    # Synthetic data
    z = np.arange(3.75, 20000, 3.75)
    P_elastic, _, params = synthetic_signals(
        z,
        532,
        synthetic_beta=(5e-6, 0.0),
        ae=(1.5, 0.5),
        lr=(80.0, 45.0),
        sigmoid_edge=(3000.0, 5000.0),
        apply_overlap=True,
    )

    # lr_part = params["particle_alpha"] / params["particle_beta"]
    lr_part = np.divide(
        params["particle_alpha"],
        params["particle_beta"],
        out=np.full_like(params["particle_alpha"], 0.0),  # Default output
        where=params["particle_beta"] != 0  # Only divide where beta is nonzero
        )
    # lr_part[np.isnan(lr_part)] = 0.0
    # k_synthetic = (P_elastic * z**2/ params['overlap']) / (params["molecular_beta"] + params["particle_beta"]) / params['transmittance_elastic']**2

    # Retrieve beta particle
    beta_part = klett_rcs(
        signal_to_rcs(P_elastic, z),
        range_profile=z,
        beta_mol_profile=params["molecular_beta"],  # type: ignore
        lr_part=lr_part,
        reference=(7000, 8000),
    )

    mean_calib, std_calib = get_calibration_factor(
        P_elastic=P_elastic,
        range_profile=z,
        params=params,
        beta_part_profile=beta_part,
        lr_part=lr_part,
        full_overlap_height=1300.0,
        range_to_average=(2000.0, 3000.0),
        debug=True,
    )    

    assert np.allclose(mean_calib, 95696937095.47034, atol=1e-2)
    assert np.allclose(std_calib, 50248.31048428802, atol=1e-2)
