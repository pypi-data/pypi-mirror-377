"""
    gnss_utils
    =====================

    Utils module contains some useful utils module.

    1. Everett Interpolation
    2. SSR to Clock

"""

import pickle
from collections import defaultdict
from sqlite3 import SQLITE_DBCONFIG_LEGACY_ALTER_TABLE

import numpy as np
import xarray as xr
import pandas as pd

from ppgnss import gnss_time
from ppgnss import gnss_geodesy

# Everett Interpolation, see slade1971.
EVCF = [1.7873015873015873E0, -0.4960317460317460E0, 0.1206349206349206E0,
        -0.1984126984126984E-1, 0.1587301587301587E-2, -0.9359567901234568E0,
        0.6057098765432098E0, -0.1632716049382716E0, 0.2779982363315696E-01,
        -0.2259700176366843E-02, 0.1582175925925926E0, -0.1171296296296296E0,
        0.4606481481481481E-1, -0.8796296296296296E-2, 0.7523148148148148E-3,
        -0.9755291005291005E-2, 0.7605820105820106E-2, -0.3505291005291005E-2,
        0.8597883597883598E-3, -0.8267195767195767E-4, 0.1929012345679012E-3,
        -0.1543209876543210E-3, 0.7716049382716048E-4, -0.2204585537918871E-4,
        0.2755731922398589E-5]

EVCF_MAT = np.array([EVCF[i * 5:(i + 1) * 5][::-1]
                     + EVCF[i * 5 + 1: (i + 1) * 5]
                     for i in range(0, 5)])


def get_xr_rms(xr_neu, str_start_time=None, str_stop_time=None):
    """
    :param xr_neu:
    :param str_start_time:
    :param str_stop_time:
    :return: rms of n, e ,u
    """
    if str_start_time is None:
        str_start_time = str(xr_neu.coords["time"].values[0])
    if str_stop_time is None:
        str_stop_time = str(xr_neu.coords["time"].values[-1])
    xr_neu_new = xr_neu.loc[str_start_time:str_stop_time, :]
    rms_neu = np.sqrt(np.nanmean(xr_neu_new * xr_neu_new, axis=0))
    return rms_neu[0], rms_neu[1], rms_neu[2], np.sqrt(rms_neu[0] ** 2 + rms_neu[1] ** 2)


def everett_interp_order8(ti_list, fi_list, t4interp):
    """
    Everett Interpolation using 8th difference. ``ti_list`` and ``fi_list``
    are time series with same interval. ``ti_list`` should be in time order.
    ``t`` is the time for interplotion. ``t`` should be greater then the
    first value of ``ti_list`` and less then the last value ``ti_list``.

    :param ti_list: time list in time order, Modified Julian Date
    :type ti_list: float list
    :param fi_list: function value list
    :type fi_list: float list
    :return: float
    :rtype: float
    """
    if len(ti_list) != 9:
        raise ValueError("list length is not 9: " + str(ti_list))
    dti_list = [t0 - t1 for t0, t1 in zip(ti_list[:-1], ti_list[1:])]
    if not all([dt0 == dt1 for dt0, dt1 in zip(dti_list[:-1], dti_list[1:])]):
        raise ValueError("Time intervals are not in order")

    if t4interp < ti_list[0] or t4interp > ti_list[-1]:
        raise ValueError("time for interplotion is not in time range.")
    boundary = filter(lambda t0, t1: t0 < t4interp < t1,
                      zip(ti_list[:-1], ti_list[1:]))
    if not boundary:
        raise ValueError("time for interplotion is not in time range.")
    t_front, t_behind = boundary[0]
    h_step = ti_list[1] - ti_list[0]
    p_factor = (t4interp - t_front) / h_step
    q_factor = 1 - p_factor
    print(q_factor)
    y_vec = np.dot(EVCF_MAT, fi_list)
    print(y_vec)


def saveobject(obj0, filename):
    """Save python object to file.

    :param obj0: object in python
    :type obj0: object
    :param filename: Output filename for saving file.
    :type filename: string
    """
    status = False
    with open(filename, 'wb') as fwrite:
        pickle.dump(obj0, fwrite)
        status = True
    return status


def loadobject(binfilename):
    """Load object from file. File should be saved by
    :func:`gnss_utils.saveobject`.

    :param binfilename: filename for loading
    :type binfilename: string

    """
    obj = None
    with open(binfilename, 'rb') as fread:
        obj = pickle.load(fread)
    return obj


def xr_ssr2clock_norm(xr_clock_ssr, xr_brdc):
    """
    Convert correction and brdc to satellite clock. If different interval and
    latency is required, use `gnss_utils.xr_ssr2clock2`.
    """
    coord_prns = [prn for prn in xr_clock_ssr.coords['prn'].values
                  if prn.startswith("G") and len(prn) == 3]
    coord_time = xr_clock_ssr.coords['time'].values
    ndata = np.zeros((len(coord_time), len(coord_prns)),
                     dtype=np.float64) + np.nan

    xr_clock = xr.DataArray(ndata,
                            coords=[coord_time, coord_prns],
                            dims=['time', 'prn'])
    for prn in coord_prns:
        if prn not in xr_brdc.coords['prn'].values:
            continue
        xr_brdc_prn = xr_brdc.loc[:, prn]
        xr_ssr_prn = xr_clock_ssr.loc[:, prn]

        idx_valid_brdc = np.logical_not(
            np.isnan(xr_brdc_prn.loc[:, "IODE"].values))
        xr_valid_brdc_prn = xr_brdc_prn[idx_valid_brdc]

        for iode, clock_bias, clock_drift, toe, gpsw in \
                xr_valid_brdc_prn.loc[:, ["IODE",
                                          "SVclockBias",
                                          "SVclockDrift",
                                          "TimeEph",
                                          "GPSWeek",
                                          ]]:
            idx_iode_equal = xr_ssr_prn.loc[:, "IODE"] == iode
            # print idx_iode_equal
            xr_c0_prn_iode = xr_ssr_prn[idx_iode_equal.values].loc[:, "C0"]
            xr_a0_prn_iode = clock_bias
            xr_a1_prn_iode = clock_drift

            obj_reference_time = gnss_time.toe2datetime(
                gpsw.values, toe.values)
            dt64_reference_time = np.datetime64(obj_reference_time)

            delta_time = xr_c0_prn_iode.coords['time'] - \
                         dt64_reference_time
            delta_seconds = delta_time / np.timedelta64(1, 's')
            # relativ_corr = 0.
            xr_clock_prn = xr_a0_prn_iode \
                           + xr_c0_prn_iode / gnss_geodesy.GPS_LIGHT_SPEED \
                           + xr_a1_prn_iode.values * delta_seconds.values
            xr_clock.loc[idx_iode_equal, prn] = xr_clock_prn.values
    return xr_clock


