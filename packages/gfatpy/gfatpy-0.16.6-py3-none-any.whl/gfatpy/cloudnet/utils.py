import os

import numpy as np
import pandas as pd
import numpy as np
import xarray as xr
from datetime import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
from loguru import logger

from gfatpy.cloudnet import CLOUDNET_INFO
from gfatpy.utils import utils


def get_cloudnet_fn(
    station_name: str, date_str: str, kind: str, cloudnet_dn: str | None = None
) -> str | None:
    """Get file name full path for a day cloudnet data

    Args:
        station_name: str
            name of station
        date_str: str
            date (day) YYYYMMDD
        kind: str
            categorize, classification
        cloudnet_dn: str
            absolute path for cloudnet data
    Returns:
        cldnt_fn: str
            full path cloudnet file name
    """

    try:
        if cloudnet_dn is None:  # GFAT NAS
            cloudnet_dn = r"/mnt/NASGFAT/datos/CLOUDNET"

        if kind in CLOUDNET_INFO["CLOUDNET_KINDS"]:
            date_year = datetime.strptime(date_str, "%Y%m%d").strftime("%Y")
            cldnt_fn = os.path.join(
                cloudnet_dn,
                station_name,
                kind,
                date_year,
                "%s_%s_%s.nc" % (date_str, station_name, kind),
            )
            if not os.path.isfile(cldnt_fn):
                logger.error("File %s not found" % cldnt_fn)
                cldnt_fn = None
        else:
            logger.error("Cloudnet File kind %s does not exist" % kind)
            cldnt_fn = None
    except Exception as e:
        logger.error(str(e))
        cldnt_fn = None

    return cldnt_fn


def CBH_attenuated(
    cat: xr.Dataset,
    threshold: float = 2.5e-6,
    cloud_height_maximum: float = 4000,
    plot_flag: bool = False,
) -> xr.Dataset:

    """
    CBH_attenuated finds the CBH from attenuated backscatter in CLUODNET categorize files
    Input:
    cat: xarray from  CLUODNET categorize file
    threshold: minimum value of cloud attenuated backscatter (default: 2.5e-6 m^1*sr^-1
    cloud_height_maximum: maximxum height at which CBH will be search (Default: 4000 m),
    plot_flag: it plots the CBH temporal evolution (Default: False)
    Output:
    cat: xarray categorize input but with CBH.
    """

    top_idx, _ = utils.find_nearest_1d(cat.height.values, cloud_height_maximum)
    height = cat.height[0:top_idx].values

    CBH = np.nan * np.ones(len(cat.time))
    for i_ in np.arange(len(cat.time)):
        profile = cat.beta[i_, 0:top_idx].values
        try:
            candidate = height[profile > threshold][0]
        except:
            candidate = height[profile > threshold]
        if candidate < cloud_height_maximum:
            CBH[i_] = candidate
    if plot_flag:
        fig, axes = plt.subplots(1, 1)
        for i_ in np.arange(len(cat.time)):
            profile = cat.beta[i_, 0:top_idx].values
            axes.plot(profile, height)
        fig.set_figheight(15)
        fig.set_figwidth(15)
        axes.vlines(threshold, 0, cloud_height_maximum)
        plt.xlim(0, threshold * 3)

    cat["CBH_attenuated_beta"] = ("time", CBH)

    return cat


