import numpy as np

import xarray as xr
from scipy.constants import Boltzmann

from gfatpy.atmo import atmo
from gfatpy.atmo.rayleigh import molecular_properties
from gfatpy.lidar.utils.types import ParamsDict
from gfatpy.lidar.utils.utils import extrapolate_beta_with_angstrom
from gfatpy.lidar.utils.utils import sigmoid


def generate_particle_properties(
    ranges: np.ndarray,
    wavelength: float,
    ae: float | tuple[float, float] = (1.5, 0),
    lr: float | tuple[float, float] = (75, 45),
    synthetic_beta: float | tuple[float, float] = (2.5e-6, 2.0e-6),
    sigmoid_edge: float | tuple[float, float] = (2500, 5000),
) -> np.ndarray:
    """_summary_

    Args:
        ranges (np.ndarray): ranges
        wavelength (float): wavelength
        fine_ae (float): fine-mode Angstrom exponent
        coarse_ae (float): coarse-mode Angstrom exponent
        fine_beta532 (float, optional): fine-mode backscatter coefficient at 532 nm. Defaults to 2.5e-6.
        coarse_beta532 (float, optional): coarse-mode backscatter coefficient at 532 nm. Defaults to 2.0e-6.

    Returns:
        np.ndarray: particle backscatter coefficient profile
    """
    if isinstance(ae, tuple):
        fine_ae = ae[0]
        coarse_ae = ae[1]
    else:
        fine_ae = ae
        coarse_ae = ae

    if isinstance(lr, tuple):
        fine_lr = lr[0]
        coarse_lr = lr[1]
    else:
        fine_lr = lr
        coarse_lr = lr

    if isinstance(sigmoid_edge, tuple):
        sigmoid_edge_fine = sigmoid_edge[0]
        sigmoid_edge_coarse = sigmoid_edge[1]
    else:
        sigmoid_edge_fine = sigmoid_edge
        sigmoid_edge_coarse = sigmoid_edge

    if isinstance(synthetic_beta, tuple):
        fine_beta532 = synthetic_beta[0]
        coarse_beta532 = synthetic_beta[1]
    else:
        fine_beta532 = synthetic_beta
        coarse_beta532 = synthetic_beta

    beta_part_fine_532 = sigmoid(
        ranges, sigmoid_edge_fine, 1 / 60, coeff=-fine_beta532, offset=fine_beta532
    )
    beta_part_coarse_532 = sigmoid(
        ranges,
        sigmoid_edge_coarse,
        1 / 60,
        coeff=-coarse_beta532,
        offset=coarse_beta532,
    )

    beta_part_fine = extrapolate_beta_with_angstrom(
        beta_part_fine_532, 532, wavelength, fine_ae
    )

    beta_part_coarse = extrapolate_beta_with_angstrom(
        beta_part_coarse_532, 532, wavelength, coarse_ae
    )

    beta_total = beta_part_fine + beta_part_coarse

    alpha_part_fine = fine_lr * beta_part_fine
    alpha_part_coarse = coarse_lr * beta_part_coarse

    alpha_total = alpha_part_fine + alpha_part_coarse

    return (
        beta_part_fine,
        beta_part_coarse,
        beta_total,
        alpha_part_fine,
        alpha_part_coarse,
        alpha_total,
    )