def time_arr_gen(time_from, time_to, interval):
    """ Generate equal-interval time array.

    :time_from: startting time, like "2017-10-10 10:10:10.000"
    :type time_start: string
    :time_to: End time. like "2017-10-11 10:10:10.000"
    :type time_to: string
    :interval: interval (second)
    :type interval: int

    Usage example::

      >>> time_from='2017-10-10 00:00:00.00'
      >>> time_to = '2017-10-10 00:00:20.00'
      >>> interval = 5
      >>> time_arr_gen(time_from, time_to, 5)
      DatetimeIndex(['2017-10-10 00:00:00', '2017-10-10 00:00:05',
                     '2017-10-10 00:00:10', '2017-10-10 00:00:15',
                     '2017-10-10 00:00:20'],
                    dtype='datetime64[ns]', freq='5S')
.
      ----------------------------------------------------------------------
      Ran 1 test in 0.001s


    """
    str_freq = '%02dS' % interval
    # pd_time_list = pd.date_range(time_from, time_to,
    #                              freq=str_freq).to_datetime()
    pd_time_list = pd.to_datetime(pd.date_range(time_from, time_to,
                                                freq=str_freq))
    return pd_time_list


def xr_ssr2clock(xr_clock_ssr, xr_brdc, latency=0, interval=None,
                 valid_seconds=None):
    """
    Convert correction and brdc to satellite clock.

    :xr_clock_ssr: SSR. Obtain from `gnss_io.read_ssr_file`
    :xr_brdc: brdc. Obtain from `gnss_io.read_brdc_file`
    :latency: latency of RTS
    :type latency: int
    :interval: interval of out clock, seconds
    :type interval: int
    :valid_seconds: how many seconds are valid when using SSR
    :type valid_seconds: int
    :repair: Whether repair datum jumps or not
    :type repair: bool
    :return: clock

    """
    coord_prns = [prn for prn in xr_clock_ssr.coords['prn'].values
                  if prn.startswith("G") and len(prn) == 3]

    time_from_obj64 = xr_clock_ssr.coords['time'].values[0]
    time_to_obj64 = xr_clock_ssr.coords['time'].values[-1]
    update_rate = (xr_clock_ssr.coords['time'].values[1]
                   - xr_clock_ssr.coords['time'].values[0]) \
                  / np.timedelta64(1, 's')
    if not interval:
        interval = update_rate
    if not valid_seconds:
        valid_seconds = update_rate - 1
    str_freq = '%02dS' % interval

    coord_time = pd.to_datetime(pd.date_range(
        time_from_obj64,
        time_to_obj64 + np.timedelta64(int(latency + valid_seconds), 's'),
        freq=str_freq))
    # coord_time = pd.date_range(
    #     time_from_obj64,
    #     time_to_obj64 + np.timedelta64(int(latency + valid_seconds), 's'),
    #     freq=str_freq).to_datetime()
    ndata = np.zeros((len(coord_time), len(coord_prns)),
                     dtype=np.float64) + np.nan

    xr_clock = xr.DataArray(ndata,
                            coords=[coord_time, coord_prns],
                            dims=['time', 'prn'])

    for prn in coord_prns:
        if prn not in xr_brdc.coords['prn'].values:
            continue
        xr_brdc_prn = xr_brdc.loc[:, prn]
        xr_ssr_prn = xr_clock_ssr.loc[:, prn]

        idx_valid_brdc = np.logical_not(
            np.isnan(xr_brdc_prn.loc[:, "IODE"].values))
        xr_valid_brdc_prn = xr_brdc_prn[idx_valid_brdc]

        for iode, clock_bias, clock_drift, toe, gpsw in \
                xr_valid_brdc_prn.loc[:, ["IODE",
                                          "SVclockBias",
                                          "SVclockDrift",
                                          "TimeEph",
                                          "GPSWeek",
                                          ]]:

            idx_iode_equal = xr_ssr_prn.loc[:, "IODE"] == iode
            if not idx_iode_equal.values.any():
                continue
            rts_reftime_from = xr_ssr_prn[
                idx_iode_equal.values].coords['time'].values[0]
            rts_reftime_to = xr_ssr_prn[
                idx_iode_equal.values].coords['time'].values[-1]

            # coord_time_extra = pd.date_range(
            #     rts_reftime_from + np.timedelta64(latency, 's'),
            #     rts_reftime_to +
            #     np.timedelta64(int(latency + valid_seconds), 's'),
            #     freq=str_freq).to_datetime()
            coord_time_extra = pd.to_datetime(pd.date_range(
                rts_reftime_from + np.timedelta64(latency, 's'),
                rts_reftime_to +
                np.timedelta64(int(latency + valid_seconds), 's'),
                freq=str_freq))

            xr_c0_prn_iode = xr_ssr_prn[idx_iode_equal.values].sel(
                time=coord_time_extra,
                method='ffill').loc[:, "C0"]
            xr_c1_prn_iode = xr_ssr_prn[idx_iode_equal.values].sel(
                time=coord_time_extra,
                method='ffill').loc[:, "C1"]

            xr_a0_prn_iode = clock_bias
            xr_a1_prn_iode = clock_drift

            brdc_ref_time_dt64 = np.datetime64(
                gnss_time.toe2datetime(gpsw.values, toe.values))

            extra_seconds = np.array([
                (curr_time - brdc_ref_time_dt64) / np.timedelta64(1, 's')
                for curr_time in coord_time_extra])

            latency_seconds = \
                np.array([(t1 - t2) / np.timedelta64(1, 's')
                          for t1, t2 in
                          zip(coord_time_extra,
                              xr_c0_prn_iode.coords['time'].values)])

            idx_invalid = latency_seconds > valid_seconds

            xr_clock_prn = xr_a0_prn_iode.values \
                           + xr_c0_prn_iode.values / gnss_geodesy.GPS_LIGHT_SPEED \
                           + xr_a1_prn_iode.values * extra_seconds

            if idx_invalid.any():
                xr_clock_prn[idx_invalid] = np.nan
            xr_clock.loc[coord_time_extra, prn] = xr_clock_prn
    # repairing here
    return xr_clock


