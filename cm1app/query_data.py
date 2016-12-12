# -*- coding: utf-8 -*-
import sys,logging,time
from os.path import expanduser
sys.path.append(expanduser('~'))
from json import dumps
from node.helper import *    #dt2ts,get_dbfile
from node.config.config_support import get_dbfile,config_as_dict,get_range,get_list_of_nodes,get_list_of_variables
#from node.storage.storage import storage_read_only
from node.storage.storage2 import storage_read_only as store2
from node.storage.storage2 import auto_time_col,id2table
from numpy import mean,median
from scipy.signal import medfilt
from datetime import datetime,timedelta
from os.path import exists


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def validate(site,node,variable):
    """Check if there's a db for the given (site,node), and
also pick a time column if there is."""
    C = config_as_dict()
    if site not in C.keys():
        logger.debug('Unknown site: {}'.format(site))
        return None
    if node not in C[site]:
        logger.debug('{} not in {}'.format(node,site))
        return None
    store = store2()    # storage2 uses MySQL. No more "path to db" problem.
    table = id2table(node)
    columns = store.get_list_of_columns(table)
    if variable not in columns:
        logger.debug('{} not in {}'.format(variable,node))
        return None
    time_col = auto_time_col(columns)
    return (store,table,time_col)

    '''# legacy sqlite stuff
    dbfile = get_dbfile(site,node)
    if dbfile is None:
        logger.error('no dbfile for {}'.format((site,node,variable)))
        return None
    assert exists(dbfile)
    store = storage_read_only(dbfile=dbfile)
    table = node.replace('-','_')
    if table not in store.get_list_of_tables():
        logger.error('table {} not found'.format(table))
        return None
    variables = store.get_list_of_columns(node)
    if variable not in variables:
        logger.error('variable {} not found'.format(variable))
        return None
    time_col = auto_time_col(variables)
    return (store,table,time_col)'''

def query_time_range(site,node,variable,begin,end):
    """Fetch samples collected in the given time period (if any)."""
    assert type(begin) is float     # caller should ensure this
    assert type(end) is float
    
    tmp = validate(site,node,variable)
    if tmp is None:
        logger.debug('Data source not found for the {} combo'.format((site,node,variable)))
        return None
    store,table,time_col = tmp
    r = store.read_time_range(node,time_col,[time_col,variable],begin,end)
    if r is None:
        logger.debug('No record for {}'.format((site,node,variable)))
        return None
    return {time_col:[dt2ts(t) for t in r[time_col]],variable:r[variable]}

# can't do this, they are not equivalent:
# one gets the latest data (not necessarily recent) (for the "latest readings" table on nodepage)
# the other gets the data (if any) in a given period of time (for interactive plots)
#def get_last_N_minutes(site,node,variable,minutes):
    #end = datetime.utcnow()
    #begin = end - timedelta(minutes=minutes)
    #return query_time_range(site,node,variable,begin,end)

def get_last_N_minutes(site,node,variable,minutes):
    """Get the latest "minutes" worth of samples where the variable is not None/NaN.
Note: the latest samples in the database may not be recent (sensor could be dead)."""
    tmp = validate(site,node,variable)
    if tmp is not None:
        store,table,time_col = tmp
        #r = store.read_last_N_minutes(node,time_col,minutes,cols=[time_col,variable],nonnull=variable)
        r = store.read_last_N_minutes(node,time_col,minutes,nonnull=variable)
        if r is not None and len(r[time_col]) > 0:
            if type(r[time_col][0]) is datetime:
                r[time_col] = [dt2ts(t) for t in r[time_col]]
            return {time_col:r[time_col],
                    variable:r[variable]}
    logger.debug('No record for {}'.format((site,node,variable)))
    return None

def read_latest_group_average(site,time_col,node,variable):
    d = get_last_N_minutes(site,node,variable,1)
    if d is None:
        logger.debug('No data for {} using {}'.format((site,node,variable),time_col))
        return None
    if len(d[variable]) > 3:
        return (mean(d[time_col]),mean(medfilt(d[variable],3)))
    else:
        return (mean(d[time_col]),mean(d[variable]))

def read_baro_avg(site,time_col):
    p = []
    t = []
    for node in get_list_of_nodes(site):
        variables = get_list_of_variables(site,node)
        if 'P_180' in variables:
            r = read_latest_group_average(site,time_col,node,'P_180')
            if r is not None and time.time() - r[0] < 60*60:
                t.append(r[0])
                p.append(r[1]/1e3)
        if 'P_280' in variables:
            r = read_latest_group_average(site,time_col,node,'P_280')
            if r is not None and time.time() - r[0] < 60*60:
                t.append(r[0])
                p.append(r[1])
    
    '''nodes = get_list_of_nodes(site)
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
        pass'''
    return mean(t),mean(medfilt(p,3))

def qaqc(site,node,variable,reading):
    # check for null
    # check timestamp
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
#    print get_last_N_minutes('/home/nuc/data/base-003/storage/sensor_data.db','ReceptionTime','node-009','d2w',30)
    print(query_time_range('poh','node-008','d2w',datetime.utcnow() - timedelta(hours=1)))
    