def synthetic_signals(
    ranges: np.ndarray,
    wavelengths: float | tuple[float, float] = 532,
    wavelength_raman: float | None = 531,
    overlap_midpoint: float = 800,
    overlap_slope: float = 1 / 150,
    k_lidar: float | tuple[float, float] = (1e11, 1e10), #El coeficiente de ganancias es igual que el coeficiente de k_lidar. Representan la elastica y la raman 
    ae: float | tuple[float, float] = (1.5, 0), #Modo fino y modo grueso
    lr: float | tuple[float, float] = (75, 45),
    synthetic_beta: float | tuple[float, float] = (2.5e-6, 2.0e-6), #Modo fino y modo grueso
    sigmoid_edge: float | tuple[float, float] = (2500, 5000), #Modo fino y modo grueso
    force_zero_aer_after_bin: int | None = None,
    paralell_perpendicular_ratio: float = 0.33, #despo_particle
    meteo_profiles: tuple[np.ndarray, np.ndarray] | None = None,
    apply_overlap: bool = True,
    N: int = 10, #Number of values to eliminate from the signal at the beginning
) -> tuple[np.ndarray, np.ndarray | None, ParamsDict]:
    """It generates synthetic lidar signal.

    Args:
        ranges (np.ndarray): Range
        wavelength (float, optional): Wavelength. Defaults to 532.
        wavelength_raman (float | None, optional): Raman wavelength. Defaults to None. If None, signal is elastic.
        overlap_midpoint (float, optional): _description_. Defaults to 600.
        overlap_slope (float, optional): _description_. Defaults to 1 / 150.
        k_lidar (float | tuple[float, float], optional): Lidar constant calibration. Defaults to 1e11.
        ae (float | tuple[float, float], optional): Angstrom exponent. Defaults to (1.5, 0).
        lr (float | tuple[float, float], optional): Lidar ratio. Defaults to (75, 45).
        synthetic_beta (float | tuple[float, float], optional): Synthetic backscatter coefficient. Defaults to (2.5e-6, 2.0e-6).
        sigmoid_edge (float | tuple[float, float], optional): _description_. Defaults to (2500, 5000).
        force_zero_aer_after_bin (int | None, optional): _description_. Defaults to None.
        meteo_profiles (tuple[np.ndarray, np.ndarray] | None, optional): _description_. Defaults to None.
        apply_overlap (bool, optional): _description_. Defaults to True.
        N (int, optional): Number of values to eliminate from the signal at the beginning. Defaults to 107 (approx 400 m).

    Returns:
        tuple[np.ndarray, ParamsDict]: _description_
    """
    
    z = ranges

    # Overlap
    if apply_overlap:
        overlap = sigmoid(
            z.astype(np.float64),
            overlap_midpoint,
            overlap_slope,
            offset=0.,)

    else:
        overlap = np.ones_like(z)

    if isinstance(lr, float):
        lr = (lr, lr)
    if isinstance(ae, float):
        ae = (ae, ae)
    if isinstance(synthetic_beta, float):
        synthetic_beta = (synthetic_beta, synthetic_beta)

    if isinstance(k_lidar, float):
        k_lidar_elastic = k_lidar
    else:
        k_lidar_elastic, k_lidar_raman = k_lidar

    # Check temperature and pressure profiles
    if meteo_profiles is None:
        P, T, _ = atmo.standard_atmosphere(z)
    else:
        # check length of meteo_profiles with z
        if len(meteo_profiles[0]) != len(z):
            raise ValueError("Length of meteo_profiles must be equal to length of z")
        else:
            P = meteo_profiles[0]
            T = meteo_profiles[1]

    # Check if wavelength is a tuple
    if isinstance(wavelengths, tuple):
        wavelength = wavelengths[0]
        wavelength_raman = wavelengths[1]
    else:
        wavelength = wavelengths
        wavelength_raman = None

    # Generate molecular profiles for elastic wavelength
    mol_properties = molecular_properties(wavelength, P, T, heights=z)
    
    (
        _,
        _,
        beta_part,
        alpha_part_fine,
        alpha_part_coarse,
        alpha_part,
    ) = generate_particle_properties(
        ranges, wavelength, ae=ae, lr=lr, synthetic_beta=synthetic_beta, sigmoid_edge=sigmoid_edge
    )
  
    # Elastic transmittance
    T_elastic = atmo.transmittance(mol_properties["molecular_alpha"] + alpha_part, z)
    
    # Elastic signal
    P_elastic = (
        k_lidar_elastic
        * (overlap / z**2)
        * (mol_properties["molecular_beta"] + beta_part)
        * T_elastic**2
    )
    # Eliminate first N values
    P_elastic[:N] = np.nan
    
    clean_attenuated_molecular_beta = (
        mol_properties["molecular_beta"]
        * atmo.transmittance(mol_properties["molecular_alpha"], z) ** 2
    )

    # Save parameters to create synthetic elastic signal
    params: ParamsDict = {
        "particle_beta": beta_part,
        "particle_alpha": alpha_part,
        "molecular_beta": mol_properties["molecular_beta"],
        "molecular_alpha": mol_properties["molecular_alpha"],
        "lidar_ratio": lr,
        "attenuated_molecular_backscatter": clean_attenuated_molecular_beta,
        "transmittance_elastic": T_elastic,
        "overlap": overlap,
        "k_lidar": k_lidar,
        "particle_angstrom_exponent": ae,
        "synthetic_beta": synthetic_beta,
        "temperature": T,
        "pressure": P,
    }

    # Raman signal
    if wavelength_raman is not None:
        # Generate molecular profiles for raman wavelength
        mol_properties_raman = molecular_properties(wavelength_raman, P, T, heights=z)

        # Alpha particle raman
        alpha_part_fine_raman = alpha_part_fine * (wavelength_raman / wavelength) ** (
            -ae[0]
        )
        alpha_part_coarse_raman = alpha_part_coarse * (
            wavelength_raman / wavelength
        ) ** (-ae[1])
        alpha_part_raman = alpha_part_fine_raman + alpha_part_coarse_raman

        # Transmittance Raman
        T_raman = atmo.transmittance(
            mol_properties_raman["molecular_alpha"] + alpha_part_raman, z
        )
        P_raman = (
            k_lidar_raman
            * (overlap / z**2)
            * mol_properties_raman["molecular_beta"]
            * T_elastic
            * T_raman
        )
        # Eliminate first N values
        P_raman[:N] = np.nan
        
        clean_attenuated_molecular_beta_raman: xr.DataArray = (
            mol_properties_raman["molecular_beta"]
            * atmo.transmittance(mol_properties_raman["molecular_alpha"], z)
            * atmo.transmittance(mol_properties["molecular_alpha"], z)
        )

        params["molecular_alpha_raman"] = mol_properties_raman["molecular_alpha"]
        params["molecular_beta_raman"] = mol_properties_raman["molecular_beta"]
        params["attenuated_molecular_backscatter_raman"] = (
            clean_attenuated_molecular_beta_raman,
        )
        params["transmittance_raman"] = T_raman
        params["overlap"] = overlap

    else:
        P_raman = None

    if force_zero_aer_after_bin is not None:
        alpha_part[force_zero_aer_after_bin:] = 0
        beta_part[force_zero_aer_after_bin:] = 0
        
    return P_elastic, P_raman, params


