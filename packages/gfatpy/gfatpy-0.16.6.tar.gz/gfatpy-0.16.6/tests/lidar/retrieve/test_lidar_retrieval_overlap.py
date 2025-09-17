from datetime import datetime
from pathlib import Path
from matplotlib.axes import Axes
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from gfatpy.atmo.atmo import generate_meteo_profiles
from gfatpy.atmo.ecmwf import get_ecmwf_temperature_pressure
from gfatpy.lidar.retrieval.overlap import overlap_function_explicit, overlap_iterative_raman, overlap_iterative_klett


from gfatpy.lidar.retrieval.synthetic.generator import synthetic_signals
from gfatpy.lidar.utils.utils import signal_to_rcs
from gfatpy.utils.plot import color_list

def test_overlap_iterative_raman():
    elastic_wavelength = 532.
    raman_wavelength = 531.

    z = np.arange(3.75, 30000, 3.75)

    lr_part = 45.
    meteo_profiles = get_ecmwf_temperature_pressure(datetime(2021, 1, 1), 0, z)
    P_elastic, P_raman, params = synthetic_signals(
        z,
        (elastic_wavelength, raman_wavelength),
        synthetic_beta=(0.0, 6e-6),
        overlap_midpoint=500.,        
        ae=1.0,
        lr=lr_part,
        apply_overlap=True,
        meteo_profiles=(np.array(meteo_profiles['pressure']), np.array(meteo_profiles['temperature'])),
        force_zero_aer_after_bin= int(6000/3.75)
    )

    #Convert P_elastic and P_raman from numpy.ndarray to xarray.DataArray
    P_elastic = xr.DataArray(P_elastic, dims=('range',), coords={'range': z})
    P_raman = xr.DataArray(P_raman, dims=('range',), coords={'range': z}) 

    iteration_limit = 20
    if isinstance(params['particle_angstrom_exponent'], tuple):
        part_ae = params['particle_angstrom_exponent'][0]
    else: 
        part_ae = params['particle_angstrom_exponent']
    dataset = overlap_iterative_raman(
        P_elastic,
        P_raman,
        meteo_profiles,
        lr_part,
        wavelengths=(elastic_wavelength, raman_wavelength),
        reference=(7000, 7005),
        iteration_limit=iteration_limit,
        particle_angstrom_exponent=part_ae,
        debugging=True

    )

    # Figure
    colors = color_list(iteration_limit)
    fig, ax = plt.subplots(ncols=4, nrows=1, figsize=(15, 7), sharey=True)
    if isinstance(ax, Axes):
        ax = [ax]
    # Plot  corrected RCS
    for i in range(iteration_limit):
        signal_to_rcs(dataset.corrected_signal.sel(iteration=i),dataset.range).plot(y='range', color=colors[i], ax=ax[0], label=f"Iter {i}")
    ax[0].set_xlabel("Corrected signal")
    ax[0].set_ylabel("Altitude [m]")
    ax[0].set_ylim(0, 4000)

    # Plot overlap function
    for i in range(iteration_limit):
        dataset.overlap_function_matrix.sel(iteration=i).plot(y='range', color=colors[i], ax=ax[1], label=f"Iter {i}")
    ax[1].plot(params['overlap'], z, color='black', linestyle='--', label="Synthetic")
    ax[1].set_xlabel("Overlap function")
    ax[1].set_ylabel("")
    ax[1].set_ylim(0, 4000)

    # Plot beta klett matrix and Raman backscatter
    for i in range(iteration_limit):
        (1e6*dataset.elastic_backscatter_matrix.sel(iteration=i)).plot(y='range', color=colors[i], ax=ax[2], label=f"Iter {i}")
    ax[2].plot(1e6*params['particle_beta'], z, label="Synthetic", linestyle="-", color="grey", linewidth=3)
    (1e6*dataset.raman_backscatter).plot(y='range', ax=ax[2], label="Raman", linestyle="--", color="black")
    ax[2].set_xlabel("Backscatter [Mm^-1sr^-1]")

    ax[2].set_ylabel("")
    ax[2].set_ylim(0, 4000)

    # Relative difference
    for i in range(iteration_limit):
        relative_difference = np.divide(dataset.elastic_backscatter_matrix.sel(iteration=i).values - params['particle_beta'], 
                                        params['particle_beta'], 
                                        out=np.full_like(params["particle_beta"], np.nan),
                                        where=params["particle_beta"] != 0
                                        )
        ax[3].plot(relative_difference,z, color=colors[i], label=f"Iter {i}")
    ax[3].plot(np.zeros_like(z), z, color='black', linestyle='--')
    ax[3].set_xlabel("Rel. difference, [%]")
    ax[3].set_ylabel("")
    ax[3].set_xlim(-0.05, 0.01)
    ax[3].set_ylim(0, 4000)

    legend_fontsize = 8
    for ax_ in ax:
        ax_.grid()
        ax_.set_ylim(0, 4000)
        ax_.legend(fontsize=legend_fontsize)

    
    fig.tight_layout()
    output_dir = Path(__file__).parent.parent.parent / 'figures'
    fig.savefig(output_dir / "overlap_iterative_raman.png", bbox_inches='tight')
    plt.close(fig)

    idx = np.logical_and(z>1000. ,z<1200.)
    assert np.allclose(dataset['overlap_function'][idx], params['overlap'][idx], rtol=1)