def _remove_drift(xr_clock, xr_brdc):
    """Removing Clock drift from clock first order difference.
    """
    xr_clock_firstorder = xr_clock.diff('time', label="upper")
    coord_prns = [prn for prn in xr_clock.coords['prn'].values
                  if prn.startswith("G") and len(prn) == 3]
    coord_times = xr_clock.coords['time']
    intervals = (coord_times.diff(
        'time', label="lower") / np.timedelta64(1, 's')).values

    clock_drift = np.nanmean(
        xr_brdc.loc[:, coord_prns, "SVclockDrift"].values, axis=0)
    nepochs, nsat = xr_clock_firstorder.shape

    intervals.shape = (-1, 1)
    clock_drift.shape = (1, -1)
    xr_clock_removed_drift = xr_clock_firstorder \
                             - intervals * clock_drift
    return xr_clock_removed_drift


def clock_extrapolation(xr_clock, xr_brdc, interval=None, valid_seconds=None):
    """Extrapolating Satellite Clock using Clock drift from BRDC.
    """
    coord_prns = [prn for prn in xr_clock.coords['prn'].values
                  if prn.startswith("G") and len(prn) == 3]

    update_rate = (xr_clock.coords['time'].values[1]
                   - xr_clock.coords['time'].values[0]) \
                  / np.timedelta64(1, 's')
    if not interval:
        interval = update_rate
    if not valid_seconds:
        valid_seconds = update_rate - 1

    str_freq = '%02dS' % interval
    clock_reftime_from = xr_clock.coords['time'].values[0]
    clock_reftime_to = xr_clock.coords['time'].values[-1]

    coord_time_extra = pd.date_range(
        clock_reftime_from,
        clock_reftime_to + np.timedelta64(int(valid_seconds), 's'),
        freq=str_freq).to_datetime()

    ndata = np.zeros((len(coord_time_extra), len(coord_prns)),
                     dtype=np.float64) + np.nan
    xr_clock_extra = xr.DataArray(ndata,
                                  coords=[coord_time_extra, coord_prns],
                                  dims=['time', 'prn'])
    for prn in coord_prns:
        idx_clock_nan = np.logical_not(np.isnan(xr_clock.loc[:, prn]))
        if not idx_clock_nan.any():
            continue
        xr_clock_prn = xr_clock.loc[:, prn]

        xr_clock_prn_droped = xr_clock_prn[idx_clock_nan]

        clock_reftime_prn_from = xr_clock_prn_droped.coords['time'].values[0]
        clock_reftime_prn_to = xr_clock_prn_droped.coords['time'].values[-1] \
                               + np.timedelta64(int(valid_seconds), 's')
        coord_time_prn_extra = pd.date_range(
            clock_reftime_prn_from,
            clock_reftime_prn_to,
            freq=str_freq).to_datetime()

        xr_reftime_prn = xr_clock_prn_droped.coords['time'].sel(
            time=coord_time_prn_extra,
            method='ffill')

        xr_clock_prn_extra = xr_clock_prn_droped.sel(time=coord_time_prn_extra,
                                                     method='ffill')
        # print(xr_reftime_prn.loc["2017-06-21 01:02:10.00"])
        latency_seconds = np.array([(t1 - t2) / np.timedelta64(1, 's')
                                    for t1, t2 in
                                    zip(coord_time_prn_extra,
                                        xr_reftime_prn['time'].values)])
        clock_drift_prn = np.nanmean(
            xr_brdc.loc[:, prn, "SVclockDrift"].values,
            axis=0)

        tmp = clock_drift_prn * latency_seconds
        # print(tmp)
        # print(xr_clock_prn_extra.loc["2017-06-21 01:02:10.00"])
        xr_clock_extra.loc[
        str(clock_reftime_prn_from):str(clock_reftime_prn_to),
        prn] = xr_clock_prn_extra.values + tmp
    xr_diff = xr_clock_extra.diff('time')
    idx_outlier = np.abs(xr_diff) > 0.3 * 1e-9
    # plt.plot(xr_diff)
    # plt.show()
    # plt.close()
    ndata = xr_clock_extra[1:].values
    ndata[idx_outlier] = np.nan
    xr_clock_extra[1:] = ndata
    return xr_clock_extra


