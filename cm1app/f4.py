import logging, xmlrpc.client, socket, json
from flask import Flask, render_template, request, escape
from cm1app import app
from datetime import datetime, timedelta
from node.helper import dt2ts
from node.config.c import config_as_dict, get_list_of_devices, get_list_of_variables, get_variable_attribute
from cm1app import panels, dashboard, nodepage, v5
from cm1app.common import validate_id


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


@app.route('/')
def route_default():
    return render_template('index.html')

# migrated varpage from this. I don't think anything else is using this now.
'''@app.route('/<site>/data/<node>/<variable>.json')
def site_node_variable(site, node, variable):
    """Examples:
http://192.168.0.20:5000/poh/data/node-009/d2w.json?minutes=1

The "site" argument is ignored.
"""

    logger.debug((site, node, variable))

    b,m = validate_id(node)
    if not b:
        return m

    conn = _config_import()

    try:
        if node not in get_list_of_devices(conn=conn):
            return 'No such node: {}'.format(escape(node))

        if variable not in get_list_of_variables(node, conn=conn):
            return 'No such variable: {}'.format(escape(variable))
    
        begin = request.args.get('begin')
        end = request.args.get('end')
        minutes = request.args.get('minutes')
        max_count = request.args.get('max_count')

        #variable = str(variable)    # storage.py doesn't like unicode variable names... TODO
        unit = get_variable_attribute(node, variable, 'unit', conn=conn)
        desc = get_variable_attribute(node, variable, 'description', conn=conn)
        bounds = get_range(node, variable)
        lb = get_variable_attribute(node, variable, 'lower_bound', conn=conn)
        ub = get_variable_attribute(node, variable, 'upper_bound', conn=conn)
        b = [lb, ub]
        bounds = [None if tmp in [float('-inf'), float('inf')] else tmp for tmp in b]

        d = {'unit':unit,
             'description':desc,
             'bounds':bounds,
             'samples':None}

        proxy = xmlrpc.client.ServerProxy('http://127.0.0.1:8000/')
        if begin is not None:
            begin = float(begin)
            end = float(end)
            logger.debug('from {} to {}'.format(begin, end))
            r = proxy.query_time_range(node, [time_col, variable], begin, end, time_col)
        else:
            if minutes is None:
                minutes = 24*60
            minutes = float(minutes)
            logger.debug('minutes={}'.format(minutes))
            r = proxy.get_last_N_minutes(node, variable, minutes)

        # deal with max_count
        #if 'error' not in r and max_count is not None:
        if max_count is not None:
            max_count = int(max_count)
            if max_count > 0:
                assert 2 == len(r.keys())   # a time column and a variable column
                #time_col = list(set(r.keys()) - set([variable]))[0]
                tmp = list(zip(r[time_col], r[variable]))
                tmp = proxy.condense(tmp, max_count)
                tmp = list(zip(*tmp))
                r = {time_col:tmp[0], variable:tmp[1]}
        
        d['samples'] = r
        return json.dumps(d, separators=(',',':'))
    except:
        logging.exception('')
        return "it's beyond my paygrade"
'''

# wait who is using this again?
@app.route('/data/2/config/listing')
def get_listing():
    return json.dumps(config_as_dict(), separators=(',',':'))

# check __init__.py for the line that enables CORS at this endpoint
@app.route('/data/2/<node>/<variables>.json')
#@cross_origin() this doesn't work for some reason
def get_xy(node, variables):
    """Example:
https://grogdata.soest.hawaii.edu/data/2/node-047/Timestamp,d2w,t.json?begin=1500000000&end=1500082230&time_col=Timestamp
"""
    logger.debug((node, variables))

    variables = variables.split(',')                # assumption: no comma in variable name... it seems most of programming is the problem of encoding and decoding. "Do you mean this word literally or do you mean the thing behind this word"...
    variables = [v.strip() for v in variables]
    begin = request.args.get('begin')
    end = request.args.get('end')
    time_col = request.args.get('time_col').strip()

    if begin is None:
        return 'missing: begin'
    if end is None:
        return 'missing: end'
    if time_col is None:
        return 'missing: time_col'

    if time_col not in variables:
        return '"time_col" must be among the list of variables. Most likely one of {"ReceptionTime","Timestamp","ts"}.'

    try:
        begin = float(begin)
        end = float(end)
    except ValueError:
        return '"begin" and "end" must be numbers.'

    try:
        if node not in get_list_of_devices():
            return 'No such node: {}'.format(escape(node))

        columns = get_list_of_variables(node)
        if time_col not in columns:
            return 'No such time column: {}'.format(escape(time_col))
        for var in variables:
            if var not in columns:
                return 'No such variable: {}'.format(escape(var))

        proxy = xmlrpc.client.ServerProxy('http://127.0.0.1:8000/')
        r = proxy.query_time_range2(node, variables, begin, end, time_col)
        return json.dumps(r, separators=(',', ':'))
    except:
        logging.exception('')
        return "it's beyond my paygrade 2"

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/tech/')
def tech():
    return render_template('tech.html')

@app.route('/tech/tidegauge/')
def tidegauge():
    return render_template('tidegauge.html')

@app.route('/tech/logger/')
def kiwilogger():
    return render_template('logger.html')

@app.route('/tech/loggerhd/')
def kiwiloggerhd():
    return render_template('loggerhd.html')

@app.route('/dev/')
def dev():
    return render_template('dev.html')

@app.route('/dev/rtcomm')
def rtcomm():
    return render_template('rtcomm.html')

@app.route('/project_info/')
def project_info():
    return render_template('project_info.html')

@app.route('/data_access/')
def data_access():
    return render_template('data_access.html')