def synthetic_signals_despo(
    ranges: np.ndarray,
    wavelength: float = 532,
    overlap_midpoint: float = 800,
    overlap_slope: float = 1 / 50, 
    k_lidar_parallel: float  = 1e5, # po*tau/2*c*At. Fijamos Po * tau = 82.4 mJ. La estoy poniendo más baja de lo que debería ser
    k_lidar_perpendicular: float = 1e5, 
    phi: float = 90.0,
    reflectance_transmittance_s_path: tuple[float, float] = (0.99, 0.01),
    reflectance_transmittance_p_path: tuple[float, float] = (0.05, 0.95),
    photomultipliers_gains: tuple[float, float] = (2e6, 2e6), #Hamamatsu R9880U SERIES
    ae: float | tuple[float, float] = (1.5, 0),
    lr: float | tuple[float, float] = (75, 45),
    synthetic_beta: float | tuple[float, float] = (2.5e-6, 2.0e-6),
    sigmoid_edge: float | tuple[float, float] = (2500, 5000),
    force_zero_aer_after_bin: int | None = None,
    despo_particle: float = 0.33, 
    meteo_profiles: tuple[np.ndarray, np.ndarray] | None = None,
    apply_overlap: bool = True,
    N: int = 10, #Numero de valores para eliminar de la señal al inicio
) -> tuple[np.ndarray, np.ndarray | None, ParamsDict]:
    """It generates polarized synthetic lidar signal.

    Args:
        ranges (np.ndarray): Range
        wavelength (float, optional): Elastic wavelength. Defaults to 532.
        overlap_midpoint (float, optional): _description_. Defaults to 800.
        k_lidar_parallel (float, optional): Lidar constant calibration for parallel component withot gain. Defaults to 1e11.
        k_lidar_perpendicular (float, optional): Lidar constant calibration for perpendicular component without. Defaults to 1e11.
        phi (float, optional): Angle between the plane of laser polarization and the incident plane of PBC. Defaults to 90.0 (s-path = parallel-path and p-path=perpendicular path). 
        reflectance_transmittance_s_path (tuple[float, float], optional): Reflectance and transmittance for s-path. Defaults to (0.99, 0.01).
        reflectance_transmittance_p_path (tuple[float, float], optional): Reflectance and transmittance for p-path. Defaults to (0.05, 0.95).
        photomultipliers_ganancies (tuple[float, float], optional): Photomultipliers ganancies for reflected and transmitted signals. Defaults to (0.9, 0.9).                                                                                                                     
        ae (float | tuple[float, float], optional): Ángstrong exponent. Defaults to (1.5, 0).
        lr (float | tuple[float, float], optional): Lidar ratio. Defaults to (75, 45).
        synthetic_beta (float | tuple[float, float], optional): Synthetic backscatter coefficient. Defaults to (2.5e-6, 2.0e-6).
        sigmoid_edge (float | tuple[float, float], optional): _description_. Defaults to (2500, 5000).
        force_zero_aer_after_bin (int | None, optional): _description_. Defaults to None.
        despo_particle (float, optional): Linear particle despolarization ratio. Defaults to 0.33 (dust).
        meteo_profiles (tuple[np.ndarray, np.ndarray] | None, optional): _description_. Defaults to None.
        apply_overlap (bool, optional): _description_. Defaults to True.
        N (int, optional): Number of values to eliminate from the signal at the beginning. Defaults to 10 (approx 40 m).

    Returns:
        tuple[np.ndarray, ParamsDict]: _description_
    """
    
    z = ranges

    # Overlap
    if apply_overlap:
        overlap = sigmoid(
            z.astype(np.float64),
            overlap_midpoint,
            overlap_slope,
            offset=0.,
        )

    else:
        overlap = np.ones_like(z)

    if isinstance(lr, float):
        lr = (lr, lr)
    if isinstance(ae, float):
        ae = (ae, ae)
    if isinstance(synthetic_beta, float):
        synthetic_beta = (synthetic_beta, synthetic_beta)

    if isinstance(k_lidar_parallel, float):
        k_lidar_elastic_parallel = k_lidar_parallel
        
    if isinstance(k_lidar_perpendicular, float):
        k_lidar_elastic_perpendicular = k_lidar_perpendicular
    
    # Check if reflectance_transmittance_s_path components sum 1
    if sum(reflectance_transmittance_s_path) != 1:
        raise ValueError("Sum of reflectance_transmittance_s_path must be equal to 1")
    
    # Check if reflectance_transmittance_p_path components sum 1
    if sum(reflectance_transmittance_p_path) != 1:
        raise ValueError("Sum of reflectance_transmittance_p_path must be equal to 1") 
    
    #Identify the reflectance and transmittance components for the parallel and perpendicular components of the cube
    reflectance_s_path = reflectance_transmittance_s_path[0]
    transmittance_s_path = reflectance_transmittance_s_path[1]
    
    reflectrance_p_path = reflectance_transmittance_p_path[0]
    transmittance_p_path = reflectance_transmittance_p_path[1]  
    
    #Identify the photomultipliers ganancies for the parallel and perpendicular components of the cube
    gain_reflected_path = photomultipliers_gains[0]
    gain_transmitted_path = photomultipliers_gains[1] 
      

    # Check temperature and pressure profiles
    if meteo_profiles is None:
        P, T, _ = atmo.standard_atmosphere(z)
    else:
        # check length of meteo_profiles with z
        if len(meteo_profiles[0]) != len(z):
            raise ValueError("Length of meteo_profiles must be equal to length of z")
        else:
            P = meteo_profiles[0]
            T = meteo_profiles[1]

    # Generate molecular profiles for elastic wavelength
    mol_properties = molecular_properties(wavelength, P, T, heights=z, component="cabannes")
    beta_mol_total= mol_properties['molecular_beta']
    mol_despo = mol_properties['molecular_depolarization']
    
    #Calculate the backscatter coefficient for the parallel and perpendicular components
    beta_mol_parallel = beta_mol_total/(1+mol_despo)
    beta_mol_perpendicular= beta_mol_total - beta_mol_parallel
    
    # Generate particle profiles for elastic wavelength
    (
        _,
        _,
        beta_part,
        alpha_part_fine,
        alpha_part_coarse,
        alpha_part,
    ) = generate_particle_properties(
        ranges, wavelength, ae=ae, lr=lr, synthetic_beta=synthetic_beta, sigmoid_edge=sigmoid_edge
    )
    
    #Calculate the backscatter coefficient for the parallel and perpendicular components
    beta_part_parallel = beta_part/(1+despo_particle)
    beta_part_perpendicular= beta_part - beta_part_parallel
    

    # Elastic transmittance
    # T_elastic = np.exp(-cumulative_trapezoid(alpha_mol+ alpha_part, z, initial=0))  # type: ignore
    T_elastic = atmo.transmittance(mol_properties["molecular_alpha"] + alpha_part, z)
    
    # Elastic signal. T_elastic_parallel and T_elastic_perpendicular are same (aproximation).
    P_elastic_parallel = (
        k_lidar_elastic_parallel
        * (overlap / z**2)
        * (beta_mol_parallel+ beta_part_parallel)
        * T_elastic**2 
    )
    
    P_elastic_perpendicular = (
        k_lidar_elastic_perpendicular
        * (overlap / z**2)
        * (beta_mol_perpendicular+ beta_part_perpendicular)
        * T_elastic**2
    )
    
    P_elastic_parallel[:N] = np.nan
    P_elastic_parallel[:N] = np.nan
    
    #Calculate the volumic depolarization ratio
    despo_volumic= (beta_mol_perpendicular+beta_part_perpendicular)/(beta_mol_parallel+beta_part_parallel) 
    
    #Calculate the attenuation molecular backscatter
    clean_attenuated_molecular_beta_total = (
        beta_mol_total
        * atmo.transmittance(mol_properties["molecular_alpha"], z) ** 2
    )
    
    clean_attenuated_molecular_beta_parallel = (
        beta_mol_parallel
        * atmo.transmittance(mol_properties["molecular_alpha"], z) ** 2
    )
    clean_attenuated_molecular_beta_perpendicular = (
        beta_mol_perpendicular
        * atmo.transmittance(mol_properties["molecular_alpha"], z) ** 2
    )

    #Calculate the particle depolarization ratio
    despo_particle_profile= beta_part_perpendicular/beta_part_parallel    
    despo_particle_profile= np.nan_to_num(despo_particle_profile)
    
    #Calculate the molecular depolarization ratio
    despo_molecular= mol_despo
    
    #Calculate the backscattering ratio R
    R=(beta_mol_total + beta_part)/(beta_mol_total)
    
    #Calculate the signal components with respect to incident plane of the PBC
    
    Ps = P_elastic_parallel * np.sin(np.radians(phi))**2 + P_elastic_perpendicular * np.cos(np.radians(phi))**2
    Pp = P_elastic_parallel * np.cos(np.radians(phi))**2 + P_elastic_perpendicular * np.sin(np.radians(phi))**2
    
    
    #Calculate the reflected and transmitted signals
    P_elastic_reflected = (Pp*reflectrance_p_path + Ps*reflectance_s_path)*gain_reflected_path
    P_elastic_transmitted = (Pp*transmittance_p_path + Ps*transmittance_s_path)*gain_transmitted_path
    
    
    if phi == 0.0:
        reflectance_parallel_path = reflectrance_p_path
        reflectance_perpendicular_path = reflectance_s_path
        transmittance_parallel_path = transmittance_p_path
        transmittance_perpendicular_path = transmittance_s_path
    
    if phi == 90.0:
        reflectance_parallel_path = reflectance_s_path
        reflectance_perpendicular_path = reflectrance_p_path
        transmittance_parallel_path = transmittance_s_path
        transmittance_perpendicular_path = transmittance_p_path
        
    else :
        reflectance_parallel_path = np.nan
        reflectance_perpendicular_path = np.nan
        transmittance_parallel_path = np.nan
        transmittance_perpendicular_path = np.nan
    
    # Save parameters to create synthetic elastic signal
    params: ParamsDict = {
        "particle_beta_total": beta_part,
        "particle_beta_parallel": beta_part_parallel,
        "particle_beta_perpendicular": beta_part_perpendicular,
        "particle_alpha": alpha_part,
        "molecular_beta_total": beta_mol_total,
        "molecular_beta_parallel": beta_mol_parallel,
        "molecular_beta_perpendicular": beta_mol_perpendicular,
        "molecular_alpha": mol_properties["molecular_alpha"],
        "lidar_ratio": lr,
        "attenuated_molecular_backscatter_total": clean_attenuated_molecular_beta_total,
        "attenuated_molecular_backscatter_parallel": clean_attenuated_molecular_beta_parallel,
        "attenuated_molecular_backscatter_perpendicular": clean_attenuated_molecular_beta_perpendicular,
        "transmittance_elastic": T_elastic,
        "overlap": overlap,
        "k_lidar_elastic_parallel": k_lidar_elastic_parallel,
        "k_lidar_elastic_perpendicular": k_lidar_elastic_perpendicular,
        "particle_angstrom_exponent": ae,
        "synthetic_beta": synthetic_beta,
        "temperature": T,
        "pressure": P,
        "despolarization_particle": despo_particle_profile,
        "despolarization_volumic": despo_volumic,
        "despolarization_molecular": despo_molecular,
        "backscattering_ratio" : R,
        "angle_laser_PBC": phi,
        "reflectance_s_path": reflectance_s_path,
        "reflectance_p_path": reflectrance_p_path,
        "transmittance_s_path": transmittance_s_path,
        "transmittance_p_path": transmittance_p_path,
        "gain_reflected_path": gain_reflected_path,
        "gain_transmitted_path": gain_transmitted_path,
        "reflectance_parallel_path": reflectance_parallel_path,
        "reflectance_perpendicular_path": reflectance_perpendicular_path,
        "transmittance_parallel_path": transmittance_parallel_path,
        "transmittance_perpendicular_path": transmittance_perpendicular_path,
        "signal_parallel_path": P_elastic_parallel,
        "signal_perpendicular_path": P_elastic_perpendicular,
        "signal_s_path": Ps,
        "signal_p_path": Pp, 
    }
    
    if force_zero_aer_after_bin is not None:
        alpha_part[force_zero_aer_after_bin:] = 0
        beta_part[force_zero_aer_after_bin:] = 0


    return P_elastic_reflected, P_elastic_transmitted, params


