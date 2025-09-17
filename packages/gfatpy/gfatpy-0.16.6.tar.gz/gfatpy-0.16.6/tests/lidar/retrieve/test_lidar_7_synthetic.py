from pathlib import Path
from matplotlib import pyplot as plt, ticker
from matplotlib.axes import Axes
import xarray as xr
import numpy as np
from gfatpy.lidar.retrieval.synthetic.generator import synthetic_signals
from gfatpy.lidar.utils.utils import signal_to_rcs


def test_synthetic_signal():
    reference_range = (7000, 8000)
    z = np.arange(3.75, 30000, 3.75, dtype=np.float64)

    lr_part = 45
    P_elastic, P_raman, params = synthetic_signals(
        z,
        (532, 607),
        synthetic_beta=(0.0, 6e-6),
        ae=1.0,
        lr=lr_part,
        apply_overlap=True,
    )
    att_beta_mol = params["attenuated_molecular_backscatter"]

    #convert att_beta_mol to xr.DataArray
    att_beta_mol = xr.DataArray(att_beta_mol, coords=[z], dims=["range"])

    #convert P_elastic to xr.DataArray
    P_elastic = xr.DataArray(P_elastic, coords=[z], dims= ['range'])
    P_raman = xr.DataArray(P_raman, coords=[z], dims= ['range'])

    ref_att_beta_mol = att_beta_mol.where(
        np.logical_and(z > reference_range[0], z < reference_range[1])
    ).mean("range")
    rcs = signal_to_rcs(P_elastic, P_elastic.range)
    n_rcs = ref_att_beta_mol * (
        rcs / rcs.sel(range=slice(*reference_range)).mean("range")
    )

    att_beta_mol_raman = params["attenuated_molecular_backscatter_raman"][0]

    #convert att_beta_mol_raman to xarray
    att_beta_mol_raman = xr.DataArray(att_beta_mol_raman, coords=[z], dims=["range"])

    ref_att_beta_mol_raman = att_beta_mol_raman.where(
        np.logical_and(z > reference_range[0], z < reference_range[1])
    ).mean("range")
    rcs_raman = signal_to_rcs(P_raman, P_raman.range)
    n_rcs_raman = ref_att_beta_mol_raman * (
        rcs_raman / rcs_raman.sel(range=slice(*reference_range)).mean("range")
    )

    fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(10, 5))
    if isinstance(ax, Axes):
        ax = [ax]
    ax[0].grid(which="both", linewidth=1.0)
    ax[0].plot(z / 1e3, att_beta_mol, lw=3, c="k", label="elastic molecular")
    ax[0].plot(z / 1e3, n_rcs, lw=1, c="r", label="elastic lidar")
    ax[0].set_yscale("log")
    ax[0].xaxis.get_label().set_fontsize("medium")
    ax[0].xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax[0].set_ylabel(r"$\beta_{att}, [Mm^{-1}sr^{-1}]$", fontsize="medium")
    ax[0].set_xlabel("Range, km", fontsize="medium")
    ax[0].set_xlim(0, 20)
    # ax[0].set_ylim(*y_lim)
    ax[0].set_yscale("log")
    leg = ax[0].legend(fontsize="medium")
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_facecolor("silver")

    ax[1].grid(which="both", linewidth=1.0)
    ax[1].plot(z / 1e3, att_beta_mol_raman, lw=3, c="k", label="raman molecular")
    ax[1].plot(z / 1e3, n_rcs_raman, lw=1, c="r", label="raman lidar")
    ax[1].set_yscale("log")
    ax[1].xaxis.get_label().set_fontsize("medium")
    ax[1].xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax[1].set_ylabel(r"$\beta_{att}, [Mm^{-1}sr^{-1}]$", fontsize="medium")
    ax[1].set_xlabel("Range, km", fontsize="medium")
    ax[1].set_xlim(0, 20)
    # ax[1].set_ylim(*y_lim)
    ax[1].set_yscale("log")
    leg = ax[1].legend(fontsize="medium")
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_facecolor("silver")

    fig.tight_layout()
    test_figures_dir = Path("./tests/figures")
    if not test_figures_dir.exists():
        test_figures_dir.mkdir(parents=True)
    fig.savefig(test_figures_dir / "test_synthetic_signal.png")
    plt.close(fig)
    assert np.allclose(
        n_rcs[np.logical_and(z > 6000, z < 8000)],
        att_beta_mol[np.logical_and(z > 6000, z < 8000)],
        rtol=1e-4,
    )
