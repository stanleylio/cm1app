# -*- coding: utf-8 -*-
# TODO: deprecate this file.
# lesson: don't refactor by source text block. refactor by function/purpose.
# don't write single-purpose code. a feature is "nice to have"? put it in a sandbox for easy removal.
import sys,logging,time
from os.path import expanduser
sys.path.append(expanduser('~'))
#from json import dumps
from node.config.config_support import get_list_of_nodes,get_list_of_variables
#from node.helper import dt2ts
#from node.storage.storage2 import storage_read_only as store2
#from node.storage.storage2 import auto_time_col,id2table
from numpy import mean
from scipy.signal import medfilt
#from os.path import exists
import xmlrpclib


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


'''# can probably get rid of site here too.
def validate(site,node,variable):
    """Check if site exists, if node belongs to site, and if variable is in node.
Pick a time column if all check out."""
    C = config_as_dict()

    # is there such site?
    if site not in C.keys():
        logger.debug('Unknown site: {}'.format(site))
        return None

    # does node belong to site?
    if node not in C[site]:
        logger.debug('{} not in {}'.format(node,site))
        return None
    
    # is the variable defined in the db?
    store = store2()    # storage2 uses MySQL. No more "path to db" problem.
    table = id2table(node)
    columns = store.get_list_of_columns(table)
    if variable not in columns:
        logger.debug('{} not in {}'.format(variable,node))
        return None
    time_col = auto_time_col(columns)
    return (store,table,time_col)

# can't do this, they are not equivalent:
# get_last_N_minutes() gets the latest data (even though they may be stale) (used by the "latest readings" table on nodepage)
# query_time_range() gets the data within the given period of time (if any) (used by interactive plots and paepae app)
#def get_last_N_minutes(site,node,variable,minutes):
    #end = datetime.utcnow()
    #begin = end - timedelta(minutes=minutes)
    #return query_time_range(site,node,variable,begin,end)

def OBSOLETE_query_time_range(site,node,variable,begin,end):
    """Fetch samples collected in the given time period (if any)."""
    assert type(begin) in [float,int]
    assert type(end) in [float,int]
    
    tmp = validate(site,node,variable)
    if tmp is None:
        logger.debug('Data source not found for the {} combo'.format((site,node,variable)))
        return None
    store,table,time_col = tmp
    r = store.read_time_range(node,time_col,[time_col,variable],begin,end)
    if r is None:
        logger.debug('No record for {}'.format((site,node,variable)))
        return None

    if type(r[time_col][0]) is datetime:
        r[time_col] = [dt2ts(tmp) for tmp in r[time_col]]
    return r

def OBSOLETE_get_last_N_minutes(site,node,variable,minutes):
    """Get the latest "minutes" worth of samples where the variable is not None/NaN.
Note: the latest samples in the database may not be recent (sensor could be dead)."""
    tmp = validate(site,node,variable)
    if tmp is not None:
        store,table,time_col = tmp
        r = store.read_last_N_minutes(node,time_col,minutes,nonnull=variable)
        if r is not None and len(r[time_col]) > 0:
            if type(r[time_col][0]) is datetime:
                r[time_col] = [dt2ts(t) for t in r[time_col]]
            return {time_col:r[time_col],
                    variable:r[variable]}
    logger.debug('No record for {}'.format((site,node,variable)))
    return None
'''


def unnamed(t,x):
    """calculate the medfilt-ed average from observations"""
    if len(t) > 3:
        return (mean(t),mean(medfilt(x,3)))
    else:
        return (mean(t),mean(x))


# TODO: get rid of this
def read_latest_group_average(site,time_col,node,variable):
    #d = get_last_N_minutes(site,node,variable,1)
    proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
    d = proxy.get_last_N_minutes(node,variable,1)
    assert d is not None
    if len(d[time_col]) <= 0:
        logger.debug('No data for {} using {}'.format((site,node,variable),time_col))
        return None
    if len(d[variable]) > 3:
        return (mean(d[time_col]),mean(medfilt(d[variable],3)))
    else:
        return (mean(d[time_col]),mean(d[variable]))

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
    
