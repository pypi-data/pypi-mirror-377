from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np

from gfatpy.atmo.freudenthaler_molecular_properties import molecular_properties
from gfatpy.atmo.atmo import standard_atmosphere, transmittance
from gfatpy.atmo.rayleigh import molecular_properties as mol_prop


def test_molecular_properties():
    heights = np.arange(2666) * 7.5
    pressure, temperature, _ = standard_atmosphere(heights)
    molecular_profiles = molecular_properties(
        532, pressure, temperature, heights=heights
    )
    T = transmittance(molecular_profiles["molecular_alpha"].values, heights=heights)
    molecular_properties_adolfo = mol_prop(532, pressure, temperature, heights=heights)
    # T = transmittance(molecular_properties_adolfo, heights=heights)
    # attenuated_mol_beta_adolfo = mol_beta*T**2

    fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(10, 5), sharey=True)
    ax[0].plot(
        1e6 * molecular_profiles["molecular_alpha"],
        heights,
        lw=0,
        marker="o",
        c="r",
        label="Volker",
    )
    ax[0].plot(
        1e6 * molecular_properties_adolfo["molecular_alpha"],
        heights,
        lw=0,
        marker=".",
        c="g",
        label="Adolfo",
    )
    ax[0].set_xscale("linear")
    ax[0].set_xlabel(r"$\alpha_{m}, [Mm^{-1}]$")
    ax[0].set_ylabel("Height, [m]")
    ax[0].legend()

    ax[1].plot(
        1e6 * molecular_profiles["molecular_beta"],
        heights,
        lw=0,
        marker="o",
        c="r",
        label="Volker",
    )
    ax[1].plot(
        1e6 * molecular_properties_adolfo["molecular_beta"],
        heights,
        lw=0,
        marker=".",
        c="g",
        label="Adolfo",
    )
    ax[1].set_xscale("linear")
    ax[1].set_xlabel(r"$\beta_{m}, [Mm^{-1}sr^{-1}]$")
    ax[1].legend()

    test_figures_dir = Path("./tests/figures")
    if not test_figures_dir.exists():
        test_figures_dir.mkdir(parents=True)
    fig.savefig(test_figures_dir / "test_molecular_properties.png")
    plt.close(fig)

    assert np.allclose(
        molecular_profiles["molecular_alpha"],
        molecular_properties_adolfo["molecular_alpha"],
        atol=1e-4,
    )
    assert np.allclose(
        molecular_profiles["molecular_beta"],
        molecular_properties_adolfo["molecular_beta"],
        atol=1e-4,
    )
