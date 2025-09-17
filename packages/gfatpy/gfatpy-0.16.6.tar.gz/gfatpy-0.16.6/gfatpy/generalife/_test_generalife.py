#%%
import os   
import re
from scipy.signal import savgol_filter
import glob
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from datetime import datetime
from gfatpy.lidar.utils.utils import signal_to_rcs
from gfatpy.utils.io import unzip_file
from gfatpy.generalife.io import LicelReader
from gfatpy.utils.plot import color_list    

dz = 7.5
max_bins = 2000

start_date = "20240413"
end_date = "20240413"

dates = pd.date_range(start=start_date, end=end_date, freq='D')
dates = dates.strftime('%Y%m%d')

raw_dir = Path(r"U:\UGR")
output_dir = Path(r"W:\UGR")
personal_dir = Path(r'G:\Mi unidad\Alh_study_cases')

for date in dates:

    # Update the directory paths according to your file structure
    input_path = raw_dir / "generalife" / date[:4] / date[4:6] / date[6:8] 
    output_path = output_dir / "generalife" / '1a' / date[:4] / date[4:6] / date[6:8] 
    fig_path = personal_dir / "generalife" / "plots" / date[:4] / date[4:6] / date[6:8] 

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    if not fig_path.exists():
        fig_path.mkdir(parents=True, exist_ok=True)

    RS_FL_name = 'RS_' + date + '*.zip'

    zip_files = list(input_path.glob(RS_FL_name))
    
    for zip_file in zip_files:
        zip_file_path = Path(zip_file)
        
        unzipped_folder = unzip_file(zip_file_path)
        if unzipped_folder is None:
            print(f"Error unzipping file {zip_file_path}.")
            continue
        date_folder = unzipped_folder / date

        files = list(date_folder.rglob('*'))
        
        def licel_to_datetime(licel_name: str) -> datetime:
            name, extension = licel_name.split(".")
            try:
                month_decimal = int(name[-5], 16)
                return datetime.strptime(f"{name[-7:-5]}{month_decimal:02d}{name[-4:-2]}T{name[-2:]}{extension[:4]}", r"%y%m%dT%H%M%S")
            except ValueError:
                print(f"Skipping file {licel_name} due to unexpected name format.")
                return None
            
        times = [licel_to_datetime(file.name) for file in files]
        #times = [time.strftime("%Y-%m-%d %H:%M:%S") for time in times if time is not None]

        df = pd.read_csv(files[0], header=None, skiprows=3, delimiter=' ', encoding='ISO-8859-1', on_bad_lines='skip')
        wavelengths = df[8].dropna().astype(int).values

        data = np.empty((len(files), len(wavelengths), max_bins))

        for file_idx, file_path in enumerate(files):
            sp = LicelReader.LicelFileReader(file_path)
            for i, wavelength in enumerate(wavelengths):
                data[file_idx, i, :] = sp.dataSet[i].physData

        # Create an xarray DataArray from the data array
        raw = xr.DataArray(
            data,
            coords={'wavelength': wavelengths, 'times': times, 'bins': np.arange(max_bins)},
            dims=['times', 'wavelength', 'bins']
        )

        # Calculate the background signal and subtract it from the raw signal
        background_signal = (raw[:, :, 70:400]).mean(dim='bins')
        bckg_corrected_signal = raw - background_signal

        # Remove the first 400 bins from the signal
        bin_corrected_signal = bckg_corrected_signal[:, :, 400:]

        # Create a new dataset with the corrected signal and assign new bin coordinates
        spectra = bin_corrected_signal.to_dataset(name='bin_corrected_signal')
        new_bins = np.arange(0, 1600)
        spectra = spectra.assign_coords(bins=(('bins', new_bins)))

        # Rename dimensions and coordinates
        spectra = spectra.rename({'bins': 'range'})
        spectra['range'] = spectra['range'] * dz
        spectra = spectra.rename({'times': 'time'})

        # Convert the signal to RCS (Radar Cross Section)
        rcs_signal = signal_to_rcs(spectra['bin_corrected_signal'], spectra['range'])
        spectra['rcs_signal'] = rcs_signal

        # Update dataset attributes

        center_wavelength = (wavelengths[16] + wavelengths[15]) / 2

        spectra.attrs.update({
            'system name': 'Generalife',  
            'location': 'Granada',
            'latitude': '37.1641° N',
            'longitude': '3.6026° W',
            'altitude': '680 m',
            'frequency': '10 Hz',
            'bin width': '7.5 m',
            'number of bins': '2000',
            'number of channels': '32',
            'center wavelength': center_wavelength,
            'high voltage': '709 mV',
            'discriminator' : '4.0',
            'bin_corrected': 'True',
            'bcg_corrected': 'True',
        })

        wv = spectra.attrs['center wavelength']

        # Assume times is a list of datetime objects
        selected_time = times[0]  # Select the first time, change this as needed

        hour = selected_time.strftime("%H%M")  # Extract the hour and minute from the datetime object

        for file in files:
            filename = os.path.basename(file)
            match = re.match(r'^([a-zA-Z]+)', filename)
            if match:
                nc_name = output_path / f"gen_1a_{match.group(1)}_{date}_{hour}.nc"

        spectra.sel(wavelength=wavelength).to_netcdf(nc_name)
       
        # Define a function to create a subplot of the mean signal and RCS
        def create_subplot(ax, data, label, xlabel, ylabel, color, ylim=None):
            mean_data = data.mean(dim='time')
            ax.plot(spectra.range.values/1000, mean_data, label=label, color=color)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            if ylim is not None:
                ax.set_ylim(ylim)   
            ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        # Use the function to create subplots
        colors = color_list(len(wavelengths))
        fig, axs = plt.subplots(1, 2, figsize=(15, 5))  # Adjusted figure size to accommodate 2 subplots

        # Add a centered title to the figure
        fig.suptitle(f'Bckg and bin corrected signal {date}')

        for i, wavelength in enumerate(wavelengths):
            create_subplot(axs[0], spectra.sel(wavelength=wavelength)['bin_corrected_signal'], f'{wavelength} nm', 'Range (km)', 'Mean signal', colors[i])
            create_subplot(axs[1], spectra.sel(wavelength=wavelength)['rcs_signal'], f'{wavelength} nm', 'Range (km)', 'Mean RCS', colors[i], ylim=(0, 3e5))
        
        axs[0].set_ylim(0, 0.1)
        axs[1].set_xlim(0, 5)
        axs[1].set_ylim(0, 1e5)
        plt.tight_layout()  # Adjusts subplot params so that subplots fit into the figure area
        plt.savefig(f'{fig_path}/Spectra_{date}_{hour}.png')

        ##%%

        # Define a function to create a subplot with optional Savitzky-Golay smoothing of the mean signal and RCS
        def create_subplot(ax, data, label, xlabel, ylabel, color, ylim=None, smooth=False):
            mean_data = data.mean(dim='time')
            if smooth:
                mean_data = savgol_filter(mean_data, 51, 3)  # Apply Savitzky-Golay smoothingmean_data = savgol_filter(mean_data, 51, 3)  # Apply Savitzky-Golay filter
            ax.plot(spectra.range.values/1000, mean_data, label=label, color=color)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            if ylim is not None:
                ax.set_ylim(ylim)   
            ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

        # Use the function to create subplots
        colors = color_list(len(wavelengths))
        fig, axs = plt.subplots(1, 2, figsize=(15, 5))  # Adjusted figure size to accommodate 2 subplots

        # Add a centered title to the figure
        fig.suptitle(f'Smoothed bckg and bin corrected signal {date}')

        for i, wavelength in enumerate(wavelengths):
            create_subplot(axs[0], spectra.sel(wavelength=wavelength)['bin_corrected_signal'], f'{wavelength} nm', 'Range (km)', 'Mean signal', colors[i])
            create_subplot(axs[1], spectra.sel(wavelength=wavelength)['rcs_signal'], f'{wavelength} nm', 'Range (km)', 'Mean RCS', colors[i], ylim=(0, 2.3e5), smooth=True)
        
        axs[0].set_ylim(0, 0.1)
        axs[0].set_xlim(0, 3)
        axs[1].set_xlim(0, 3)
        axs[1].set_ylim(0, 1e5)
        plt.tight_layout()  # Adjusts subplot params so that subplots fit into the figure area
        plt.savefig(f'{fig_path}/Spectra_{date}_{hour}_smoothed.png')

        # Define a function to create a subplot for averaged spectrum
        def create_subplot_spectrum(ax, data, label, xlabel, ylabel, log_scale=False):
            mean_data = data.mean(dim=['time', 'range'])
            ax.plot(wavelengths, mean_data, label=label)
            
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend()  # Add legend to the subplot
            if log_scale:
                ax.set_yscale('log')
                ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
                ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

        # Create a figure
        fig, axs = plt.subplots(1, 2, figsize=(15, 5))  # Adjusted figure size to accommodate 2 subplots

        # Add a centered title to the figure
        fig.suptitle(f'0-3000m average spectrum {date}')

        create_subplot_spectrum(axs[0], spectra['bin_corrected_signal'].sel(range=slice(0, 2000)), 'Mean signal', 'Wavelength (nm)', 'Mean signal')
        create_subplot_spectrum(axs[1], spectra['rcs_signal'].sel(range=slice(0, 2000)), 'Mean RCS', 'Wavelength (nm)', 'Mean RCS')
        
        axs[0].set_ylim(0, 0.1)
        axs[0].set_xlim(0, 3)
        axs[1].set_xlim(0, 3)
        axs[1].set_ylim(0, 1e5)
        plt.tight_layout()  # Adjusts subplot params so that subplots fit into the figure area
        plt.savefig(f'{fig_path}/Spectra_{date}_{hour}_average_0_3000.png')

        ##%%
        # Define the range windows)), f'{start+start_range}-{end+start_range} m', 'Wavelength (nm)', 'Mean RCS', log_scale=True)
        range_windows = [(i, i+200) for i in range(0, 1000, 200)]

        # Create a figure for each range
        for start_range in [0]:  # Changed to only [0]
            fig, axs = plt.subplots(1, 2, figsize=(15, 5))  # Adjusted figure size to accommodate 2 subplots

            # Add a centered title to the figure
            fig.suptitle(f'{start_range}-{start_range+1000}m {date}')

            # Iterate over the range windows
            for start, end in range_windows:
                create_subplot_spectrum(axs[0], spectra['bin_corrected_signal'].sel(range=slice(start, end)), f'{start}-{end}m', 'Wavelength (nm)', 'Mean signal')
                create_subplot_spectrum(axs[1], spectra['rcs_signal'].sel(range=slice(start, end)), f'{start}-{end}m', 'Wavelength (nm)', 'Mean RCS')

            # Set y-axis to logarithmic scale
            axs[0].set_yscale('log')
            axs[1].set_yscale('log')

            plt.tight_layout()  # Adjusts subplot params so that subplots fit into the figure area
            plt.savefig(f'{fig_path}/Spectra_{date}_{hour}_continuous_{start_range}_{start_range+1000}.png')  # Save the figure

        ##%%
        # Define the range windows
        range_windows = [(i, i+500) for i in range(0, 3000, 500)]

        # Create a figure for each range
        for start_range in [0]:  # Changed to only [0]
            fig, axs = plt.subplots(1, 2, figsize=(15, 5))  # Adjusted figure size to accommodate 2 subplots

            # Add a centered title to the figure
            fig.suptitle(f'{start_range}-{start_range+3000}m {date}')

            # Iterate over the range windows
            for start, end in range_windows:
                create_subplot_spectrum(axs[0], spectra['bin_corrected_signal'].sel(range=slice(start, end)), f'{start}-{end}m', 'Wavelength (nm)', 'Mean signal')
                create_subplot_spectrum(axs[1], spectra['rcs_signal'].sel(range=slice(start, end)), f'{start}-{end}m', 'Wavelength (nm)', 'Mean RCS')
            
            # Set y-axis to logarithmic scale
            axs[0].set_yscale('log')
            axs[1].set_yscale('log')

            plt.tight_layout()  # Adjusts subplot params so that subplots fit into the figure area
            plt.savefig(f'{fig_path}/Spectra_{date}_{hour}_continuous_{start_range}_{start_range+3000}.png')  # Save the figure
        