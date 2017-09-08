# -*- coding: utf-8 -*-
# todo: reserve Flask for rendering and routing only. everything else via RPC ("microservice").
import traceback,sys,logging
from os.path import expanduser
sys.path.append(expanduser('~'))
from flask import Flask,render_template,request,escape
from cm1app import app
from json import dumps
from datetime import datetime,timedelta
from node.helper import dt2ts
from node.config.config_support import get_unit,get_description,config_as_dict
from node.storage.storage2 import storage
from panels import *
from dashboard import *
from nodepage import *
#from s3 import *
import v4,v5
import xmlrpclib,socket


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

sites = config_as_dict().keys()


@app.route('/')
def route_default():
    return render_template('index.html')

@app.route('/<site>/data/<node>/<variable>.json')
def site_node_variable(site,node,variable):
    """Examples:
http://192.168.0.20:5000/poh/data/node-009/d2w.json?minutes=1

"site" needs to be one of the defined sites, but it no longer checks if
the node is in that particular site. Trying to phase out the concept of "site".
"""

    logger.debug((site,node,variable))

    #if site not in ['poh','coconut','makaipier','sf']:
    if site not in sites:
        logger.error('no such site: {}'.format(escape(site)))
        return 'No such site: {}'.format(escape(site))

    store = storage()
    if node not in store.get_list_of_tables():
        return 'No such node: {}'.format(escape(node))

    if variable not in store.get_list_of_columns(node):
        return 'No such variable: {}'.format(escape(variable))
    
    try:
        begin = request.args.get('begin')
        end = request.args.get('end')
        minutes = request.args.get('minutes')
        max_count = request.args.get('max_count')

        variable = str(variable)    # storage.py doesn't like unicode variable names... TODO
        unit = get_unit(node,variable)
        desc = get_description(node,variable)
        bounds = get_range(node,variable)
        if bounds is None:
            bounds = [float('-inf'),float('inf')]
        else:
            bounds = [None if tmp in [float('-inf'),float('inf')] else tmp for tmp in bounds]

        d = {'unit':unit,
             'description':desc,
             'bounds':bounds,
             'samples':None}

        proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
        
        if begin is not None:
            begin = float(begin)
            if end is None:
                end = dt2ts()     # assumption: database time too is in UTC
            else:
                end = float(end)
            if begin >= end:
                # don't actually need this check - sql will just give you [] in this case.
                errmsg = 'require: begin < end'
                logger.error(errmsg)
                return dumps({'error':errmsg},separators=(',',':'))
            else:
                logger.debug('from {} to {}'.format(begin,end))
                r = proxy.query_time_range(node,variable,begin,end,'ReceptionTime')
        else:
            if minutes is None:
                minutes = 24*60
            minutes = float(minutes)
            logger.debug('minutes={}'.format(minutes))
            #r = get_last_N_minutes(site,node,variable,minutes)
            r = proxy.get_last_N_minutes(node,variable,minutes)

        # deal with max_count
        #if 'error' not in r and max_count is not None:
        if max_count is not None:
            max_count = int(max_count)
            if max_count > 0:
                assert 2 == len(r.keys())   # a time column and a variable column
                time_col = list(set(r.keys()) - set([variable]))[0]
                tmp = zip(r[time_col],r[variable])
                tmp = proxy.condense(zip(r[time_col],r[variable]),max_count)
                tmp = zip(*tmp)
                r = {time_col:tmp[0],variable:tmp[1]}
        
        d['samples'] = r
        return dumps(d,separators=(',',':'))
    except:
        traceback.print_exc()
        return "it's beyond my paygrade"

@app.route('/data/2/<node>/<variables>.json')
def get_xy(node,variables):
    """Example:
https://grogdata.soest.hawaii.edu/data/2/node-047/Timestamp,d2w,t.json?begin=1500000000&end=1500082230&time_col=Timestamp
"""

    logger.debug((node,variables))

    variables = variables.split(',')    # require: no comma in variable name
    begin = request.args.get('begin')
    end = request.args.get('end')
    time_col = request.args.get('time_col')

    if begin is None or end is None or time_col is None:
        return 'begin, end, and time_col must be supplied'
    begin = float(begin)
    end = float(end)
    
    store = storage()
    if node not in store.get_list_of_tables():
        return 'No such node: {}'.format(escape(node))

    for var in variables:
        if var not in store.get_list_of_columns(node):
            return 'No such variable: {}'.format(escape(var))

    if time_col not in store.get_list_of_columns(node):
        return 'No such time column: {}'.format(escape(time_col))

    #return str((begin,end,time_col))

    try:
        proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
        r = proxy.query_time_range(node,variables,begin,end,time_col)
        return dumps([r[k] for k in variables],separators=(',',':'))
    except:
        traceback.print_exc()
        return "it's beyond my paygrade 2"

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/tech/')
def tech():
    return render_template('tech.html')

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
