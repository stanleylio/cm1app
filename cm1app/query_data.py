# -*- coding: utf-8 -*-
import sys,logging,time
from os.path import expanduser
sys.path.append(expanduser('~'))
from node.config.config_support import get_list_of_nodes,get_list_of_variables
from numpy import mean
from scipy.signal import medfilt
import xmlrpclib


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def unnamed(t,x):
    """calculate the medfilt-ed average from observations"""
    if len(t) > 3:
        return (mean(t),mean(medfilt(x,3)))
    else:
        return (mean(t),mean(x))

def read_latest_group_average(site,time_col,node,variable):
    proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
    d = proxy.get_last_N_minutes(node,variable,1)
    assert d is not None
    if len(d[time_col]) <= 0:
        logger.debug('No data for {} using {}'.format((site,node,variable),time_col))
        return None
    return unnamed(d[time_col],d[variable])

def read_baro_avg(site,time_col):
    t = []
    p = []
    proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
    now = time.time()
    for node in get_list_of_nodes(site):
        variables = get_list_of_variables(site,node)
        var = 'P_180'   # different units (kPa vs Pa)... WHY...
        if var in variables:
            r = proxy.query_time_range(node,var,now-60*60,now)
            if len(r[time_col]) > 0:
                t.extend(r[time_col])
                p.extend([tmp/1e3 for tmp in r[var]])
        var = 'P_280'
        if var in variables:
            r = proxy.query_time_range(node,var,now-60*60,now)
            if len(r[time_col]) > 0:
                t.extend(r[time_col])
                p.extend(r[var])
    return unnamed(t,p)

def read_water_depth(site,time_col,node,baro_avg=None):
    """Get water depth in meter."""
    if baro_avg is None:
        t,baro_avg = read_baro_avg(site,time_col)
    r = read_latest_group_average(site,time_col,node,'P_5803')
    if r is not None:
        wd = (r[1] - baro_avg)*1e3/(1.03e3*9.8)
        return r[0],wd
    else:
        logger.error('No P_5803 data to calculate water depth')
    return None


if '__main__' == __name__:
    from datetime import datetime,timedelta
#    print get_last_N_minutes('/home/nuc/data/base-003/storage/sensor_data.db','ReceptionTime','node-009','d2w',30)
    print(query_time_range('poh','node-008','d2w',datetime.utcnow() - timedelta(hours=1)))
    
