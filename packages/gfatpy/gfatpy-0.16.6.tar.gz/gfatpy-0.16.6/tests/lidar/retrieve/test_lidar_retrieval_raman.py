from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from gfatpy.lidar.retrieval.raman import (
    retrieve_extinction,
    retrieve_backscatter,
    retrieve_extinction_deprecated,
)
from gfatpy.lidar.retrieval.synthetic.generator import synthetic_signals
from gfatpy.lidar.utils.utils import refill_overlap, signal_to_rcs


def test_retrieve_raman_no_overlap():
    z = np.arange(3.75, 30000, 3.75)

    lr_part = 45.0
    P_elastic, P_raman, params = synthetic_signals(
        z,
        (532, 607),
        synthetic_beta=(0.0, 6e-6),
        overlap_midpoint=500.0,
        ae=1.0,
        lr=lr_part,
        apply_overlap=False,
    )

    alpha_part_ansmann = retrieve_extinction_deprecated(
        P_raman,
        z,
        (532, 607),
        params["pressure"],
        params["temperature"],
        window_size_m=25,
    )

    alpha_part_from_aod = retrieve_extinction(
        P_raman, z, (532, 607), params["pressure"], params["temperature"], reference=(7000., 8000.)
    )

    beta_part_gfatpy = retrieve_backscatter(
        P_raman,
        P_elastic,
        alpha_part_from_aod,
        z,
        (532, 607),
        params["pressure"],
        params["temperature"],
        reference=(7000., 8000.),
        particle_angstrom_exponent=params["particle_angstrom_exponent"][0],
    )

    R = beta_part_gfatpy / params["molecular_beta"] + 1
    LR_profile = alpha_part_ansmann / beta_part_gfatpy
    LR_profile_aod = alpha_part_from_aod / beta_part_gfatpy
    z = z / 1e3
    fig, ax = plt.subplots(ncols=4, nrows=1, figsize=(10, 5), sharey=True)
    # Plot RCS_raman
    ax[0].plot(signal_to_rcs(P_elastic, 1e3 * z), z, lw=2, label="elastic")
    ax[0].plot(signal_to_rcs(P_raman, 1e3 * z), z, lw=2, label="raman")
    ax[0].set_xscale("log")
    ax[0].set_xlim(1, 1e6)
    ax[0].set_xlabel("RCS, [a.u.]")
    ax[0].legend(loc="upper right", fontsize=8)

    # Plot Extinction
    ax[1].plot(
        1e6 * params["particle_alpha"], z, lw=6, color="black", label="synthetic"
    )
    ax[1].plot(
        1e6 * alpha_part_ansmann, z, lw=4, color="lightgreen", label="GFATPY-Ansmann"
    )
    ax[1].plot(1e6 * alpha_part_from_aod, z, lw=1, color="purple", label="GFATPY-AOD")
    ax[1].plot(
        1e6 * params["molecular_alpha"],
        z,
        lw=2,
        color="darkgreen",
        label=r"$\alpha_{m}^{elastic}$",
    )
    ax[1].plot(
        1e6 * params["molecular_alpha_raman"],
        z,
        lw=2,
        color="darkred",
        label=r"$\alpha_{m}^{raman}$",
    )
    ax[1].set_xscale("linear")
    ax[1].set_yticklabels([])
    ax[1].set_xlim(-5, 300)
    ax[1].set_xlabel(r"$\alpha_{p} [Mm^{-1}]$")
    ax[1].legend(loc="upper right", fontsize=8)

    ax[2].plot(1e6 * params["particle_beta"], z, lw=4, color="black", label="synthetic")
    ax[2].plot(
        1e6 * beta_part_gfatpy, z, lw=2, color="lightgreen", label="GFATPY particle"
    )
    ax[2].plot(
        1e6 * params["molecular_beta"],
        z,
        lw=2,
        color="green",
        label=r"$\beta_{m}^{elastic}$",
    )
    ax[2].plot(
        1e6 * params["molecular_beta_raman"],
        z,
        lw=2,
        color="red",
        label=r"$\beta_{m}^{raman}$",
    )
    # ax[2].plot(1e6 * beta_aer_gfatpy, z, lw=2, color="lightblue", label="GFATPY aer")
    ax[2].set_xscale("linear")
    ax[2].set_yticklabels([])
    ax[2].set_xlabel(r"$\beta_{p} [Mm^{-1}\cdot sr^{-1}]$")
    ax[2].legend(loc="upper right", fontsize=8)

    ax[3].plot(
        np.divide(params["particle_alpha"],
                  params["particle_beta"], 
                  out=np.full_like(params["particle_beta"], np.nan),
                  where=params["particle_beta"] != 0
                  ),
        z,
        lw=4,
        color="black",
        label="synthetic",
    )
    ax[3].plot(
        LR_profile[R > 3], z[R > 3], lw=2, color="lightgreen", label="GFATPY-Ansmann"
    )
    ax[3].plot(
        LR_profile_aod[R > 3], z[R > 3], lw=2, color="purple", label="GFATPY-AOD"
    )
    ax[3].set_xscale("linear")
    ax[3].set_yticklabels([])
    ax[3].set_xlim(43, 47)
    ax[3].set_xlabel("LR [sr]")
    ax[3].legend(loc="upper right", fontsize=8)

    # Affect to all axis
    ax[0].set_ylim(0, 8)
    ax[0].set_ylabel("Altitude, [km]")
    yticks = ax[0].get_yticks()
    ax[0].set_yticks(yticks)
    ax[0].set_yticklabels(yticks)

    fig.tight_layout()

    test_figures_dir = Path("./tests/figures")
    if not test_figures_dir.exists():
        test_figures_dir.mkdir(parents=True)
    fig.savefig(test_figures_dir / "test_retrieve_raman_no_overlap.png", dpi=600)
    plt.close(fig)

    idx = np.logical_and.reduce([~np.isnan(alpha_part_from_aod), ~np.isnan(params["particle_alpha"]), R>3.])
    assert np.allclose(
        alpha_part_from_aod[idx], params["particle_alpha"][idx], atol=1e-4
    )
    assert np.allclose(
        beta_part_gfatpy[idx], params["particle_beta"][idx], atol=1e-4
    )
    assert np.allclose(LR_profile[np.logical_and(~np.isnan(LR_profile), R>3.)], lr_part, atol=1.0)