def synthetic_signals_2D(
    ranges: np.ndarray,
    time: np.ndarray,
    wavelengths: float | tuple[float, float] = 532,
    overlap_midpoint: float = 800,
    overlap_slope: float = 1 / 50,
    k_lidar: float = 1e11,
    ae: float | tuple[float, float] = (1.5, 0),
    lr: float | tuple[float, float] = (75, 45),
    synthetic_beta: float | tuple[float, float] = (2.5e-6, 2.0e-6),
    sigmoid_edge: float | tuple[float, float] = (5000, 5000),
    force_zero_aer_after_bin: int | None = None,
    meteo_profiles: tuple[np.ndarray, np.ndarray] | None = None,
    apply_overlap: bool = True,
    N: int = 10,
    variable_intensity: bool = False,
    variable_ABL_top: bool = False,
) -> tuple[np.ndarray, np.ndarray | None, ParamsDict]:
    """It generates a quicklook of synthetic elastic lidar signal."""

    z = ranges
    t = time

    # Lógica de superposición (overlap)
    if apply_overlap:
        overlap = sigmoid(z.astype(np.float64), overlap_midpoint, overlap_slope, offset=0.)
    else:
        overlap = np.ones_like(z)

    # Manejo de parámetros
    if isinstance(lr, float):
        lr = (lr, lr)
    if isinstance(ae, float):
        ae = (ae, ae)
    if isinstance(synthetic_beta, float):
        synthetic_beta = (synthetic_beta, synthetic_beta)

    # Verificación de perfiles meteorológicos
    if meteo_profiles is None:
        P, T, _ = atmo.standard_atmosphere(z)
    else:
        if len(meteo_profiles[0]) != len(z):
            raise ValueError("Length of meteo_profiles must be equal to length of z")
        else:
            P = meteo_profiles[0]
            T = meteo_profiles[1]

    # Generación de perfiles moleculares
    mol_properties = molecular_properties(wavelengths, P, T, heights=z)

    # Inicializar matrices para las propiedades de partículas
    beta_part2D = np.zeros((len(t), len(z)))
    alpha_part2D = np.zeros((len(t), len(z)))
    
    # Inicializar la matriz de señales
    P_elastic2D = np.zeros((len(t), len(z)))  
    T_elastic2D = np.zeros((len(t), len(z)))
    
    # Asegurar que overlap es 2D
    if overlap.ndim == 1:
        overlap2D = np.tile(overlap[np.newaxis, :], (len(t), 1))

    # Asegurar que molecular_beta es 2D
    # Asegurar que molecular_beta es 2D sin modificar el Dataset original
    molecular_beta = mol_properties["molecular_beta"].values
    molecular_alpha = mol_properties["molecular_alpha"].values

    if molecular_beta.ndim == 1:
        molecular_beta2D = np.tile(molecular_beta[np.newaxis, :], (len(t), 1))
        
    if molecular_alpha.ndim == 1:
        molecular_alpha2D = np.tile(molecular_alpha[np.newaxis, :], (len(t), 1))
        
    periodo = 50
    omega = 2*np.pi/periodo    
    amplitud = (sigmoid_edge[0] / 10, sigmoid_edge[-1] / 10)
    # amplitud = (sigmoid_edge[0] , sigmoid_edge[-1])
    
    for i, t_i in enumerate(t):
        if variable_intensity and not variable_ABL_top:
            (_, _, beta_part2D[i, :], _, _, alpha_part2D[i, :]) = generate_particle_properties(
                ranges, wavelengths, ae=ae, lr=lr,
                synthetic_beta=(synthetic_beta[0] * (t_i / (t[-1] * 5)), synthetic_beta[-1] * (t_i / (t[-1] * 5))),
                sigmoid_edge=sigmoid_edge
            )
        elif variable_ABL_top and not variable_intensity:
            (_, _, beta_part2D[i, :], _, _, alpha_part2D[i, :]) = generate_particle_properties(
                ranges, wavelengths, ae=ae, lr=lr,
                synthetic_beta=(synthetic_beta[0], synthetic_beta[-1]),
                sigmoid_edge=(
                    amplitud[0] * np.cos(omega * t_i) + sigmoid_edge[0] * t_i / t[-1],
                    amplitud[-1] * np.cos(omega * t_i) + sigmoid_edge[-1] * t_i / t[-1]
                )
            )
        elif variable_intensity and variable_ABL_top:
            (_, _, beta_part2D[i, :], _, _, alpha_part2D[i, :]) = generate_particle_properties(
                ranges, wavelengths, ae=ae, lr=lr,
                synthetic_beta=(
                    synthetic_beta[0] * (t_i / (t[-1] * 5)),
                    synthetic_beta[-1] * (t_i / (t[-1] * 5))
                ),
                sigmoid_edge=(
                    amplitud[0] * np.cos(omega * t_i) + sigmoid_edge[0] * t_i / t[-1],
                    amplitud[-1] * np.cos(omega * t_i) + sigmoid_edge[-1] * t_i / t[-1]
                )
                # sigmoid_edge=(
                #     amplitud[0] * np.cos(omega * t_i) + sigmoid_edge[0],
                #     amplitud[-1] * np.cos(omega * t_i) + sigmoid_edge[-1]
                # )
            )

        T_elastic2D[i, :] = atmo.transmittance(molecular_alpha2D[i, :] + alpha_part2D[i, :], z) 
        P_elastic2D[i, :] = (
            k_lidar * (overlap2D[i, :] / z**2) * T_elastic2D[i, :] ** 2 * (beta_part2D[i, :] + molecular_beta2D[i, :])
        )
    
        

    P_elastic2D[:, :N] = np.nan  # Establecer a NaN los primeros N valores
    
    # Convertir a xarray.DataArray
    beta_part2D = xr.DataArray(
        beta_part2D,
        dims=["time", "range"],
        coords={
            "time": t, 
            "range": z
        },
        name="beta_part"
    )
    
    alpha_part2D = xr.DataArray(
        alpha_part2D,
        dims=["time", "range"],
        coords={
            "time": t, 
            "range": z
        },
        name="alpha_part"
    )
    
    molecular_alpha2D = xr.DataArray(
        molecular_alpha2D,
        dims=["time", "range"],
        coords={
            "time": t, 
            "range": z
        },
        name="molecular_alpha"
    )
    
    molecular_beta2D = xr.DataArray(
        molecular_beta2D,
        dims=["time", "range"],
        coords={
            "time": t, 
            "range": z
        },
        name="molecular_beta"
    )

    T_elastic2D = xr.DataArray(
        T_elastic2D,
        dims=["time", "range"],
        coords={
            "time": t, 
            "range": z
        },
        name="transmittance_elastic"
    )
    
    overlap2D = xr.DataArray(
        overlap2D,
        dims=["time", "range"],
        coords={
            "time": t, 
            "range": z
        },
        name="overlap"
    )
    
    # Guardar parámetros
    params: ParamsDict = {
        "particle_beta2D": beta_part2D,
        # "particle_beta_base": beta_part_base,
        "particle_alpha2D": alpha_part2D,
        # "particle_alpha_base": alpha_part_base,
        "molecular_beta2D": molecular_beta2D,
        "molecular_beta": molecular_beta,
        "molecular_alpha2D": molecular_alpha2D,
        "molecular_alpha": molecular_alpha,
        "transmittance_elastic2D": T_elastic2D,
        # "transmittance_elastic": T_elastic,
        "overlap2D": overlap2D,
        "overlap": overlap,
        "lidar_ratio": lr,  
        "k_lidar": k_lidar,
        "particle_angstrom_exponent": ae,
        "synthetic_beta": synthetic_beta,
        "temperature": T,
        "pressure": P,
    }

    if force_zero_aer_after_bin is not None:
        # alpha_part_base[force_zero_aer_after_bin:] = 0
        # beta_part_base[force_zero_aer_after_bin:] = 0
        alpha_part2D[force_zero_aer_after_bin:] = 0
        beta_part2D[force_zero_aer_after_bin:] = 0
        
    # Convertir a xarray.DataArray
    P_elastic_xarray = xr.DataArray(
        P_elastic2D,
        dims=["time", "range"],
        coords={
            "time": t, 
            "range": z
        },
        name="LIDAR_signal"
    )

    return P_elastic_xarray, params

