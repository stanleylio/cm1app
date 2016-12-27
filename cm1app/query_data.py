# -*- coding: utf-8 -*-
import sys,logging,time
from os.path import expanduser
sys.path.append(expanduser('~'))
from json import dumps
from node.helper import dt2ts
from node.config.config_support import config_as_dict,get_range,get_list_of_nodes,get_list_of_variables
from node.storage.storage2 import storage_read_only as store2
from node.storage.storage2 import auto_time_col,id2table
from numpy import mean
from scipy.signal import medfilt
from datetime import datetime,timedelta
from os.path import exists


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


# can probably get rid of site here too.
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

def query_time_range(site,node,variable,begin,end):
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

def get_last_N_minutes(site,node,variable,minutes):
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
    return mean(t),mean(medfilt(p,3))

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
#    print get_last_N_minutes('/home/nuc/data/base-003/storage/sensor_data.db','ReceptionTime','node-009','d2w',30)
    print(query_time_range('poh','node-008','d2w',datetime.utcnow() - timedelta(hours=1)))
    