def cloud_edges(cat: xr.Dataset, threshold_split: float = 200) -> xr.Dataset:
    """
    CTH_finder finds the CTH from radar reflectivity in CLUODNET categorize files
    Input:
    cat: xarray from CLUODNET categorize file
    cloud_height_maximum: maximxum height at which CTH will be search (Default: 5000 m),
    Output:
    cat: xarray categorize input but with CTH.
    """
    cat["Zboolean"] = cat.Z.where(np.isnan(cat.Z), other=1)
    cat["Zboolean"] = cat.Zboolean.where(~np.isnan(cat.Z), other=0)
    cat["Zbooleandiff_CBH"] = (
        ("time", "height"),
        np.diff(cat.Zboolean, axis=1, prepend=0),
    )
    cat["Zbooleandiff_CTH"] = (
        ("time", "height"),
        np.diff(cat.Zboolean, axis=1, prepend=0),
    )

    # CBH candidates
    final_CBH = np.nan * np.ones(np.shape(cat["Z"]))
    final_CTH = np.nan * np.ones(np.shape(cat["Z"]))
    CBH0 = np.nan * np.ones(len(cat["time"]))
    CTH0 = np.nan * np.ones(len(cat["time"]))
    single_layer = np.ones(len(cat["time"]))
    idx_height = np.arange(len(cat["height"]))
    for idx_ in np.arange(len(cat["time"])):
        # CBH candidates
        booleanCBH = cat["Zbooleandiff_CBH"][idx_, :] == 1
        CBHcandidates = cat["height"].where(booleanCBH)
        # CTH candidates
        booleanCTH = cat["Zbooleandiff_CTH"][idx_, :] == -1
        CTHcandidates = cat["height"].where(booleanCTH)

        # Glue clouds too near
        CBHs = CBHcandidates[booleanCBH]
        CTHs = CTHcandidates[booleanCTH]
        if len(CBHs) > 0:
            if np.logical_and.reduce((len(CBHs) > 1, len(CBHs) == len(CTHs))):
                distance = CBHs.values[1:] - CTHs.values[:-1]  # type: ignore
                if np.logical_and.reduce((len(distance) > 0, distance.any())):
                    idx_badDistance = (
                        distance < threshold_split
                    )  # CTH(n) and CBH(n+1) should be far enough to be consider different cloud
                    goodCBH = CBHs[np.append(True, ~idx_badDistance)]
                    goodCTH = CTHs[np.append(~idx_badDistance, True)]
                    if np.logical_and.reduce((goodCBH.any(), goodCTH.any())):
                        for CBH_ in goodCBH:
                            final_CBH[idx_, idx_height[cat["height"] == CBH_]] = CBH_
                        for CTH_ in goodCTH:
                            final_CTH[idx_, idx_height[cat["height"] == CTH_]] = CTH_
                    CBH0[idx_] = final_CBH[idx_, :][~np.isnan(final_CBH[idx_, :])][0]
                    CTH0[idx_] = final_CTH[idx_, :][~np.isnan(final_CTH[idx_, :])][0]
                single_layer[idx_] = 0
            else:
                try:
                    CBH0[idx_] = CBHs
                    CTH0[idx_] = CTHs
                except:
                    raise ValueError("CBH and CTH are not the same length")
    cat["CBH"] = (("time", "height"), final_CBH)
    cat["CTH"] = (("time", "height"), final_CTH)
    cat["CBH_first"] = (("time"), CBH0)
    cat["CTH_first"] = (("time"), CTH0)
    cat["cloud_depth"] = (("time"), CTH0 - CBH0)
    cat["single_layer"] = (("time"), single_layer)
    return cat


def CTH_finder(cat: xr.Dataset, cloud_height_maximum: float = 5000):
    """
    CTH_finder finds the CTH from radar reflectivity in CLUODNET categorize files
    Input:
    cat: xarray from CLUODNET categorize file
    cloud_height_maximum: maximxum height at which CTH will be search (Default: 5000 m),
    Output:
    cat: xarray categorize input but with CTH.
    """
    top_idx, _ = utils.find_nearest_1d(cat.height.values, cloud_height_maximum)
    height = cat.height[0:top_idx].values
    CTH = np.nan * np.ones(len(cat.time))
    for i_ in np.arange(len(cat.time)):
        profile = cat.Z[i_, 0:top_idx].values
        CBH = cat.CBH[i_]
        if np.logical_and(~np.isnan(CBH), (~np.isnan(profile)).any()):
            CTH[i_] = height[~np.isnan(profile)][-1]
            if CTH[i_] <= CBH:
                CTH[i_] = np.nan

    cat["CTH"] = ("time", CTH)

    return cat


