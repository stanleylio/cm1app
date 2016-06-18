# -*- coding: utf-8 -*-
import traceback
import sys
sys.path.append('/home/nuc/node')
from flask import Flask,render_template,request
from cm1app import app
from json import dumps
from helper import *
from storage.storage import storage_read_only
from config.config_support import get_unit,get_description

from panels import *
from dashboard import *
from nodepage import *
from s1 import *


@app.route('/dev/')
def dev():
    return render_template('index.html')

# There is currently only one site so the landing page is the poh landing page.
#@app.route('/poh/systemstatus/')
@app.route('/')
def route_systemstatus():
    return render_template('systemstatus.html')

@app.route('/<site>/data/<node>/<variable>.json')
def site_node_variable(site,node,variable):
    """Examples: http://192.168.0.20:5000/poh/data/node-009/d2w.json?minutes=1
http://192.168.0.20:5000/coconut/data/node-021/S_CTD.json"""
    if site in ['poh','coconut']:
        print(' | '.join([site,node,variable]))

        minutes = request.args.get('minutes')
        if minutes is None:
            minutes = 24*60
        print('minutes={}'.format(minutes))

        variable = str(variable)    # storage.py doesn't like unicode variable names...

        unit = get_unit(site,node,variable)
        desc = get_description(site,node,variable)

        dbfile = get_dbfile(site,node)
        print dbfile
        
        d = query_data(dbfile,time_col,node,variable,minutes)
        d = {'unit':unit,
             'description':desc,
             'samples':d}
        return dumps(d,separators=(',',':'))
    return 'Eddie might go'

@app.route('/about/')
def about():
    return render_template('about.html')

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