def cm2inch(cm):
    return cm / 2.54


def inch2cm(inch):
    return inch * 2.54


def repair_datum(xr_clock, xr_brdc):
    """Repair Datum jump of correction.
    """
    xr_clock_firstorder_zeromean = _remove_drift(xr_clock, xr_brdc)
    xr_clock_firstorder_mean = np.nanmean(xr_clock_firstorder_zeromean, axis=1)

    std_each_prn = np.nanstd(xr_clock_firstorder_zeromean, axis=0)
    std_each_epoch = np.nanstd(xr_clock_firstorder_zeromean, axis=1)
    throldhold = 0.05 * 1E-9  # std_each_prn * 3

    idx_outlier = np.abs(
        xr_clock_firstorder_zeromean) > throldhold  # std_each_prn

    idx_not_outlier = np.logical_not(idx_outlier)
    idx_not_datum_jump = np.all(
        np.abs(xr_clock_firstorder_zeromean) < throldhold, axis=1)
    idx_prob_datum_jump = np.any(
        np.abs(xr_clock_firstorder_zeromean) > throldhold, axis=1)

    xr_clock_firstorder_probjump = xr_clock_firstorder_zeromean * idx_outlier
    ndata = xr_clock_firstorder_probjump.values
    ndata[idx_not_outlier] = np.nan

    xr_clock_firstorder_probjump = ndata
    xr_clock_firstorder_probjump_mean = np.nanmean(
        xr_clock_firstorder_probjump, axis=1)
    xr_clock_firstorder_probjump_std = np.nanstd(
        xr_clock_firstorder_probjump, axis=1)

    xr_clock_firstorder_probjump_range = np.nanmax(
        xr_clock_firstorder_probjump, axis=1) \
                                         - np.nanmin(xr_clock_firstorder_probjump, axis=1)

    xr_clock_firstorder_probjump_nsat = np.sum(idx_outlier, axis=1)

    idx_sure_datum_jump = np.logical_and(
        np.logical_and(
            xr_clock_firstorder_probjump_range < 0.2 * 1E-9,
            xr_clock_firstorder_probjump_nsat >= 1,
        ),
        np.logical_and(
            np.abs(xr_clock_firstorder_mean) > .05 * 1e-9,
            idx_prob_datum_jump,
        )
    )

    idx_sure_outlier = np.logical_and(
        np.logical_and(
            xr_clock_firstorder_probjump_range > 0.5 * 1E-9,
            xr_clock_firstorder_probjump_nsat > 1,
        ),
        np.logical_and(
            np.abs(xr_clock_firstorder_mean) >= 0,
            idx_prob_datum_jump,
        )
    )
    xr_outlier = xr_clock_firstorder_zeromean[idx_sure_outlier]

    idx_nan = np.isnan(xr_clock_firstorder_probjump_mean)
    idx_not_nan_and_jumped = np.logical_and(np.logical_not(idx_nan),
                                            idx_sure_datum_jump)

    jumped_values = np.zeros(
        len(xr_clock_firstorder_probjump_mean), dtype=np.float64)
    jumped_values[idx_not_nan_and_jumped] = xr_clock_firstorder_probjump_mean[
        idx_not_nan_and_jumped]
    cum_jumped_values = np.cumsum(jumped_values)
    cum_jumped_values.shape = (-1, 1)

    xr_clock_repaired = xr_clock.copy(deep=True)
    ndata = xr_clock_repaired.values[1:]
    nsat = len(xr_clock.coords['prn'].values)
    ndata -= np.tile(cum_jumped_values, (1, nsat))
    xr_clock_repaired[1:].values = ndata

    xr_diff = xr_clock_repaired.diff('time')

    idx_outlier = np.abs(xr_diff) > 0.5 * 1E-9
    ndata = xr_clock_repaired[1:].values
    ndata[idx_outlier] = np.nan
    xr_clock_repaired[1:] = ndata

    # xr_clock_repaired[idx_outlier] = np.nan
    xr_jumped = xr.DataArray(cum_jumped_values[:, 0],
                             coords=[xr_clock.coords['time'].values[1:], ],
                             dims=['time', ])

    # return xr_clock_repaired, xr_jumped, idx_not_nan_and_jumped,
    # xr_outlier, xr_clock_firstorder_probjump_nsat
    return xr_clock_repaired, xr_jumped  # , xr_outlier


def points2grids(points, llpoint, shape, cellsize):
    """
    points: n*3
    points[0]: x
    points[1]: y
    points[2]: z
    llpoint: (llx, lly) 左下角像元四个角点的左下角坐标
    shape: (ncol, nrow) 列数(x方向）, 行数(y方向）
    cellsize: (xcellsize, ycellsize), x 和 y方向格网大小
    """
    ncol, nrow = shape[0], shape[1]
    xstep, ystep = cellsize[0], cellsize[1]
    xmin, ymin = llpoint[0], llpoint[1]

    xmax = xmin + ncol * xstep
    ymax = ymin + nrow * ystep
    grid_points = [[list() for j in range(ncol)] for i in range(nrow)]
    inds = list()
    for record in points:
        x, y, v = record[0], record[1], record[2]
        # print(x, y, v)
        if (x < xmin) or (x > xmax) or (y < ymin) or (y > ymax):
            continue
        ind_col = int(np.floor((x - xmin) / xstep)) # 列索引
        ind_row = int(np.floor((y - ymin) / ystep)) #
        # print(ind_row, ind_col, llpoint[0], llpoint[1], shape)
        # print(len(grid_points), len(grid_points[0]))
        grid_points[ind_row][ind_col].append(v)
        inds.append((ind_row, ind_col))

    data = defaultdict()
    for key in {"mean", "std", "max", "min", "count"}:
        data[key] = np.full((nrow, ncol), np.nan)
    for ind_row, ind_col in inds:
        data["mean"][ind_row, ind_col] = np.mean(grid_points[ind_row][ind_col])
        data["max"][ind_row, ind_col] = np.max(grid_points[ind_row][ind_col])
        data["min"][ind_row, ind_col] = np.min(grid_points[ind_row][ind_col])
        data["count"][ind_row, ind_col] = len(grid_points[ind_row][ind_col])
        data["std"][ind_row, ind_col] = np.std(grid_points[ind_row][ind_col])

    return data, inds

