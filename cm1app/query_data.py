# -*- coding: utf-8 -*-
import sys,logging
from os.path import expanduser
sys.path.append(expanduser('~'))
from json import dumps
from node.storage.storage import storage_read_only
from node.helper import *    #dt2ts,ts2dt,get_dbfile
from node.config.config_support import get_dbfile
from numpy import mean,median
from scipy.signal import medfilt
from datetime import datetime,timedelta
from os.path import exists


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def validate(site,node,variable):
    """Check if there's a db for the given (site,node), and
select a time column."""
    #if site in ['makaipier','sf'] and node in ['node-010','node-011','node-012']:
    if site in ['makaipier','sf']:
        from storage.storage2 import storage_read_only as S
        from storage.storage2 import auto_time_col,id2table
        store = S()     # storage2 uses MySQL. No more "path to db" problem.
        table = id2table(node)
        time_col = auto_time_col(store.get_list_of_columns(table))
        return (store,table,time_col)

    # legacy sqlite stuff
    
    dbfile = get_dbfile(site,node)
    if dbfile is None or not exists(dbfile):
        logger.error('no dbfile for {}'.format((site,node,variable)))
        return None
    store = storage_read_only(dbfile=dbfile)
    table = node.replace('-','_')
    if table not in store.get_list_of_tables():
        logger.error('table {} not found'.format(table))
        return None
    variables = store.get_list_of_columns(node)
    if variable not in variables:
        logger.error('variable {} not found'.format(variable))
        return None
    if 'ReceptionTime' in variables:
        time_col = 'ReceptionTime'
    elif 'Timestamp' in variables:
        time_col = 'Timestamp'
    else:
        logger.error('no timestamp found in db')
        return None
    return (store,table,time_col)

def query_time_range(site,node,variable,begin,end=None):
    tmp = validate(site,node,variable)
    if tmp is not None:
        store,table,time_col = tmp
        if type(begin) is float:
            begin = ts2dt(begin)
        if type(end) is float:
            end = ts2dt(end)
        r = store.read_time_range(node,time_col,[time_col,variable],begin,end)
        if r is not None:
            d = {time_col:[dt2ts(t) for t in r[time_col]],
                 variable:r[variable]}
            return d
    #d = {'error':'no record for {}'.format((site,node,variable))}
    logger.warning('no record for {}'.format((site,node,variable)))
    return None

# can't do this, they are not equivalent:
# one gets the latest data (they may not be recent data) (for the table on node_page)
# the other gets the data (if any) in a given period of time (generic time range queries)
#def query_data(site,node,variable,minutes):
    #end = datetime.utcnow()
    #begin = end - timedelta(minutes=minutes)
    #return query_time_range(site,node,variable,begin,end)

def query_data(site,node,variable,minutes):
    """Get the latest "minutes" worth of samples.
Note: the latest samples in the database may not be recent (sensor could be dead)."""
    tmp = validate(site,node,variable)
    if tmp is not None:
        store,table,time_col = tmp
        r = store.read_last_N_minutes(node,time_col,minutes,cols=[time_col,variable],nonnull=variable)
        if r is not None and len(r[time_col]) > 0:
            if type(r[time_col][0]) is datetime:
                r[time_col] = [dt2ts(t) for t in r[time_col]]
            d = {time_col:r[time_col],
                 variable:r[variable]}
            return d
    d = {'error':'no record for {}'.format((site,node,variable))}
    return d

def read_latest_group_average(site,time_col,node,variable):
    d = query_data(site,node,variable,1)
    if d is not None:
        if len(d[variable]) > 3:
            return (mean(d[time_col]),mean(medfilt(d[variable],3)))
        else:
            return (mean(d[time_col]),mean(d[variable]))

def read_baro_avg(site,time_col):
    from config.config_support import get_range,get_list_of_nodes

    p = []
    t = []
    nodes = get_list_of_nodes(site)
    for node in nodes:
        table = node.replace('-','_')
        dbfile = get_dbfile(site,node)
        store = storage_read_only(dbfile=dbfile)
    #tables = store.get_list_of_tables()
    #for table in tables:
        r = store.read_last_N(table,time_col)
        # Explicit freshness check is more robust, but median(t) is cleaner.
        if r is not None and \
           datetime.utcnow() - r[time_col][0] < timedelta(minutes=30):
# OH MAN.
            if 'P_180' in r:
                if r['P_180'][0] in get_range('poh',table,'P_180'):
                    t.append(dt2ts(r[time_col][0]))
                    p.append(r['P_180'][0]/1e3)
            if 'P_280' in r:
                if r['P_280'][0] in get_range('poh',table,'P_280'):
                    t.append(dt2ts(r[time_col][0]))
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

def read_water_depth(site,time_col,node,baro_avg=None):
    """Get water depth in meter."""
    if baro_avg is None:
        t,baro_avg = read_baro_avg(site,time_col)
    r = read_latest_group_average(site,time_col,node,'P_5803')
    if r is not None:
        if qaqc('poh',node,'P_5803',r[1]):
            wd = (r[1] - baro_avg)*1e3/(1.03e3*9.8)
            return r[0],wd
        else:
            logger.error('QAQC failed in read_water_depth()')
    else:
        logger.error('No P_5803 data to calculate water depth')
    return None


if '__main__' == __name__:
#    print query_data('/home/nuc/data/base-003/storage/sensor_data.db','ReceptionTime','node-009','d2w',30)
    print(query_time_range('poh','node-008','d2w',datetime.utcnow() - timedelta(hours=1)))
    