def test_retrieve_raman_overlap():

    z = np.arange(3.75, 30000, 3.75)

    lr_part = 45.0
    P_elastic, P_raman, params = synthetic_signals(
        z,
        (532, 607),
        synthetic_beta=(0.0, 6e-6),
        overlap_midpoint=500.0,
        ae=1.0,
        lr=lr_part,
        apply_overlap=True,
    )

    alpha_part_gfatpy = retrieve_extinction(
        P_raman,
        z,
        (532, 607),
        params["pressure"],
        params["temperature"],
        window_size_m=25,
        reference=(7000., 8000.),
    )

    # Refill extinction from surface to 2 km
    alpha_part_gfatpy = refill_overlap(alpha_part_gfatpy, z, 2000.0)

    beta_part_gfatpy = retrieve_backscatter(
        P_raman,
        P_elastic,
        alpha_part_gfatpy,
        z,
        (532, 607),
        params["pressure"],
        params["temperature"],
        reference=(7000., 8000.),
        particle_angstrom_exponent=params["particle_angstrom_exponent"][0],
    )

    R = beta_part_gfatpy / params["molecular_beta"] + 1
    LR_profile = alpha_part_gfatpy / beta_part_gfatpy

    z = z / 1e3
    fig, ax = plt.subplots(ncols=4, nrows=1, figsize=(10, 5), sharey=True)
    
    # Plot RCS_raman
    ax[0].plot(signal_to_rcs(P_elastic, 1e3 * z), z, lw=2, label="elastic")
    ax[0].plot(signal_to_rcs(P_raman, 1e3 * z), z, lw=2, label="raman")
    ax[0].set_xscale("log")
    ax[0].set_xlim(1, 1e6)
    ax[0].set_xlabel("RCS, [a.u.]")
    ax[0].legend(loc="upper right", fontsize=8)

    # Plot Extinction
    ax[1].plot(
        1e6 * params["particle_alpha"], z, lw=4, color="black", label="synthetic"
    )
    ax[1].plot(1e6 * alpha_part_gfatpy, z, lw=2, color="lightgreen", label="GFATPY")
    ax[1].plot(
        1e6 * params["molecular_alpha"],
        z,
        lw=2,
        color="darkgreen",
        label=r"$\alpha_{m}^{elastic}$",
    )
    ax[1].plot(
        1e6 * params["molecular_alpha_raman"],
        z,
        lw=2,
        color="darkred",
        label=r"$\alpha_{m}^{raman}$",
    )
    ax[1].set_xscale("linear")
    ax[1].set_yticklabels([])
    ax[1].set_xlim(-5, 300)
    ax[1].set_xlabel(r"$\alpha_{p} [Mm^{-1}]$")
    ax[1].legend(loc="upper right", fontsize=8)

    ax[2].plot(1e6 * params["particle_beta"], z, lw=4, color="black", label="synthetic")
    ax[2].plot(
        1e6 * beta_part_gfatpy, z, lw=2, color="lightgreen", label="GFATPY particle"
    )
    ax[2].plot(
        1e6 * params["molecular_beta"],
        z,
        lw=2,
        color="green",
        label=r"$\beta_{m}^{elastic}$",
    )
    ax[2].plot(
        1e6 * params["molecular_beta_raman"],
        z,
        lw=2,
        color="red",
        label=r"$\beta_{m}^{raman}$",
    )
    # ax[2].plot(1e6 * beta_aer_gfatpy, z, lw=2, color="lightblue", label="GFATPY aer")
    ax[2].set_xscale("linear")
    ax[2].set_yticklabels([])
    ax[2].set_xlabel(r"$\beta_{p} [Mm^{-1}\cdot sr^{-1}]$")
    ax[2].legend(loc="upper right", fontsize=8)

    ax[3].plot(
        np.divide(params["particle_alpha"], 
                  params["particle_beta"],
                  out=np.full_like(params["particle_beta"], np.nan),
                  where=params["particle_beta"] !=0
                  ),
        z,
        lw=4,
        color="black",
        label="synthetic",
    )
    ax[3].plot(LR_profile[R > 3], z[R > 3], lw=2, color="lightgreen", label="GFATPY")
    ax[3].set_xscale("linear")
    ax[3].set_yticklabels([])
    ax[3].set_xlim(43, 47)
    ax[3].set_xlabel("LR [sr]")
    ax[3].legend(loc="upper right", fontsize=8)

    # Affect to all axis
    ax[0].set_ylim(0, 8)
    ax[0].set_ylabel("Altitude, [km]")
    yticks = ax[0].get_yticks()
    ax[0].set_yticks(yticks)
    ax[0].set_yticklabels(yticks)

    fig.tight_layout()

    test_figures_dir = Path("./tests/figures")
    if not test_figures_dir.exists():
        test_figures_dir.mkdir(parents=True)
    fig.savefig(test_figures_dir / "test_retrieve_raman_with_overlap.png")
    plt.close(fig)
    assert np.allclose(
        alpha_part_gfatpy[R > 3.0], params["particle_alpha"][R > 3.0], atol=1e-4
    )
    assert np.allclose(
        beta_part_gfatpy[R > 3.0], params["particle_beta"][R > 3.0], atol=1e-4
    )
    assert np.allclose(LR_profile[R > 3.0], lr_part, atol=1.0)