def xr_gim2solar(xr_gim):
    """
    将模型数据同时保存地理坐标系和日固坐标系数据
    新增坐标'data'，包含'vtec'（地理坐标系格网数据，未roll）和'solar_vtec'（日固坐标系格网数据，roll后）
    """
    # print(xr_gim)
    # 计算每个时间点的小时数
    hours = pd.to_datetime(xr_gim.time.values).hour
    # 计算滚动量：每小时对应 72/24 = 3 列
    # shifts = (hours * 3).astype(int)
    lon_len = len(xr_gim.lon)
    shifts = hours * lon_len / 24 + int(lon_len / 2)

    # 原始地理坐标系格网数据
    tec_geo = xr_gim.values + 0
    # 日固坐标系格网数据
    tec_sun_fixed = np.zeros_like(tec_geo)
    for i, shift in enumerate(shifts):
        tec_sun_fixed[i] = np.roll(tec_geo[i], int(shift), axis=1)
        # if i == 12:
        #     print(i, shift)
        #     fig, axes = plt.subplots(1, 2)
        #     axes[0].pcolor(tec_geo[i])
        #     axes[1].pcolor(tec_sun_fixed[i])
        #     plt.savefig("test_12.png")
        #     plt.close()
        # 构建新的xarray.Dataset，增加'data'坐标
    # data: 0 - vtec (地理坐标系), 1 - solar_vtec (日固坐标系)
    data_types = np.array(['vtec', 'solar_vtec'])
    tec_both = np.stack([tec_geo, tec_sun_fixed], axis=0)  # shape: (2, time, lat, lon)

    # 处理slon和地理lon
    slon = xr_gim['lon'].values
    # 生成新的lon变量（地理经度），每个时刻都要根据shift进行滚动
    new_lon = np.zeros((len(xr_gim.time), len(slon)))
    for i, shift in enumerate(shifts):
        new_lon[i] = np.roll(slon, -int(shift))
    # slon不变，lon随shift变化

    xr_gim_new = xr.DataArray(
        data = tec_both,
        coords = {
            'data': data_types,
            'time': xr_gim.time.values,
            'lat': xr_gim.lat.values,
            'lon': xr_gim.lon.values,
            
        },
    )
    return xr_gim_new


def xr_obs2solar(xr_obs):
    """
    将xr_obs的data维度扩充，增加"slon"变量。
    slon = lon - hour_float*15
    其中hour_float为当前时间与0时的差异（单位为小时）。
    """
    import numpy as np
    import xarray as xr

    # 获取原始data变量名
    data_vars = xr_obs.coords['data'].values.tolist()
    # 查找"lon"在data维度中的索引
    lon_idx = data_vars.index('lon')

    # 获取lon数据 (site, time, satellite)
    lon = xr_obs.isel(data=lon_idx)

    # 获取时间信息
    times = xr_obs.coords['time'].values  # (time,)
    # 计算每个时间点的hour_float
    # 转为pandas的DatetimeIndex方便处理
    import pandas as pd
    times_pd = pd.to_datetime(times)
    hour_float = times_pd.hour + times_pd.minute/60. + times_pd.second/3600.  # (time,)

    # 由于pandas的Index不再支持多维索引，需先转为numpy数组
    hour_float_np = np.array(hour_float)
    # 广播hour_float到与lon相同的shape (site, time, satellite)
    # hour_float: (time,) -> (1, time, 1)
    hour_float_broadcast = hour_float_np[None, :, None]
    # lon: (site, time, satellite)
    slon = lon.values - hour_float_broadcast * 15

    # 规范到[-180, 180]
    slon = np.where(slon > 180, slon - 360, slon)
    slon = np.where(slon < -180, slon + 360, slon)

    # 构造新的data维度
    new_data_vars = data_vars + ['slon']
    # 构造新的data array
    # 先将原始数据取出
    arr = xr_obs.values  # (site, time, satellite, data)
    # 新增一列slon
    slon_expand = slon[..., None]  # (site, time, satellite, 1)
    arr_new = np.concatenate([arr, slon_expand], axis=-1)  # (site, time, satellite, data+1)

    # 构造新的xarray.DataArray
    xr_obs_new = xr.DataArray(
        arr_new,
        dims=xr_obs.dims,
        coords={**xr_obs.coords, 'data': new_data_vars},
        name=xr_obs.name,
        attrs=xr_obs.attrs
    )
    return xr_obs_new


