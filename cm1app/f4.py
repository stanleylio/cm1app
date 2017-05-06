# -*- coding: utf-8 -*-
# todo: reserve Flask for rendering and routing only. everything else via RPC ("microservice").
import traceback,sys,logging
from os.path import expanduser
sys.path.append(expanduser('~'))
from flask import Flask,render_template,request
from cm1app import app
from json import dumps
from datetime import datetime,timedelta
from node.helper import dt2ts
from node.config.config_support import get_unit,get_description,config_as_dict
from panels import *
from dashboard import *
from nodepage import *
#from s3 import *
import v4
import v5
import xmlrpclib,socket


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

sites = config_as_dict().keys()


@app.route('/')
def route_default():
    return render_template('index.html')

@app.route('/<site>/data/<node>/<variable>.json')
def site_node_variable(site,node,variable):
    """Examples: http://192.168.0.20:5000/poh/data/node-009/d2w.json?minutes=1
http://192.168.0.20:5000/coconut/data/node-021/S_CTD.json"""

    logger.debug((site,node,variable))
    #if site not in ['poh','coconut','makaipier','sf']:
    if site not in sites:
        logger.error('no such site: {}'.format(site))
        return 'No such site: {}'.format(site)
    
    begin = request.args.get('begin')
    end = request.args.get('end')
    minutes = request.args.get('minutes')
    max_count = request.args.get('max_count')

    variable = str(variable)    # storage.py doesn't like unicode variable names... TODO
    unit = get_unit(node,variable)
    desc = get_description(node,variable)
    bounds = get_range(node,variable)
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
            errmsg = 'require: begin < end'
            logger.error(errmsg)
            return dumps({'error':errmsg},separators=(',',':'))
        else:
            logger.debug('from {} to {}'.format(begin,end))
            #r = query_time_range(site,node,variable,begin,end)
            r = proxy.query_time_range(node,variable,begin,end)
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

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/tech/')
def tech():
    return render_template('tech.html')

@app.route('/dev/')
def dev():
    return render_template('dev.html')

@app.route('/haha/')
def haha():
    return render_template('haha.html')

@app.route('/project_info/')
def project_info():
    return render_template('project_info.html')

'''@app.route('/debug/')
def debug():
    #dbfile = '/home/nuc/data/base-003/storage/sensor_data.db'
    dbfile = '/home/nuc/node/www/poh/storage/sensor_data.db'
    time_col = 'ReceptionTime'
    store = storage_read_only(dbfile=dbfile)
    tables = store.get_list_of_tables()
    s = ''
    for table in tables:
        r = store.read_last_N(table,time_col)
        if r is not None:
            #s = s + '{}<br>{}<br>'.format(table,'<ul>{}</ul>'.format(''.join(['<li>{}, {}</li>'.format(c,r[c][0]) for c in store.get_list_of_columns(table)])))
            s = s + '{}<br>{}<br>'.format(table,'<ul>{}</ul>'.format(''.join(['<li>{}, {}</li>'.format(c,r[c][0]) for c in sorted(r.keys(),key=lambda x: x.lower())])))
        else:
            s = s + '{}<br>{}<br>'.format(table,'<ul>{}</ul>'.format(''.join(['<li>{}</li>'.format(c) for c in store.get_list_of_columns(table)])))
    return s'''
