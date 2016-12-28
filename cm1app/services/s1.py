import sys,logging
from os.path import expanduser
sys.path.append(expanduser('~'))
from datetime import datetime
from node.storage.storage2 import storage_read_only
from node.helper import dt2ts


def condense(d,max_count):
    """recursively subsample d until len(d) <= max_count
subsample at a 2:1 ratio"""
    assert type(max_count) in [float,int]
    if len(d) > max_count:
        return condense(d[0::2],max_count)
    return d


def strip_none(r,time_col,var):
    # convert None into float('nan')
    #r[var] = [float('nan') if tmp is None else tmp for tmp in r[var]]
    # ... or just strip them. I can't plot them anyway.
    # XMLRPC doesn't do None (without sacrificing compatibility); JSON doesn't do NaN...
    # so... just strip them.
    if len(r[time_col]) <= 0:
        return r
    r = zip(r[time_col],r[var])
    r = filter(lambda x: x[1] is not None,r)
    r = zip(*r)
    return {time_col:r[0],var:r[1]}


def fix_ts_format(r,time_col,var):
    # convert datetime.datetime to POSIX timestamps (float)
    if len(r[time_col]) <= 0:
        return r
    if type(r[time_col][0]) is datetime:
        logging.debug('This thing is still using datetime instead of timestamp: {}'.format((node,var)))
        r[time_col] = [dt2ts(tmp) for tmp in r[time_col]]
    return r

store = storage_read_only()

def query_time_range(node,var,begin,end):
    assert type(begin) in [float,int]
    assert type(end) in [float,int]
    assert begin < end
    time_col = 'ReceptionTime'
    r = store.read_time_range(node,time_col,[time_col,var],begin,end)
    r = strip_none(r,time_col,var)
    r = fix_ts_format(r,time_col,var)
    return r


def get_last_N_minutes(node,var,minutes):
    assert minutes > 0
    time_col = 'ReceptionTime'
    r = store.read_last_N_minutes(node,time_col,minutes,nonnull=var)
    r = strip_none(r,time_col,var)
    r = fix_ts_format(r,time_col,var)
    return r


if '__main__' == __name__:
    from SimpleXMLRPCServer import SimpleXMLRPCServer
    #server = SimpleXMLRPCServer(('localhost',8000),allow_none=True)
    server = SimpleXMLRPCServer(('localhost',8000)) # who knows, these may be rewritten by Haskell/Golang later.
    server.register_function(condense,'condense')
    server.register_function(query_time_range,'query_time_range')
    server.register_function(get_last_N_minutes,'get_last_N_minutes')
    server.serve_forever()
