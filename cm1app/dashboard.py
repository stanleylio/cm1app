# TODO: To see a good API design, look at RabbitMQ's management console.
#... just get rid of "site" already will you? TODO
import sys, redis, json, time, MySQLdb
sys.path.append('/home/nuc')
from flask import Flask, Markup, Response, request, escape
from datetime import timedelta
from cm1app import app
from node.config.c import get_list_of_sites, get_list_of_devices, get_node_attribute, get_variable_attribute, get_list_of_disp_vars
from cm1app.common import auto_time_col


# - - - - -
# Compare this to the value in log2redis.py:
# That one puts the real-time stuff in the cache, so if an instrument
# hits that script the instrument is probably still operational.
# Here this script also needs to deal with dead and decommissioned
# instruments, and those are not expected to come back alive soon. Hence
# the long TTL value.
redis_TTL_second = int(timedelta(days=60).total_seconds())
# - - - - -


def read_latest_sample(time_col, node, var, conn):
    try:
        cur = conn.cursor()
        cmd = """SELECT `{time_col}`,`{var}`
                FROM uhcm.`{node}`
                WHERE `{var}` IS NOT NULL
                ORDER BY `{time_col}` DESC LIMIT 1""".format(time_col=time_col, node=node, var=var)
        cur.execute(cmd)
        return list(cur.fetchone())
    except (MySQLdb.OperationalError, TypeError):
        # you get TypeError if fetchone returns no row.
        return None


@app.route('/<site>/data/dashboard.json')
def data_dashboard(site):
    """Examples:
    Either specify a valid "site":
        https://grogdata.soest.hawaii.edu/poh/data/dashboard.json
    Or specify the list of nodes ("site" will be ignored):
        https://grogdata.soest.hawaii.edu/poh/data/dashboard.json?nodes=node-049,base-011
    """

    conn = MySQLdb.connect('localhost', user='webapp', charset='utf8mb4')

    with conn:
        # Either supply a list of nodes as query params, or specify a valid "site" name
        nodes = request.args.get('nodes', default=None)
        if nodes is not None:
            nodes = [node.strip() for node in nodes.split(',')]
        else:
            if site not in get_list_of_sites(conn=conn):
                return 'Error: Unknown site: {}'.format(site)
            nodes = get_list_of_devices(site=site, conn=conn)
        
        redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)
        
        S = {}
        # "only for nodes defined in the site config AND have table in db"
        # TODO: "... AND have at least one visible variable"
        #nodes = set(nodes).intersection(set([tmp.replace('_', '-') for tmp in store.get_list_of_tables()]))
        for node in nodes:
            S[node] = {}
            S[node]['name'] = get_node_attribute(node, 'name', conn=conn)
            S[node]['location'] = get_node_attribute(node, 'location', conn=conn)
            S[node]['latest_non_null'] = {}
            S[node]['time_col'] = None
            S[node]['deployment_status'] = get_node_attribute(node, 'deployment_status', conn=conn)

            dbcols = get_list_of_disp_vars(node, conn=conn)
            time_col = auto_time_col(node, conn=conn)
            S[node]['time_col'] = time_col
            
            # Huh. If you want to (premature) optimize, you don't even
            # need to hit the db for latest readings if
            # deployment_state=='decommissioned'.

            #for var in set(dbcols).intersection(set(get_list_of_disp_vars(node))):
            for var in dbcols:
                # Response format: [timestamp, value, unit, [lower bound, upper bound], interval, description]
                r = []

                # TIME AND LATEST VALUE
                # Latest readings are cached in redis.
                # They are being cached by log2redis.py as they come in.
                # When there is a cache miss, the latest readings are
                # retrived from the db and cached as well.
                tmp = redis_server.get('latest:{}:{}'.format(node, var))
                if tmp:
                    # cache hit
                    r = json.loads(tmp.decode())
                else:
                    # cache miss. query db
                    r = read_latest_sample(time_col, node, var, conn)
                    if r is None:
                        # we have no data at all for this (node, var) combo
                        r = [None, None]
                    #else:

                # If it's from the db, cache it; if it's from the
                # cache... well putting it back would renew its TTL. And
                # if there is no data, that too should be cached so we
                # won't hit the db again (REQUIREMENT: log2redis.py must
                # be running correctly)
                redis_server.set('latest:{}:{}'.format(node, var), json.dumps(r), ex=redis_TTL_second)

                # UNIT
                r.append(get_variable_attribute(node, var, 'unit', conn=conn))

                # BOUNDARIES
                lb = get_variable_attribute(node, var, 'lower_bound', conn=conn)
                ub = get_variable_attribute(node, var, 'upper_bound', conn=conn)
                b = [lb, ub]
                #b = [None if tmp in [float('-inf'), float('inf')] else tmp for tmp in b]
                r.append(b)

                # INTERVAL
                v = get_variable_attribute(node, var, 'interval_second', conn=conn)
                if v is None or v != v: # NaN != NaN
                    v = None
                r.append(v)

                # DESCRIIPTION
                r.append(get_variable_attribute(node, var, 'description', conn=conn))

                S[node]['latest_non_null'][var] = r

    # site info (data source, location etc.)
    #base = site_base_map[site]
    r = {'site':site,
         #'data_src':base,
         #'data_src_name':get_attr(base,'note'),
         #'location':get_attr(base,'location'),
         #'gmap_link':get_attr(base,'google_earth_link'),
         'nodes':S,
         'server_time':round(time.time(), 3)}

    return Response(json.dumps(r, separators=(',', ':')),
                    mimetype='application/json; charset=utf-8')

