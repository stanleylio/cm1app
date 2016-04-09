# -*- coding: utf-8 -*-
#import sys
#sys.path.append('/home/nuc/node')
from json import dumps
from storage.storage import storage_read_only
from helper import *
from numpy import mean,median
from scipy.signal import medfilt

def query_data(dbfile,time_col,node,variable,minutes):
    """Get the latest (not necessarily fresh) "minutes" minutes of samples"""
    store = storage_read_only(dbfile=dbfile)
    table = node.replace('-','_')
    if table in store.get_list_of_tables():
        variables = store.get_list_of_columns(node)
        if variable in variables:
            r = store.read_last_N_minutes(node,time_col,minutes,cols=[time_col,variable],nonnull=variable)
            #print r
            if r is not None:
                d = {time_col:[dt2ts(t) for t in r[time_col]],
                     variable:r[variable]}
            else:
                d = {'error':'no record for {}'.format(variable)}
        else:
            d = {'error':'no such variable: {}'.format(variable)}
    else:
        d = {'error':'no such node: {}'.format(node)}
    return d

def read_latest_group_average(dbfile,time_col,node,variable):
    d = query_data(dbfile,time_col,node,variable,1)
    if 'error' in d:
        return None
    else:
        if len(d[variable]) > 3:
            return (mean(d[time_col]),mean(medfilt(d[variable],3)))
        else:
            return (mean(d[time_col]),mean(d[variable]))

def read_baro_avg(dbfile,time_col):
    store = storage_read_only(dbfile=dbfile)
    tables = store.get_list_of_tables()
    p = []
    t = []
    for table in tables:
        r = store.read_last_N(table,time_col)
        if r is not None:
            t.append(dt2ts(r[time_col][0]))
            if 'P_180' in r:
                p.append(r['P_180'][0]/1e3)
            if 'P_280' in r:
                p.append(r['P_280'][0])
    #print zip(tables,p)
    try:
        t = [t[k] if v is not None else None for k,v in enumerate(p)]
        p.remove(None)
        t.remove(None)
    except:
        pass
    return mean(t),mean(medfilt(p,3))

def qaqc(site,node,variable,reading):
    # check for null
    # check time
    # check range
    
    #if is_in_range(site,node,variable,reading):
    #    pass
    #else:
    #    print('QA/QC failed:')
    #    print((site,node,variable,reading))
    #    return False
    #return reading
    return True

def read_water_depth(dbfile,time_col,node,baro_avg=None):
    """Get water depth in meter."""
    if baro_avg is None:
        t,baro_avg = read_baro_avg(dbfile,time_col)
    r = read_latest_group_average(dbfile,time_col,node,'P_5803')
    if r is not None:
        if qaqc('poh',node,'P_5803',r[1]):
            wd = (r[1] - baro_avg)*1e3/(1.03e3*9.8)
            return r[0],wd
        else:
            print('QAQC failed in read_water_depth()')
    else:
        print('No P_5803 data to calculate water depth')

    #return float('nan'),float('nan')
    return None


#if '__main__' == __name__:
#    print query_data('/home/nuc/data/base-003/storage/sensor_data.db','ReceptionTime','node-009','d2w',30)
    