def filter_Z(cat: xr.Dataset, cbh_threshold: float = 2.5e-6, plot_flag: bool = False):
    """
    filter_Z cleans the Z matrix of low aerosol layers. It requires CLUODNET categorize files with CBH.
    Input:
    cat: xarray from CLUODNET categorize file
    cbh_threshold: attenuated beta threshold value to detect the CBH using cloudnet.CBH_attenuated()

    Output:
    cat: xarray categorize input but with cleaned Z.
    """

    if not "CBH" in cat:
        cat = CBH_attenuated(cat, threshold=cbh_threshold)

    cat["Z"] = cat.Z.where(cat.height > cat.CBH_attenuated_beta)
    if plot_flag:
        fig, axes = plt.subplots(1, 1)
        fig.set_figheight(4)
        fig.set_figwidth(15)
        cmap = mpl.cm.jet
        cat.Z.where(cat.height > cat.CBH_first).plot(
            x="time", cmap=cmap, vmin=-50, vmax=20, ax=axes
        )
        cat.CBH_first.plot(c="r", ax=axes)
    return cat


def compute_avg_in_cloud(
    Z: np.ndarray,
    v: np.ndarray,
    height: np.ndarray,
    cbh: float,
    cth: float,
    max_height: float,
) -> tuple[np.ndarray]:
    """Retrieve the Z and v mean in the given range.
    Args:
        Z (np.ndarray): reflectivity
        v (np.ndarray): vertical velocity
        height (np.ndarray): range
        cbh (float): cloud base height
        cth (float): cloud top height
        max_height (float, optional): maximum height above the CBH to perform the average. Default value None means threo.

    Returns:
        list[np.ndarray]: Z and v mean in the given range.
    """
    if max_height == -1:  # Average Over Cloud
        idc = np.logical_and(height > cbh, height < cth)
        Z_avg = np.nanmean(Z[idc])
        v_avg = np.nanmean(v[idc])
    elif max_height > 0:  # Average Over CBH and a height above CBH (and below
        # CTH)
        _, hi = utils.find_nearest_1d(height, cbh + max_height)
        idx = np.logical_and.reduce((height >= cbh, height <= hi, height <= cth))
        Z_avg = np.nanmean(Z[idx])
        v_avg = np.nanmean(v[idx])
    else:
        print("proxy_cloud must be -1 or >0")
        Z_avg = Z * np.nan
        v_avg = v * np.nan

    return Z_avg, v_avg  # FIXME


def ZdB_to_Z(Z: np.ndarray) -> np.ndarray:
    """
    Z (dBZ) to linear Z
    Z_linear = 10**(Z_log/10) x 1e-18 [mm6/m3 -> m6/m3 ]

    Args:
    - Z: units mm^6/m^3

    Returns:
    - Linear Z: units m^3
    """
    return 10 ** (Z / 10 - 18)


