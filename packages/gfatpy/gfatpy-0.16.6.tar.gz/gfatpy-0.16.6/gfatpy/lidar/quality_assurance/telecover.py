import os
import datetime as dt
from pathlib import Path

import numpy as np
import xarray as xr
from gfatpy.lidar.utils.file_manager import filename2info
from gfatpy.lidar.quality_assurance.plot import plot_telecover_channel

from gfatpy.lidar.utils.utils import LIDAR_INFO, signal_to_rcs
from gfatpy.lidar.preprocessing import preprocess

pol_name = {0: "all", 1: "parallel", 2: "perpendicular"}
det_mod_name = {0: "analog", 1: "photoncounting", 2: "gluing"}


def telecover(
    wildcard: str,
    dir: Path | str | None = None,
    output_dir: Path | str | None = None,
    channels: list[str] | None = None,
    normalization_range: tuple[float, float] = (0, 3000),
    crop_range: tuple[float, float] = (0, 3000),
    save_fig: bool = False,
) -> None:

    if dir is None:
        dir = Path.cwd()
    elif isinstance(dir, str):
        dir = Path(dir)

    if not dir.exists() or not dir.is_dir():
        raise ValueError(f"Directory {dir} does not exist or is not a directory.")

    if output_dir is None:
        output_dir = Path.cwd()
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    if not output_dir.exists() or not output_dir.is_dir():
        raise ValueError(
            f"Directory {output_dir} does not exist or is not a directory."
        )

    files = dir.glob(f"{wildcard}.nc")

    # Check files of the same time
    hours = list()  # to list telecover hours (should be the same)
    dates = list()  # to list telecover days (should be the same)
    for file_ in files:
        _, _, _, _, _, date_ = filename2info(file_.name)
        hour_ = file_.name.split("_")[-1].split(".")[0]
        hours.append(hour_)
        dates.append(date_)
    unique_dates = np.unique(dates)  # Number of telecovers of the same type
    unique_hours = np.unique(hours)  # Number of telecovers of the same type
    if len(unique_dates) > 1:
        raise RuntimeError(
            f"Files of different days detected: {dates}. Change the wildcard."
        )
    if len(unique_hours) > 1:
        raise RuntimeError(
            f"Files of different telecovers detected: {hours}. Change the wildcard."
        )

    # Check not repeated sector
    sectors = list()
    for file_ in files:
        sector_ = file_.name.split("_")[1]
        sectors.append(sector_)
    if np.unique(sectors).size < len(sectors):
        raise RuntimeError(f"Repeated sector detected: {sectors}. Change the wildcard.")

    telecover = dict()
    for file_ in files:
        sector_ = file_.name.split("_")[2].split("-")[-1]

        # LIDAR preprocessing
        telecover[sector_] = preprocess(file_)

        # Creating a Dataset [rf_ds] for each channel with all the sectors
        for channel_ in telecover[sector_].channel.values:
            if channel_ in channels and bool(
                telecover[sector_].sel(channel=channel_).active_channel.values.all()
            ):

                # Wavelength, Detection Mode, Polarization
                wavelength = np.floor(
                    telecover[sector_].wavelength.sel(channel=channel_).values
                ).astype("int")
                detection_mode = int(
                    telecover[sector_].detection_mode.sel(channel=channel_).values
                )
                polarization = int(
                    telecover[sector_].polarization.sel(channel=channel_).values
                )

                rf_ds = xr.Dataset()
                for sector_ in enumerate(telecover.keys()):
                    # TELECOVER EARLINET DATA FORMAT
                    # TODO: sacar a una funcion
                    rcs: xr.DataArray = signal_to_rcs(
                        telecover[sector_][f"signal_{channel_}"].mean(
                            dim="time", keep_attrs=True
                        ),
                        telecover[sector_]["range"] ** 2,
                    )
                    rcs.name = sector_

                    rf_ds = xr.merge([rf_ds, rcs], combine_attrs="no_conflicts")

                # Assigning coordinates
                rf_ds = rf_ds.assign_coords({"range": rf_ds.range / 1e3})

                # Attributes
                rf_ds["range"].attrs["units"] = "m"
                rf_ds["range"].attrs["long_name"] = "Height"
                rf_ds = rf_ds.sel(range=slice(*crop_range))
                rf_ds["wavelength"] = wavelength
                rf_ds["wavelength"].attrs["value_str"] = str(wavelength)

                # TODO: sacar la creacion de un dataset especifico para RF a una funcion
                # Polarization
                rf_ds["polarization"] = polarization
                rf_ds["polarization"].attrs["meaning"] = pol_name[polarization]
                rf_ds["polarization"].attrs["id"] = LIDAR_INFO["metadata"][
                    "code_polarization_number2str"
                ][polarization]

                # TODO: sacar esto a una funcion
                # Detection mode
                rf_ds["detection_mode"] = detection_mode
                rf_ds["detection_mode"].attrs["meaning"] = det_mod_name[detection_mode]
                rf_ds["detection_mode"].attrs["id"] = LIDAR_INFO["metadata"][
                    "code_mode_number2str"
                ][detection_mode]

                rf_ds.attrs["sectors"] = list(telecover.keys())
                rf_ds.attrs["lidar_location"] = "Granada"
                rf_ds.attrs["lidar_id"] = "gr"
                rf_ds.attrs["lidar_system"] = telecover[sector_].attrs["system"].lower()
                rf_ds.attrs["datetime_ini"] = dates[0].strftime("%Y%m%dT%H:%M:%S.%f")
                rf_ds.attrs["date_format"] = "%Y%m%dT%H:%M:%S.%f"
                rf_ds.attrs["hour_ini"] = hours[0]
                rf_ds.attrs["hour_end"] = hours[-1]
                rf_ds.attrs["channel_code"] = channel_

                # SAVE RF FILE
                # TODO: sacar a una funcion el escribir este archivo con formato
                cols = list(telecover.keys())
                if detection_mode == 0:  # (if analog)
                    cols.append("D")

                # Convert to pandas
                rf_df = []
                rf_df = rf_ds[cols].to_dataframe()

                # Create file
                lidar_id = rf_ds.attrs["lidar_id"]
                rf_fn = output_dir / f"telecover_{lidar_id}_{channel_}.csv"

                with open(rf_fn, "w") as f:
                    f.write(
                        "station ID = %s (%s)\n"
                        % (
                            rf_ds.attrs["lidar_id"],
                            rf_ds.attrs["lidar_location"],
                        )
                    )
                    f.write("system = %s\n" % rf_ds.attrs["lidar_system"])
                    f.write(
                        "signal = %s, %s, %s, %s\n"
                        % (
                            rf_ds["wavelength"].attrs["value_str"],
                            rf_ds["polarization"].attrs["meaning"],
                            rf_ds["detection_mode"].attrs["meaning"],
                            rf_ds.attrs["dark_subtracted"],
                        )
                    )
                    f.write(
                        "date, time= %s\n"
                        % dt.datetime.strftime(
                            rf_ds.attrs["datetime_ini"], "%d.%m.%Y, %HUTC"
                        )
                    )
                f.close()
                rf_df.index = rf_df.index.map(lambda x: "%.4f" % x)
                rf_df.to_csv(
                    rf_fn,
                    mode="a",
                    header=True,
                    na_rep="NaN",
                    float_format="%.4e",
                )
                if os.path.isfile(rf_fn):
                    # Plot Telecover for current channel
                    plot_telecover_channel(
                        rf_ds,
                        normalization_range=normalization_range,
                        output_dir=output_dir,
                        save_fig=save_fig,
                    )

    return None
