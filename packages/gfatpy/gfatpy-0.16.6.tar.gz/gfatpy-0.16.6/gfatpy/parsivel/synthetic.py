# %%
from typing import Any
from matplotlib import ticker
import numpy as np
import matplotlib.pyplot as plt

from gfatpy.utils.plot import color_list


def reflectivity(
    diameter: float | list | np.ndarray, number_per_diameter: float | list | np.ndarray
) -> tuple[float | np.ndarray, float | np.ndarray]:
    """Reflectivity factor calculation for a given diameter and number of droplets.

    Args:
        diameter (_type_): Diameter of droplets (micrometers).
        number_per_diameter (_type_): Number of droplets per diameter.

    Returns:
        _type_: _description_
    """
    if isinstance(diameter, list):
        diameter = np.array(diameter)
    if isinstance(number_per_diameter, list):
        number_per_diameter = np.array(number_per_diameter)

    linear_Z = (number_per_diameter * (diameter * 1e-3) ** 6).sum()  # en milímetros
    dBZe = 10 * np.log10(linear_Z)
    return linear_Z, dBZe


# %%
D_range = np.array([1, 10, 100, 1000])  # en micrómetros
for D in D_range:
    linear_Z, dBZe = reflectivity(D, 10)  # En milímetros
    print(f"Diameter: {D:.0e} m, Linear Z: {linear_Z:.2e}, dBZe: {dBZe:.2f} dBZ")
# %%
N = 100000
DSD = np.random.normal(10, 1, N)
diameters = np.arange(0.1, 20, 0.1)
freq, diam_bins = np.histogram(DSD, bins=diameters)
midpoints = (diam_bins[:-1] + diam_bins[1:]) / 2
linear_Z, dBZe = reflectivity(midpoints, freq)
# plot
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].plot(midpoints, linear_Z)
ax[0].set_xlabel("Droplet Diameter ($\mu m$)")
ax[0].set_ylabel("Linear Reflectivity Factor (mm^6/m^3)")
# ax[0].set_title('Linear Reflectivity Factor vs Droplet Diameter')
ax[0].grid(True)
ax[1].plot(midpoints, dBZe)
ax[1].set_xlabel("Droplet Diameter (mm)")
ax[1].set_ylabel("Reflectivity Factor (dBZ)")
# ax[1].set_title('Reflectivity Factor vs Droplet Diameter')
ax[1].grid(True)
plt.show()
# %%
N = 100000
fig, ax = plt.subplots(1, 2, figsize=(15, 6))
mu_list = [10, 20, 30, 40, 50]
colors = color_list(len(mu_list))
dBZe = np.zeros(len(mu_list))
for idx, mu in enumerate(mu_list):
    DSD = np.random.normal(mu, 1.5, N)
    diameters = np.arange(0.1, 2*mu, 0.1)
    freq, diam_bins = np.histogram(DSD, bins=diameters)
    midpoints = (diam_bins[:-1] + diam_bins[1:]) / 2
    _, dBZe[idx] = reflectivity(midpoints, freq)
    # plot
    ax[0].plot(midpoints, freq, color = colors[idx], label=f"Mean: {mu} $\mu m$")
ax[0].set_xlim(0, 60)
ax[0].set_xlabel("Droplet Diameter ($\mu m$)")
ax[0].set_ylabel("Droplet Size Distribution, $m^{-3}/\mu m$")
# ax[0].set_title('Linear Reflectivity Factor vs Droplet Diameter')
ax[0].grid(True)
ax[0].legend(loc="best", fontsize=15)

ax[1].plot(mu_list, dBZe, lw=2, marker='o', color='k')
# Color each marker according to the colors list
for idx, color in enumerate(colors):
    ax[1].plot(mu_list[idx], dBZe[idx], marker='o', markersize=20, color=colors[idx])

ax[1].set_xlabel("Droplet Diameter ($\mu m$)")
ax[1].set_ylabel("Reflectivity Factor (dBZ)")
ax[1].set_ylim(-75, -25)
# ax[1].set_title('Reflectivity Factor vs Droplet Diameter')
ax[1].grid(True)
fig.savefig("dBZe_changing_mu.png", dpi=300, bbox_inches='tight')
plt.show()
# %%
mu = 30
fig, ax = plt.subplots(1, 2, figsize=(15, 6))
N_list = 100000*np.arange(1,6)
colors = color_list(len(N_list))
dBZe = np.zeros(len(N_list))
for idx, N in enumerate(N_list):
    DSD = np.random.normal(mu, 1.5, N)
    diameters = np.arange(0.1, 2*mu, 0.1)
    freq, diam_bins = np.histogram(DSD, bins=diameters)
    midpoints = (diam_bins[:-1] + diam_bins[1:]) / 2
    _, dBZe[idx] = reflectivity(midpoints, freq)

    # plot
    ax[0].plot(midpoints, freq, color = colors[idx], label=f"{N:.1E}" +"$m^{-3}$")

