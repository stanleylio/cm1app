import sys, logging, math
from os.path import expanduser
sys.path.append(expanduser('~'))
from datetime import datetime
from node.storage.storage2 import storage, auto_time_col
from node.helper import dt2ts


def condense(d, max_count):
    """recursively subsample d until len(d) <= max_count
subsample at a 2:1 ratio"""
    assert type(max_count) in [float, int]
    if len(d) > max_count:
        return condense(d[0::2], max_count)
    return d

# Simple to write yes, but the whole row is discarded when any field is None/NaN.
def strip_none_nan(r):
    # convert None into float('nan')
    #r[var] = [float('nan') if tmp is None else tmp for tmp in r[var]]
    # ... or just strip them. I can't plot them anyway.
    # XMLRPC doesn't do None (without sacrificing compatibility); JSON doesn't do NaN...
    # so... just strip them.
    if len(r[list(r.keys())[0]]) <= 0:
        return r

    # early stage poor decision lingers forever...
    d = zip(*[r[k] for k in r.keys()])
    d = filter(lambda row: all([tmp is not None for tmp in row]), d)
    d = filter(lambda row: all([not math.isnan(tmp) for tmp in row]), d)
    
    #r = zip(r[time_col],r[var])
    #r = filter(lambda x: x[1] is not None,r)
    #r = filter(lambda x: not math.isnan(x[1]),r)
    #r = zip(*r)
    #return {time_col:r[0],var:r[1]}
    return dict(zip(r.keys(), zip(*d)))

def query_time_range(node, variables, begin, end, time_col):
    assert type(begin) in [float, int],"begin is not float/int"
    assert type(end) in [float, int],"end is not float/int"
    #assert begin < end,"begin >= end"
    store = storage()
    if type(variables) is not list:
        tmp = list([variables])
    else:
        tmp = variables
    #tmp.insert(0,time_col)
    r = store.read_time_range(node, time_col, tmp, begin, end)
    r = strip_none_nan(r)
    #r = fix_ts_format(r,time_col)
    return r

def query_time_range2(node,variables,begin,end,time_col):
    assert type(begin) in [float,int],"begin must be a float/int"
    assert type(end) in [float,int],"end must be a float/int"
    store = storage()
    if type(variables) is not list:
        tmp = list([variables])
    else:
        tmp = variables
    r = store.read_time_range2(node, time_col, tmp, begin, end)
    r = filter(lambda p: all([v is not None for v in p]),r)     # reject any row containing None
    r = filter(lambda p: all([not math.isnan(v) for v in p]), r) # reject any row containing NaN
    return list(r)

def get_last_N_minutes(node, var, minutes):
    assert type(minutes) in [float, int] and minutes > 0
    store = storage()
    time_col = auto_time_col(store.get_list_of_columns(node))
    r = store.read_last_N_minutes(node,time_col,minutes,nonnull=var)
    r = strip_none_nan(r)
    return r

# I'll worry about performance later. like reusing db connection etc.
def get_list_of_tables():
    store = storage()
    return store.get_list_of_tables()

def get_list_of_columns(node):
    store = storage()
    return store.get_list_of_columns(node)


if '__main__' == __name__:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    from xmlrpc.server import SimpleXMLRPCServer
    server = SimpleXMLRPCServer(('localhost', 8000), allow_none=True, logRequests=False)
    #server = SimpleXMLRPCServer(('localhost', 8000)) # who knows, these may be rewritten in Haskell/Golang later.
    server.register_function(condense, 'condense')
    server.register_function(query_time_range, 'query_time_range')
    server.register_function(query_time_range2, 'query_time_range2')
    server.register_function(get_last_N_minutes, 'get_last_N_minutes')
    server.register_function(get_list_of_tables, 'get_list_of_tables')
    server.register_function(get_list_of_columns, 'get_list_of_columns')
    server.serve_forever()