def filtering(
    dx_in: xr.Dataset,
    liquid_drop: bool = True,
    cbh_range: list = [450, 4000],
    lwp_range: list = [50, 150],
    lwp_rel_error_threshold: float = 50,
    similar_weather_conditions: bool = True,
    persistence: bool = True,
    force_liquid_drop_incloud: bool = True,
    preserve_time: bool = False,
    cbh_weather_conditions: bool = None,
) -> xr.Dataset:
    """_summary_

    Args:
        dx_in (xr.Dataset): categorize-classification file (merge)
        liquid_drop (bool, optional): _description_. Defaults to True.
        cbh_range (list, optional): heights where the cbh can be situated Defaults to [450, 4000].
        lwp_range (list, optional): range of values for the lwp. Defaults to [50, 150].
        lwp_rel_error_threshold (float, optional): error for lwp. Defaults to 50.
        similar_weather_conditions (bool, optional): _description_. Defaults to True.
        persistence (bool, optional): _description_. Defaults to True.
        force_liquid_drop_incloud (bool, optional): _description_. Defaults to True.
        preserve_time (bool, optional): _description_. Defaults to False.
        cbh_weather_conditions (bool, optional): _description_. Defaults to None.

    Returns:
        xr.Dataset: files that satify the conditions
    """
    # filtrado
    # - nubes liquidas
    # - rango cbh
    # - lwp>0 (e_lwp)
    # - condiciones meteo
    # - persistencia 30min
    # - si despues de filtrar, quedan menos de 10 perfiles, elimino el dia

    t = pd.to_datetime(dx_in.time.values)
    # print(t)
    h = dx_in.height.values
    # print(h)
    dx_in.model_height.values
    # print(mh)
    tc = dx_in.target_cla.values
    # print(tc)
    cbh = dx_in.cbh.values
    # print(cbh)
    cth = dx_in.cth.values
    # print(cth)
    lwp = dx_in.lwp.values
    # print(lwp)
    elwp = dx_in.lwp_error.values
    # print(elwp)
    dx_in.temperature.values
    # print(tk)
    dx_in.pressure.values
    # print(p)
    dx_in.specific_humidity.values
    # print(q)
    rr = dx_in.rainrate.values
    # print(rr)

    # TODO ADD Tk, P, Q at CLOUD BASE HEIGHT
    # tk_cbh, p_cbh, q_cbh = weather_conditions_at_cbh(cbh, mh, tk, p, q)
    # dx_in['tk_cbh'] = (['time'], tk_cbh)
    # dx_in['p_cbh'] = (['time'], p_cbh)
    # dx_in['q_cbh'] = (['time'], q_cbh)

    # index for filtering
    idx = []
    try:
        # LIQUID DROPS
        # For each profile (time), filtering is performed
        # Use TARGET CLASSIFICATION to filter out all profiles that have
        # water components other than liquid drops that may contribute to LWP:
        # drizzle, rain (2,3), ice+liquid drops (5), melting ice (6), melting
        # ice + liquid drops (7)
        # In addition, only profiles with, at least, one value for liquid
        # drop, are considered.
        idx_ld = np.ones(t.shape[0])
        if liquid_drop:  # select profiles
            for i, _t in enumerate(t):
                x = tc[:, i]
                if np.logical_and.reduce(
                    (
                        (
                            not np.logical_or.reduce(
                                (x == 2, x == 3, x == 5, x == 6, x == 7)
                            ).any()
                        )
                        and ((x == 1).any())
                    )
                ):
                    idx_ld[i] = 1
                else:
                    idx_ld[i] = 0
                del x
        # In addition, ensure no precipitation with rainrate variable
        idx_ld[rr > 0] = 0

        # MODIFY CTH

        # PERSISTENCE: if liquid_drop == TRUE
        # Se buscan perfiles consecutivos que satisfacen la condicion
        # de gota liquida durante, al menos, media hora.
        # Aflojo un poco la condicion y permito perfiles no consecutivos si
        # el lapso entre 2 no consecutivos es menor que 5 minutos.
        # obviamente, los perfiles que se intercalan entre estos dos no
        # consecutivos que, por razones obvias, no satisfacen la condición de
        # gota líquida, no se incluyen
        idx_per = idx_ld.copy()
        if persistence and liquid_drop:
            count = 1
            lp = []
            while count < t.shape[0]:
                # print("count=%i"%count)
                cp = count
                _lp = []
                if idx_ld[cp] == 1:  # si liquid drop
                    # print("comienza subset")
                    si = 1
                    last_1 = cp
                    # print("last_1=%i"%last_1)
                    while (si == 1) and (cp < t.shape[0]):  # Liquid Drop
                        if idx_ld[cp] == 1:  # si liquid drop
                            _lp.append(cp)
                            cp += 1
                            last_1 = cp
                            # print("update last_1=%i" % last_1)
                        else:  # si no liquid drop
                            if (t[cp] - t[last_1]) < np.timedelta64(300, "s"):
                                cp += 1
                            else:
                                si = 0
                    # print("termina subset")
                    lp.append(_lp)
                    count = cp + 1
                else:  # avance
                    # print("avance")
                    count += 1

            # Los subconjuntos generados deben durar, al menos, 10 minutos
            for _lp in lp:
                t_lapse = t[_lp[-1]] - t[_lp[0]]
                if t_lapse < np.timedelta64(10, "m"):
                    idx_per[_lp] = 0

        # CLOUD BASE HEIGHT RANGE
        idx_cbh = np.ones(t.shape[0])
        if isinstance(cbh_range, list):
            if len(cbh_range) == 2:
                idx = ~np.logical_and(cbh >= cbh_range[0], cbh <= cbh_range[1])
                idx_cbh[idx] = 0

        # LWP, LWP_ERROR THRESHOLDS
        idx_lwp = np.ones(t.shape[0])
        if isinstance(lwp_range, list):
            if len(lwp_range) == 2:
                idx = ~np.logical_and.reduce(
                    (
                        lwp >= lwp_range[0],
                        lwp <= lwp_range[1],
                        100 * elwp / lwp < lwp_rel_error_threshold,
                    )
                )
                idx_lwp[idx] = 0

        # ONLY LIQUID DROP INSIDE THE CLOUD
        idx_ld_incloud = np.ones(t.shape[0])
        if force_liquid_drop_incloud:
            for i, _t in enumerate(t):
                x = tc[:, i]
                ix = np.logical_and(h >= cbh[i], h <= cth[i])
                if x[ix].any():  # Existen datos incloud
                    if not (x[ix][1:] == 1).all():
                        idx_ld_incloud[i] = 0
                else:
                    idx_ld_incloud[i] = 0

        # SIMILAR METEO CONDITIONS
        # TODO usamos los perfiles que satisfacen las condiciones de gota liquida
        idx_met = np.ones(t.shape[0])
        logger.critical("Function not finished.")
        # if similar_weather_conditions:
        #     xx = idx_ld == 1
        #     idx = ~ np.logical_and(
        #         np.nanstd(tk_cbh[xx])/np.nanmean(tk_cbh[xx]) < 0.1,
        #         np.nanstd(p_cbh[xx])/np.nanmean(p_cbh[xx]) < 0.1)
        #     idx_met[idx] = 0

        # similar meteo conditions based on whole period
        # TODO: investigar si esta condicion es interesante
        """
        if cbh_weather_conditions is not None:
            # Tk, P, Q avg, sd at CBHs
            tk_cbh_avg, tk_cbh_sd = cbh_weather_conditions[0]
            p_cbh_avg, p_cbh_sd = cbh_weather_conditions[1]
            q_cbh_avg, q_cbh_sd = cbh_weather_conditions[2]

            #
            tk = dx_in.temperature.values
            p = dx_in.pressure.values
            q = dx_in.specific_humidity.values
            tk_cbh, p_cbh, q_cbh = weather_conditions_at_cbh(cbh, mh, tk, p, q)
        """

        # FILTER BY IDX
        idx = idx_ld * idx_per * idx_cbh * idx_lwp * idx_ld_incloud * idx_met
        # Hay, al menos, 10 elementos
        if len(np.argwhere(idx == 1)) >= 10:
            dx_out = dx_in.sel(time=dx_in.time[idx == 1])

            # DROP NON-NECESSARY VARIABLES
            dx_out = dx_out.drop(
                ["temperature", "pressure", "specific_humidity", "model_height"]
            )
            # REINDEX TO ORIGINAL TIME
            if preserve_time:
                dx_out = dx_out.reindex({"time": dx_in.time})
        else:
            dx_out = None
    except:
        print("SOMETHING WENT WRONG IN FILTERING")
        dx_out = None

    return dx_out