def xr_obs2pd(xr_obs):
    # 提取数据
    stec = xr_obs.sel(data="stec").values   # (site, time, satellite)
    mf = xr_obs.sel(data="mf").values
    vtec = stec / mf  # 计算VTEC
    ipp_lat = xr_obs.sel(data="lat").values
    ipp_lon = xr_obs.sel(data="lon").values

    # 获取多维坐标
    time_coords = xr_obs.coords['time'].values  # (time,)
    site_coords = xr_obs.coords['site'].values  # (site,)
    satellite_coords = xr_obs.coords['satellite'].values  # (satellite,)

    # 扩展多维坐标至与数据相同的维度 (site, time, satellite, data)
    # print(xr_obs.shape)
    time_expanded = np.tile(time_coords[np.newaxis, :, np.newaxis], (len(site_coords), 1, len(satellite_coords)))
    site_expanded = np.tile(site_coords[:, np.newaxis, np.newaxis], (1, len(time_coords), len(satellite_coords)))
    satellite_expanded = np.tile(satellite_coords[np.newaxis, np.newaxis, :], (len(site_coords), len(time_coords), 1))
    # data_expanded = np.tile(data_coords[np.newaxis, np.newaxis, np.newaxis, :], (len(site_coords), len(time_coords), len(satellite_coords), 1))
    # print(time_expanded.shape, data_expanded.shape, site_expanded.shape, satellite_expanded.shape) 

    # 扁平化所有数据
    vtec_flat = vtec.flatten()
    lat_flat = ipp_lat.flatten()
    lon_flat = ipp_lon.flatten()
    time_flat = time_expanded.flatten()
    site_flat = site_expanded.flatten()
    satellite_flat = satellite_expanded.flatten()

    # 过滤 NaN
    mask = ~np.isnan(vtec_flat)
    vtec_flat = vtec_flat[mask]
    lat_flat = lat_flat[mask]
    lon_flat = lon_flat[mask]
    # slon_flat = slon_flat[mask]
    time_flat = time_flat[mask]
    site_flat = site_flat[mask]
    satellite_flat = satellite_flat[mask]

    # 构造 DataFrame
    obs_df = pd.DataFrame({
        'vtec': vtec_flat,
        'lat': lat_flat,
        'lon': lon_flat,
        'time': time_flat,
        'site': site_flat,
        'satellite': satellite_flat,
    })
    return obs_df

def pd_obs2slon(pd_obs):
    """
    为 pd_obs 新增一列 slon，计算方式为 lon - (time.hour + time.minute / 60) * 15 + 12。

    :param pd_obs: 输入的 DataFrame，包含 'lon' 和 'time' 列。
    :type pd_obs: pd.DataFrame
    :return: 新增 'slon' 列的 DataFrame。
    :rtype: pd.DataFrame
    """
    # 提取时间的小时和分钟部分，并转换为小时的小数形式
    hours_decimal = pd_obs['time'].dt.hour + pd_obs['time'].dt.minute / 60. + pd_obs["time"].dt.second / 3600.
    # 计算 slon
    pd_obs['slon'] = pd_obs['lon'] - (hours_decimal * 15) + 12
    # 规范到 [-180, 180] 范围
    pd_obs['slon'] = pd_obs['slon'].apply(lambda x: x - 360 if x > 180 else (x + 360 if x < -180 else x))
    return pd_obs


def xr_obs2pd_with_slon(xr_obs):
    # 提取数据
    stec = xr_obs.sel(data="stec").values   # (site, time, satellite)
    mf = xr_obs.sel(data="mf").values
    vtec = stec / mf  # 计算VTEC
    ipp_lat = xr_obs.sel(data="lat").values
    ipp_lon = xr_obs.sel(data="lon").values
    ipp_slon = xr_obs.sel(data="slon").values

    # 获取多维坐标
    time_coords = xr_obs.coords['time'].values  # (time,)
    site_coords = xr_obs.coords['site'].values  # (site,)
    satellite_coords = xr_obs.coords['satellite'].values  # (satellite,)

    # 扩展多维坐标至与数据相同的维度 (site, time, satellite, data)
    # print(xr_obs.shape)
    time_expanded = np.tile(time_coords[np.newaxis, :, np.newaxis], (len(site_coords), 1, len(satellite_coords)))
    site_expanded = np.tile(site_coords[:, np.newaxis, np.newaxis], (1, len(time_coords), len(satellite_coords)))
    satellite_expanded = np.tile(satellite_coords[np.newaxis, np.newaxis, :], (len(site_coords), len(time_coords), 1))
    # data_expanded = np.tile(data_coords[np.newaxis, np.newaxis, np.newaxis, :], (len(site_coords), len(time_coords), len(satellite_coords), 1))
    # print(time_expanded.shape, data_expanded.shape, site_expanded.shape, satellite_expanded.shape) 

    # 扁平化所有数据
    vtec_flat = vtec.flatten()
    lat_flat = ipp_lat.flatten()
    lon_flat = ipp_lon.flatten()
    slon_flat = ipp_slon.flatten()
    time_flat = time_expanded.flatten()
    site_flat = site_expanded.flatten()
    satellite_flat = satellite_expanded.flatten()

    # print(vtec_flat.shape, time_flat.shape)
    # 过滤 NaN
    mask = ~np.isnan(vtec_flat)
    vtec_flat = vtec_flat[mask]
    lat_flat = lat_flat[mask]
    lon_flat = lon_flat[mask]
    slon_flat = slon_flat[mask]
    time_flat = time_flat[mask]
    site_flat = site_flat[mask]
    satellite_flat = satellite_flat[mask]

    # 构造 DataFrame
    obs_df = pd.DataFrame({
        'vtec': vtec_flat,
        'lat': lat_flat,
        'lon': lon_flat,
        'slon': slon_flat,
        'time': time_flat,
        'site': site_flat,
        'satellite': satellite_flat,
    })
    return obs_df
    

