# TODO: To see a good API design, look at RabbitMQ's management console.
#... just get rid of "site" already will you? TODO
#
# Given how fast direct access to the db is, I'm not even sure I need
# redis here.
import sys, redis, json, time
sys.path.append('/home/nuc')
from flask import Flask, Markup, Response, request, escape
from datetime import timedelta
from cm1app import app
#from node.storage.storage2 import Storage
from node.config.c import get_list_of_sites, get_list_of_devices, get_node_attribute, get_variable_attribute, get_list_of_disp_vars
from cm1app.query_data import read_latest_sample
from cm1app.common import auto_time_col


@app.route('/<site>/data/dashboard.json')
def data_dashboard(site):
    """Examples:
    Either specify a valid "site":
        https://grogdata.soest.hawaii.edu/poh/data/dashboard.json
    Or specify the list of nodes ("site" will be ignored):
        https://grogdata.soest.hawaii.edu/poh/data/dashboard.json?nodes=node-049,base-011
    """

    # Either supply a list of nodes as query params, or specify a valid "site" name
    nodes = request.args.get('nodes', default=None)
    if nodes is not None:
        nodes = [node.strip() for node in nodes.split(',')]
    else:
        if site not in get_list_of_sites():
            return 'Error: Unknown site: {}'.format(site)
        nodes = get_list_of_devices(site=site)
    #store = Storage()
    redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)

    S = {}
    # "only for nodes defined in the site config AND have table in db"
    # TODO: "... AND have at least one visible variable"
    #nodes = set(nodes).intersection(set([tmp.replace('_', '-') for tmp in store.get_list_of_tables()]))
    for node in nodes:
        S[node] = {}
        S[node]['name'] = get_node_attribute(node, 'name')
        S[node]['location'] = get_node_attribute(node, 'location')
        S[node]['latest_non_null'] = {}
        S[node]['time_col'] = None

        dbcols = get_list_of_disp_vars(node)
        #time_col = auto_time_col(store.get_list_of_columns(node))
        time_col = auto_time_col(node)
        S[node]['time_col'] = time_col
        
        #for var in set(dbcols).intersection(set(get_list_of_disp_vars(node))):
        for var in dbcols:
            # Response format: [timestamp, value, unit, [lower bound, upper bound], interval, description]
            r = []

            # TIME AND LATEST VALUE
            # Latest readings are cached in redis.
            # They are being cached by log2mysql.py as they come in, as well as inserted after db query here (due to cache miss).
            tmp = redis_server.get('latest:{}:{}'.format(node, var))
            if tmp:
                # cache hit
                r = json.loads(tmp.decode())
            else:
                # cache miss. query db
                
                #tmp = store.read_latest_non_null(node, time_col, var)
                #if tmp:
                #    r = [tmp[time_col], tmp[var]]
                #    # put in cache (to speed up the decommissioned ones)
                #    redis_server.set('latest:{}:{}'.format(node, var), json.dumps(r), ex=int(timedelta(days=1).total_seconds()))
                #else:
                #    r = [None, None]
                r = read_latest_sample(time_col, node, var)
                if r is None:
                    # we have no data at all for this (node, var) combo
                    r = [None, None]
                else:
                    # got something. cache it
                    redis_server.set('latest:{}:{}'.format(node, var), json.dumps(r), ex=int(timedelta(days=1).total_seconds()))

            # UNIT
            r.append(get_variable_attribute(node, var, 'unit'))

            # BOUNDARIES
            lb = get_variable_attribute(node, var, 'lower_bound')
            ub = get_variable_attribute(node, var, 'upper_bound')
            b = [lb, ub]
            #b = [None if tmp in [float('-inf'), float('inf')] else tmp for tmp in b]
            r.append(b)

            # INTERVAL
            v = get_variable_attribute(node, var, 'interval_second')
            if v is None or v != v: # NaN != NaN
                v = None
            r.append(v)

            # DESCRIIPTION
            r.append(get_variable_attribute(node, var, 'description'))

            S[node]['latest_non_null'][var] = r

    # site info (data source, location etc.)
    #base = site_base_map[site]
    r = {'site':site,
         #'data_src':base,
         #'data_src_name':get_attr(base,'note'),
         #'location':get_attr(base,'location'),
         #'gmap_link':get_attr(base,'google_earth_link'),
         'nodes':S}
    
    return Response(json.dumps(r, separators=(',', ':')),
                    mimetype='application/json; charset=utf-8')