def test_overlap_iterative_klett():
    elastic_wavelength = 532.

    z = np.arange(3.75, 30000, 3.75)

    lr_part = 45.
    meteo_profiles = get_ecmwf_temperature_pressure(datetime(2021, 1, 1), 0, z)
    ff_P_elastic, _, ff_params = synthetic_signals(
        z,
        elastic_wavelength,
        synthetic_beta=(0.0, 6e-6),
        overlap_midpoint=1400.,        
        ae=1.0,
        lr=lr_part,
        apply_overlap=True,
        meteo_profiles=(np.array(meteo_profiles['pressure']), np.array(meteo_profiles['temperature'])),
        force_zero_aer_after_bin= int(6000/3.75)
    )

    nf_P_elastic, _, nf_params = synthetic_signals(
        z,
        elastic_wavelength,
        synthetic_beta=(0.0, 6e-6),
        overlap_midpoint=200.,        
        ae=1.0,
        lr=lr_part,
        apply_overlap=True,
        meteo_profiles=(np.array(meteo_profiles['pressure']), np.array(meteo_profiles['temperature'])),
        force_zero_aer_after_bin= int(6000/3.75)
    )


    #Convert P_elastic and P_raman from numpy.ndarray to xarray.DataArray
    ff_P_elastic = xr.DataArray(ff_P_elastic, dims=('range',), coords={'range': z})
    nf_P_elastic = xr.DataArray(nf_P_elastic, dims=('range',), coords={'range': z}) 

    iteration_limit = 20
    dataset = overlap_iterative_klett(
        ff_P_elastic,
        nf_P_elastic,
        meteo_profiles,
        lr_part,
        wavelength=elastic_wavelength,
        reference=(7000, 7005),
        iteration_limit=iteration_limit,
        debugging=True
    )

    # Figure
    colors = color_list(iteration_limit)
    fig, ax = plt.subplots(ncols=4, nrows=1, figsize=(15, 7), sharey=True)
    if isinstance(ax, Axes):
        ax = [ax]
    # Plot  corrected RCS
    for i in range(iteration_limit):
        signal_to_rcs(dataset.corrected_signal.sel(iteration=i),dataset.range).plot(y='range', color=colors[i], ax=ax[0], label=f"Iter {i}")
    ax[0].set_xlabel("Corrected signal")
    ax[0].set_ylabel("Altitude [m]")
    ax[0].set_ylim(0, 4000)

    # Plot overlap function
    ax[1].plot(ff_params['overlap'], z, color='black', linestyle='--', lw=3, label="Synthetic FF")
    ax[1].plot(nf_params['overlap'], z, color='black', linestyle=':', lw=3, label="Synthetic NF")
    for i in range(iteration_limit):
        dataset.overlap_function_matrix.sel(iteration=i).plot(y='range', color=colors[i], ax=ax[1], label=f"Iter {i}")
    ax[1].set_xlabel("Overlap function")
    ax[1].set_ylabel("")
    ax[1].set_ylim(0, 4000)

    # Plot beta klett matrix and Raman backscatter
    (1e6*dataset.nf_elastic_backscatter).plot(y='range', ax=ax[2], label="NF Klett", linestyle="--", lw=3, color="black")
    for i in range(iteration_limit):
        (1e6*dataset.elastic_backscatter_matrix.sel(iteration=i)).plot(y='range', color=colors[i], ax=ax[2], label=f"Iter {i}")
    ax[2].plot(1e6*nf_params['particle_beta'], z, label="NF synthetic", linestyle="-", color="grey", linewidth=3)
    ax[2].set_xlabel("Backscatter [Mm^-1sr^-1]")

    ax[2].set_ylabel("")
    ax[2].set_ylim(0, 4000)

    # Relative difference
    for i in range(iteration_limit):
        relative_difference = (dataset['overlap_function_matrix'].sel(iteration=i).values - ff_params['overlap'])/ff_params['overlap']
        ax[3].plot(relative_difference,z, color=colors[i], label=f"Iter {i}")
    ax[3].plot(np.zeros_like(z), z, color='black', linestyle='--')
    ax[3].set_xlabel("O(z) rel. difference, [%]")
    ax[3].set_ylabel("")
    ax[3].set_xlim(-0.05, 1)
    ax[0].set_ylim(0, 4000)

    legend_fontsize = 8
    for ax_ in ax:
        ax_.grid()
        ax_.set_ylim(0, 4000)
        ax_.legend(fontsize=legend_fontsize)

    
    fig.tight_layout()
    output_dir = Path(__file__).parent.parent.parent / 'figures'
    fig.savefig(output_dir / "overlap_iterative_klett.png", bbox_inches='tight')
    plt.close(fig)

    assert np.allclose(dataset['overlap_function'], ff_params['overlap'], rtol=10)