def valid_obs_vs_gim(pd_obs_slon, xr_gim_slon):
    """
pd_obs_slon.head() 输出：
   vtec        lat         lon                time  site satellite        slon
0  14.558791  32.858368  115.163791 2023-01-10 00:01:00  ahaq       G10  126.913791
1  23.152165  27.920725  122.639692 2023-01-10 00:01:00  ahaq       G12  134.389692
2  22.674293  24.941687  114.772730 2023-01-10 00:01:00  ahaq       G18  126.522730
3  16.237270  30.815731  117.474878 2023-01-10 00:01:00  ahaq       G23  129.224878
4  15.300479  33.181114  119.736749 2023-01-10 00:01:00  ahaq       G24  131.486749

xr_gim_solon概略输出：
<xarray.DataArray (data: 2, time: 23, lat: 71, lon: 73)> Size: 2MB
array([[[[16.1, 16.1, 16.2, ..., 16. , 16. , 16.1],
         [18.2, 18.2, 18.3, ..., 18. , 18.1, 18.2],
         [20.8, 21. , 21.1, ..., 20.6, 20.7, 20.8],
         ...,
         [ 8.3,  8.3,  8.2, ...,  8.4,  8.4,  8.3],
         [ 6.8,  6.8,  6.9, ...,  6.6,  6.7,  6.8],
         [ 5.4,  5.4,  5.5, ...,  5.2,  5.3,  5.4]],

        [[18.1, 18.1, 18.1, ..., 18.1, 18.1, 18.1],
         [19.6, 19.6, 19.5, ..., 19.7, 19.7, 19.6],
         [21.4, 21.3, 21.3, ..., 21.6, 21.5, 21.4],
         ...,
         [ 8.8,  8.5,  8.2, ...,  9.4,  9.1,  8.8],
         [ 7.1,  7. ,  6.8, ...,  7.3,  7.2,  7.1],
         [ 5.4,  5.4,  5.3, ...,  5.4,  5.4,  5.4]],

        [[20.8, 20.7, 20.6, ..., 21. , 20.9, 20.8],
         [22.6, 22.4, 22.1, ..., 23.2, 22.9, 22.6],
         [24.6, 24.2, 23.9, ..., 25.3, 24.9, 24.6],
         ...,
...
         ...,
         [ 9.1,  9.6, 10.2, ...,  7.5,  8. ,  8.6],
         [ 9.6,  9.9, 10.2, ...,  8.7,  9. ,  9.3],
         [10.5, 10.6, 10.7, ..., 10.2, 10.2, 10.4]],

        [[14.5, 14.4, 14.3, ..., 14.9, 14.8, 14.7],
         [15.5, 15.2, 15. , ..., 16.2, 16. , 15.7],
         [16.1, 15.8, 15.4, ..., 17.3, 16.9, 16.5],
         ...,
         [12.1, 11.9, 11.8, ..., 12.5, 12.4, 12.2],
         [12.5, 12.4, 12.3, ..., 12.8, 12.7, 12.6],
         [12.8, 12.8, 12.7, ..., 12.9, 12.9, 12.8]],

        [[13.3, 13.3, 13.3, ..., 13.3, 13.3, 13.3],
         [15.5, 15.5, 15.5, ..., 15.2, 15.3, 15.4],
         [18.3, 18.4, 18.5, ..., 17.9, 18. , 18.2],
         ...,
         [10.5, 10.3, 10. , ..., 11.2, 11. , 10.8],
         [ 9.6,  9.4,  9.2, ..., 10. ,  9.9,  9.7],
         [ 8.5,  8.4,  8.3, ...,  8.7,  8.6,  8.6]]]])
Coordinates:
  * data     (data) <U10 80B 'vtec' 'solar_vtec'
  * time     (time) datetime64[ns] 184B 2023-01-10T01:00:00 ... 2023-01-10T23...
  * lat      (lat) float64 568B -87.5 -85.0 -82.5 -80.0 ... 80.0 82.5 85.0 87.5
  * lon      (lon) float64 584B -180.0 -175.0 -170.0 ... 170.0 175.0 180.0

    """
    
    # 复制观测数据
    pd_obs_out = pd_obs_slon.copy()
    
    # 确保时间列为datetime类型
    pd_obs_out['time'] = pd.to_datetime(pd_obs_out['time'])
    
    # 提取GIM时间点并排序，转换为numpy datetime64类型
    gim_times = np.sort(xr_gim_slon.time.values.astype('datetime64[ns]'))
    
    # 处理每一行数据
    def process_row(row):
        t = row['time'].to_numpy()  # 转换为numpy datetime64
        lat_val = row['lat']
        lon_val = row['slon']
        
        # 检查 lat 和 lon 是否在有效范围内
        lat_min, lat_max = xr_gim_slon.lat.min().item(), xr_gim_slon.lat.max().item()
        lon_min, lon_max = xr_gim_slon.lon.min().item(), xr_gim_slon.lon.max().item()
        
        if not (lat_min <= lat_val <= lat_max) or not (lon_min <= lon_val <= lon_max):
            return pd.Series([None, None, np.nan, np.nan, np.nan, np.nan], 
                            index=['ref_time_pre', 'ref_time_next', 'gim_vtec_pre', 'gim_vtec_next', 'gim_vtec', 'delta'])
        
        # 查找前后时间点
        index = np.searchsorted(gim_times, t, side='left')
        if index == 0:
            prev_time = None
            next_time = gim_times[0]
        elif index == len(gim_times):
            prev_time = gim_times[-1]
            next_time = None
        else:
            prev_time = gim_times[index-1]
            next_time = gim_times[index]
        
        # 初始化GIM值
        value_pre = np.nan
        value_next = np.nan
        # 获取前一个时间点的GIM值
        if prev_time is not None:
            try:
                value_pre = xr_gim_slon.sel(data='solar_vtec').sel(
                    time=prev_time, 
                    lat=lat_val, 
                    lon=lon_val, 
                    method='nearest'
                ).item()
            except Exception as e:
                # print(e, lat_val, type(lat_val))
                value_pre = np.nan
        
        # 获取后一个时间点的GIM值
        if next_time is not None:
            try:
                value_next = xr_gim_slon.sel(data='solar_vtec').sel(
                    time=next_time, 
                    lat=lat_val, 
                    lon=lon_val, 
                    method='nearest'
                ).item()
            except Exception as e:
                # print(e)
                value_next = np.nan
        
        # 计算插值后的GIM值
        if prev_time is not None and next_time is not None:
            total_sec = (next_time - prev_time).astype('timedelta64[s]').astype(float)
            sec_prev = (t - prev_time).astype('timedelta64[s]').astype(float)
            sec_next = (next_time - t).astype('timedelta64[s]').astype(float)
            gim_vtec = (value_pre * sec_next + value_next * sec_prev) / total_sec
        elif prev_time is not None:
            gim_vtec = value_pre
        elif next_time is not None:
            gim_vtec = value_next
        else:
            gim_vtec = np.nan
        
        # 计算差异
        delta = row['vtec'] - gim_vtec
        
        return pd.Series([
            pd.Timestamp(prev_time) if prev_time is not None else None, 
            pd.Timestamp(next_time) if next_time is not None else None, 
            value_pre, 
            value_next, 
            gim_vtec, 
            delta
        ], index=['ref_time_pre', 'ref_time_next', 'gim_vtec_pre', 'gim_vtec_next', 'gim_vtec', 'delta'])
    
    # 应用处理函数
    new_cols = pd_obs_out.apply(process_row, axis=1)
    pd_obs_out = pd.concat([pd_obs_out, new_cols], axis=1)
    
    return pd_obs_out
    
