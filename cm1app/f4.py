# -*- coding: utf-8 -*-
import traceback,sys,logging
sys.path.append('/home/nuc/node')
from flask import Flask,render_template,request
from cm1app import app
from json import dumps
from datetime import datetime,timedelta
from helper import *
from storage.storage import storage_read_only
from config.config_support import get_unit,get_description
from query_data import query_data,query_time_range
from panels import *
from dashboard import *
from nodepage import *
#from s1 import *
#from s2 import *
from s3 import *
import v4


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# There is currently only one site so the landing page is the poh landing page.
#@app.route('/poh/systemstatus/')
@app.route('/')
def route_systemstatus():
    return render_template('systemstatus.html')

@app.route('/<site>/data/<node>/<variable>.json')
def site_node_variable(site,node,variable):
    """Examples: http://192.168.0.20:5000/poh/data/node-009/d2w.json?minutes=1
http://192.168.0.20:5000/coconut/data/node-021/S_CTD.json"""
    logger.debug((site,node,variable))
    if site not in ['poh','coconut']:
        logger.error('no such site: {}'.format(site))
        return 'Eddie might go'
    
    begin = request.args.get('begin')
    end = request.args.get('end')
    minutes = request.args.get('minutes')

    variable = str(variable)    # storage.py doesn't like unicode variable names... TODO
    unit = get_unit(site,node,variable)
    desc = get_description(site,node,variable)

    d = {'unit':unit,
         'description':desc,
         'samples':None}
    
    if begin is not None:
        begin = float(begin)
        if end is None:
            end = dt2ts(datetime.utcnow())     # assumption: database time too is in UTC
        else:
            end = float(end)
        if begin < end:
            logger.debug('from {} to {}'.format(begin,end))
            r = query_time_range(site,node,variable,begin,end)
        else:
            errmsg = 'begin must be < end: {},{}'.format(begin,end)
            logger.error(errmsg)
            return dumps({'error':errmsg},separators=(',',':'))
    else:
        if minutes is None:
            minutes = 24*60
        logger.debug('minutes={}'.format(minutes))
        r = query_data(site,node,variable,minutes)
        
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
    return render_template('index.html')

@app.route('/project_info/')
def dev2():
    return render_template('project_info.html')

@app.route('/debug/')
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
    return s