def test_overlap_function_explicit():
    elastic_wavelength = 532.
    raman_wavelength = 531.

    z = np.arange(3.75, 15000, 3.75).astype(np.float64)

    lr_part = 45.
    meteo_profiles = generate_meteo_profiles(z)

    P_elastic, P_raman, params = synthetic_signals(
        z,
        (elastic_wavelength, raman_wavelength),
        synthetic_beta=(0.0, 6e-6),
        overlap_midpoint=500.,        
        ae=1.0,
        lr=lr_part,
        apply_overlap=True,
        meteo_profiles=(np.array(meteo_profiles['pressure']), np.array(meteo_profiles['temperature'])),
        force_zero_aer_after_bin= int(6000/3.75)
    )

    #Convert P_elastic and P_raman from numpy.ndarray to xarray.DataArray
    P_elastic = xr.DataArray(P_elastic, dims=('range',), coords={'range': z})
    P_raman = xr.DataArray(P_raman, dims=('range',), coords={'range': z}) 
    reference_height = (8500.,8550.)

    dataset = overlap_function_explicit(
        signal_to_rcs(P_elastic, P_elastic.range),
        signal_to_rcs(P_raman, P_raman.range),
        (elastic_wavelength, raman_wavelength),
        reference_height,
        lr_part,
        meteo_profiles,
        debugging=True
    )

    # Figure
    fig, ax = plt.subplots(ncols=4, nrows=1, figsize=(15, 7), sharey=True)
    if isinstance(ax, Axes):
        ax = [ax]
    # Plot  corrected RCS
    assert 'nbeta_mol' in dataset.keys()
    assert 'nXR' in dataset.keys()
    dataset['nbeta_mol'].plot(y='range', ax=ax[0], color='r', label='XR') # type: igonore
    dataset['nXR'].plot(y='range', ax=ax[0], color='g', label='XRA') # type: igonore
    ax[0].set_xlabel("Norm. signal")
    ax[0].set_ylabel("Altitude [m]")
    # ax[0].set_xlim(0,1.05)
    ax[0].set_ylim(0, 4000)

    # Plot overlap function
    assert 'overlap_function' in dataset
    dataset['overlap_function'].plot(y='range', ax=ax[1], color='b', label='Overlap') # type: ignore
    ax[1].plot(params['overlap'], z, color='black', linestyle='--', label="Synthetic")
    ax[1].set_xlabel("Overlap function")
    ax[1].set_ylabel("")
    ax[1].set_xlim(0,1.05)
    ax[1].set_ylim(0, 4000)

    # Relative difference
    relative_difference = 100*(dataset['overlap_function'].values-params['overlap'])/params['overlap']
    ax[2].plot(relative_difference,z, label='rel diff')
    ax[2].plot(np.zeros_like(z), z, color='black', linestyle='--')
    ax[2].set_xlabel("Rel. difference, [%]")
    ax[2].set_ylabel("")
    ax[2].set_xlim(-1., 1.)
    ax[2].set_ylim(0, 4000)

    #Plot phi * fexp_phi_psi * fint_g_psi 
    assert all(var  in dataset for var in ['phi', 'fexp_phi_psi', 'fint_g_psi'])
    (dataset['phi']*dataset['fexp_phi_psi']*dataset['fint_g_psi']).plot(y='range', ax=ax[3], color='r', label="phi * fexp_phi_psi * fint_g_psi") #type: ignore
    ax[3].set_xlabel("phi * fexp_phi_psi * fint_g_psi", fontsize=8)
    ax[3].set_ylabel("")
    ax[3].set_ylim(0, 4000)

    legend_fontsize = 8
    for ax_ in ax:
        ax_.grid()
        ax_.set_ylim(0, 4000)
        ax_.legend(fontsize=legend_fontsize)
    
    fig.tight_layout()
    output_dir = Path(__file__).parent.parent.parent / 'figures'
    fig.savefig(output_dir / "overlap_explicit.png", bbox_inches='tight')
    plt.close(fig)

    idx = np.logical_and(z>1000. ,z<1200.)
    assert np.allclose(dataset['overlap_function'].values[idx], params['overlap'][idx], rtol=0.5)