def gim_vs_obs(xr_gim, xr_obs):
    """
    xr_gim example: <xarray.DataArray (time: 24, lat: 71, lon: 73)>
        shape=(24, 71, 73))
        Coordinates:
        * time     (time) datetime64[ns] 192B 2023-01-10 ... 2023-01-10T23:00:00
        * lat      (lat) float64 568B -87.5 -85.0 -82.5 -80.0 ... 80.0 82.5 85.0 87.5
        * lon      (lon) float64 584B -180.0 -175.0 -170.0 ... 170.0 175.0 180.0
        
    xr_obs example: <xarray.DataArray 'ipp stec' (site: 243, time: 21, satellite: 32, data: 7)>
        shape=(243, 21, 32, 7))
        Coordinates:
        * time       (time) datetime64[ns] 168B 2023-01-10T11:55:00 ... 2023-01-10T...
        * satellite  (satellite) <U3 384B 'G01' 'G02' 'G03' ... 'G30' 'G31' 'G32'
        * data       (data) <U4 112B 'stec' 'azi' 'ele' 'lon' 'lat' 'mf' 'slon'
        * site       (site) <U4 4kB 'ahaq' 'bjgb' 'dxin' ... 'ynws' 'ynya' 'zjjd'
    """
    xr_gim_slon = xr_gim2solar(xr_gim)
    pd_obs = xr_obs2pd(xr_obs)
    pd_obs_slon = pd_obs2slon(pd_obs)
    pd_diff = valid_obs_vs_gim(pd_obs_slon, xr_gim_slon)

    mask_valid = pd_diff['ref_time_pre'].notna() & pd_diff['ref_time_next'].notna()
    # 筛选 ref_time_pre 和 ref_time_next 不为 NaT 的行
    pd_diff_filtered = pd_diff[mask_valid]
    return pd_diff


def plot_gim_vs_obs(xr_gim_slon, pd_diff_filtered):
    """
    绘制1行3列的图：
    第1列：xr_gim_slon.sel(data="solar_vtec", time=np.datetime64("2023-01-10 01:00:00"))
    第2列：xr_gim_slon.sel(data="solar_vtec", time=np.datetime64("2023-01-10 02:00:00"))
    第3列：散点图，使用 pd_diff_filtered 的 slon(x), lat(y), vtec(color)
    """
    import matplotlib.pyplot as plt
    import numpy as np

    # 创建1行3列的图
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 第1列：xr_gim_slon 在 01:00:00 的数据
    gim_01 = xr_gim_slon.sel(data="solar_vtec", time=np.datetime64("2023-01-10 01:00:00"))
    im1 = axes[0].pcolormesh(gim_01.lon, gim_01.lat, gim_01, shading='auto')
    axes[0].set_title("GIM Solar VTEC at 01:00:00")
    fig.colorbar(im1, ax=axes[0], label="VTEC (TECu)")

    # 第2列：xr_gim_slon 在 02:00:00 的数据
    gim_02 = xr_gim_slon.sel(data="solar_vtec", time=np.datetime64("2023-01-10 02:00:00"))
    im2 = axes[1].pcolormesh(gim_02.lon, gim_02.lat, gim_02, shading='auto')
    axes[1].set_title("GIM Solar VTEC at 02:00:00")
    fig.colorbar(im2, ax=axes[1], label="VTEC (TECu)")

    # 第3列：散点图
    scatter = axes[2].scatter(
        pd_diff_filtered['slon'],
        pd_diff_filtered['lat'],
        c=pd_diff_filtered['vtec'],
        cmap='viridis',
        s=10
    )
    axes[2].set_xlim([-180, 180])
    axes[2].set_ylim([-90, 90])
    axes[2].set_title("Observed VTEC (Solar Coordinates)")
    axes[2].set_xlabel("Solar Longitude (deg)")
    axes[2].set_ylabel("Latitude (deg)")
    fig.colorbar(scatter, ax=axes[2], label="VTEC (TECu)")

    plt.tight_layout()
    plt.savefig("fig.png")