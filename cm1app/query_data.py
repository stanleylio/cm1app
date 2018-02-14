# -*- coding: utf-8 -*-
from __future__ import division
import sys, logging, time
from os.path import expanduser
sys.path.append(expanduser('~'))
from node.config.config_support import get_list_of_nodes, get_list_of_variables
from node.helper import dt2ts
from datetime import datetime
from numpy import mean
from scipy.signal import medfilt
import xmlrpclib


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def unnamed(t, x):
    """calculate the medfilt-ed average from observations"""
    if len(t) > 3:
        return (mean(t), mean(medfilt(x, 3)))
    else:
        return (mean(t), mean(x))

def last(t, x):
    return (t[-1], x[-1])

def read_latest_group_average(site, time_col, node, variable):
    proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
    d = proxy.get_last_N_minutes(node, variable, 1)
    assert d is not None
    if len(d[time_col]) <= 0:
        logger.debug('No data for {} using {}'.format((site, node, variable), time_col))
        return None
    #return unnamed(d[time_col], d[variable])
    return last(d[time_col], d[variable])

def read_baro_avg(site, time_col):
    t = []
    p = []
    proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
    now = time.time()
    for node in get_list_of_nodes(site):
        variables = get_list_of_variables(node)
        var = 'P_180'   # different units (kPa vs Pa)... WHY...
        if var in variables:
            r = proxy.query_time_range(node,['ReceptionTime', var], now-60*60, now, 'ReceptionTime')
            if len(r[time_col]) > 0:
                t.extend(r[time_col])
                p.extend([tmp/1e3 for tmp in r[var]])
        var = 'P_280'
        if var in variables:
            r = proxy.query_time_range(node,['ReceptionTime', var], now-60*60, now, 'ReceptionTime')
            if len(r[time_col]) > 0:
                t.extend(r[time_col])
                p.extend(r[var])
    return unnamed(t, p)

'''def read_water_depth(site,time_col,node,baro_avg=None):
    """Get water depth in meter."""
    if baro_avg is None:
        t,baro_avg = read_baro_avg(site,time_col)
    r = read_latest_group_average(site,time_col,node,'P_5803')
    if r is not None:
        wd = (r[1] - baro_avg)*1e3/(1.03e3*9.8)
        return r[0],wd
    else:
        logger.error('No P_5803 data to calculate water depth')
    return None'''

# - - - - -
# TODO: merge the following two functions.
# ... or should I?
# map to node, correct for config change (moved sensor etc.), scale and convert unit, filter, remove junk... all optional
# - - - - -
# query water depth in meter by location (makaha/dock) (not by node)
# written specifically for the poh apps
def read_water_depth_by_location(site, location, begin, end):
    time_col = 'ReceptionTime'
    
    if 'poh' == site:
        mnmap = {'makaha1':'node-049',
                 'makaha2':'node-008',
                 'makaha3':'node-051',
                 'river':'node-014',}
        vnmap = {'makaha1':'d2w',
                 'makaha2':'d2w',
                 'makaha3':'d2w',
                 'river':'d2w',}
        fnmap = {'makaha1':lambda x: (50.7 + 1100 - x)/1e3,
                 'makaha2':lambda x: (50.7 + 2180 - x)/1e3,
# TODO
                 'makaha3':lambda x: (1701.8 - x)/1e3,  # 5'7" is for node-015 - need cal for node-051
                 'river':lambda x: (1422 - x)/1e3,}     # temporary, peak of past 229 days
    elif 'makaipier' == site:
        mnmap = {'dock1':'node-010',}
        vnmap = {'dock1':'d2w',}
        fnmap = {'dock1':lambda x: (6197.6 - x)/1e3,}
    elif 'coconut' == site:
        mnmap = {'noaa':'node-046',
                 'bridge':'node-040'}
        vnmap = {'noaa':'d2w',
                 'bridge':'d2w'}
        fnmap = {'noaa':lambda x: (1400 - x)/1e3,       # again, just the peak. need actual cal params TODO
                 'bridge':lambda x: (2900 - x)/1e3,}    # TODO
    else:
        assert False

    if begin > end:
        return [[], []]
    
    proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
    d = proxy.query_time_range(mnmap[location], [time_col, vnmap[location]], begin, end, time_col)

    t = d[time_col]
    d = d[vnmap[location]]

    # convert distance to water (d2w in mm) to water depth (in meter)
    d = [fnmap[location](tmp) for tmp in d]

    # strip all out-of-range readings
    #d = [tmp if tmp >= 0 else float('nan') for tmp in d]
    d = [tmp for tmp in d if tmp >= 0]

    # remove spike
    d = medfilt(d, 21)

    # don't need(claim) that many digits...
    d = [round(tmp, 3) for tmp in d]
    
    return [t, d]


def read_optode_by_location(site, location, begin, end, var):
    time_col = 'ReceptionTime'
    
    if 'poh' == site:
        mnmap = {'makaha1':'node-004',}
        vvnmap = {'oxygen':{'makaha1':'O2Concentration',},
                  'air':{'makaha1':'AirSaturation',},
                  'temperature':{'makaha1':'Temperature',}}
        vnmap = vvnmap[var]
        fnmap = {'makaha1':lambda x: x,}
    else:
        assert False

    if begin > end:
        return [[], []]
    proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
    d = proxy.query_time_range(mnmap[location], [time_col, vnmap[location]], begin, end, time_col)

    t = d[time_col]
    d = d[vnmap[location]]

    # strip all out-of-range readings
    d = [tmp if tmp >= 0 else float('nan') for tmp in d]

    # remove spike
    #d = medfilt(d,21)

    # don't need(claim) that many digits...
    d = [round(tmp,3) for tmp in d]
    
    return [t,d]


# this scheme doesn't make sense.

def read_ctd_by_location(site, location, begin, end, var):
    time_col = 'ReceptionTime'

    if 'poh' == site:
        mnmap = {'makaha1':'node-025',}
        vnmap = {'makaha1':'salinity_seabird'}
        fnmap = {'makaha1':lambda x: x,}
    else:
        assert False

    if begin > end:
        return [[],[]]
    proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
    d = proxy.query_time_range(mnmap[location], [time_col, vnmap[location]], begin, end, time_col)

    t = d[time_col]
    d = d[vnmap[location]]

    # strip all out-of-range readings
    d = [tmp if tmp >= 0 else float('nan') for tmp in d]

    # remove spike
    #d = medfilt(d,21)

    # don't need(claim) that many digits...
    d = [round(tmp,3) for tmp in d]
    
    return [t,d]


if '__main__' == __name__:
    from datetime import datetime, timedelta
#    print get_last_N_minutes('/home/nuc/data/base-003/storage/sensor_data.db','ReceptionTime','node-009','d2w',30)
    print(query_time_range('poh', 'node-008', 'd2w', datetime.utcnow() - timedelta(hours=1)))
    