ax[0].set_xlim(20, 40)
ax[0].set_xlabel("Droplet Diameter ($\mu m$)")
ax[0].set_ylabel("Droplet Size Distribution, $m^{-3}/\mu m$")
# ax[0].set_title('Linear Reflectivity Factor vs Droplet Diameter')
ax[0].grid(True)
ax[0].legend(loc="best", fontsize=12)

ax[1].plot(N_list, dBZe, lw=2, marker='o', color='k')
# Color each marker according to the colors list
for idx, color in enumerate(colors):
    ax[1].plot(N_list[idx], dBZe[idx], marker='o', markersize=20, color=colors[idx])
ax[1].set_ylim(-75, -25)
ax[1].set_xlabel("Droplet Diameter ($\mu m$)")
ax[1].set_ylabel("Reflectivity Factor (dBZ)")
# ax[1].set_title('Reflectivity Factor vs Droplet Diameter')
ax[1].grid(True)
ax[1].xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
ax[1].ticklabel_format(style='sci', axis='x', scilimits=(0,0))

fig.savefig("dBZe_changing_N.png", dpi=300, bbox_inches='tight')
plt.show()
# %%
mu = 30
N  = 100000
fig, ax = plt.subplots(1, 2, figsize=(15, 6))
signal_list = np.arange(1,3,0.5)
colors = color_list(len(signal_list))
dBZe = np.zeros(len(signal_list))
for idx, sigma in enumerate(signal_list):
    DSD = np.random.normal(mu, sigma, N)
    diameters = np.arange(0.1, 2*mu, 0.1)
    freq, diam_bins = np.histogram(DSD, bins=diameters)
    midpoints = (diam_bins[:-1] + diam_bins[1:]) / 2
    _, dBZe[idx] = reflectivity(midpoints, freq)

    # plot
    ax[0].plot(midpoints, freq, color = colors[idx], label=f"{sigma} " +"$\mu m$")

ax[0].set_xlim(20, 40)
ax[0].set_xlabel("Droplet Diameter ($\mu m$)")
ax[0].set_ylabel("Droplet Size Distribution, $m^{-3}/\mu m$")
# ax[0].set_title('Linear Reflectivity Factor vs Droplet Diameter')
ax[0].grid(True)
ax[0].legend(loc="best", fontsize=12)

ax[1].plot(signal_list, dBZe, lw=2, marker='o', color='k')
# Color each marker according to the colors list
for idx, color in enumerate(colors):
    ax[1].plot(signal_list[idx], dBZe[idx], marker='o', markersize=20, color=colors[idx])
ax[1].set_ylim(-75, -25)
ax[1].set_xlabel("Droplet Diameter ($\mu m$)")
ax[1].set_ylabel("Reflectivity Factor (dBZ)")
# ax[1].set_title('Reflectivity Factor vs Droplet Diameter')
ax[1].grid(True)
ax[1].xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
ax[1].ticklabel_format(style='sci', axis='x', scilimits=(0,0))

fig.savefig("dBZe_changing_sigma.png", dpi=300, bbox_inches='tight')
plt.show()

# %%
mu_list = [10, 20, 30, 40, 50]
sigma = 2
N  = 100000
# Calculate shape (k) and scale (theta) parameters
k_list = (np.array(mu_list)**2) / sigma
theta_list = (sigma / 30)*np.ones(len(k_list))

# Number of samples
size = 1000
fig, ax = plt.subplots(1, 2, figsize=(15, 6))
colors = color_list(len(k_list))
dBZe = np.zeros(len(k_list))
for idx in np.arange(len(k_list)):
    DSD = np.random.gamma(k_list[idx], theta_list[idx], N)
    diameters = np.arange(0.1, 2*mu, 0.1)
    freq, diam_bins = np.histogram(DSD, bins=diameters)
    midpoints = (diam_bins[:-1] + diam_bins[1:]) / 2
    _, dBZe[idx] = reflectivity(midpoints, freq)

    # plot
    ax[0].plot(midpoints, freq, color = colors[idx], label=f"{k_list[idx]:.2f} | {theta_list[idx]:.2f}")

# ax[0].set_xlim(20, 40)
ax[0].set_xlabel("Droplet Diameter ($\mu m$)")
ax[0].set_ylabel("Droplet Size Distribution, $m^{-3}/\mu m$")
# ax[0].set_title('Linear Reflectivity Factor vs Droplet Diameter')
ax[0].grid(True)
ax[0].legend(loc="best", fontsize=12)

ax[1].plot(k_list, dBZe, lw=2, marker='o', color='k')
# Color each marker according to the colors list
for idx, color in enumerate(colors):
    ax[1].plot(k_list[idx], dBZe[idx], marker='o', markersize=20, color=colors[idx])
# ax[1].set_ylim(-75, -25)
ax[1].set_xlabel("Droplet Diameter ($\mu m$)")
ax[1].set_ylabel("Reflectivity Factor (dBZ)")
# ax[1].set_title('Reflectivity Factor vs Droplet Diameter')
ax[1].grid(True)
ax[1].xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
ax[1].ticklabel_format(style='sci', axis='x', scilimits=(0,0))

fig.savefig("dBZe_changing_sigma.png", dpi=300, bbox_inches='tight')
plt.show()
# %%
