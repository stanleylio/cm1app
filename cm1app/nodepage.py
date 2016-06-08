# -*- coding: utf-8 -*-
import traceback
import sys
sys.path.append('/home/nuc/node')
from flask import Flask,render_template,Markup,send_from_directory
from cm1app import app
from json import dumps
from helper import *
from storage.storage import storage_read_only
from config.config_support import get_list_of_disp_vars,get_name,get_unit_map,get_location,get_note,get_range
from query_data import read_latest_group_average

#{'poh':['base-003','base-001']}

#dbfile = '/home/nuc/data/base-003/storage/sensor_data.db'
#dbfile = '/home/nuc/node/www/poh/storage/sensor_data.db'
time_col = 'ReceptionTime'

@app.route('/<site>/nodepage/<node>/')
def route_poh_node(site,node):
    """Page for individual node"""
    if site in ['poh','coconut']:
        dbfile = get_dbfile(site)
        s = storage_read_only(dbfile=dbfile)
        if node.replace('-','_') in s.get_list_of_tables():
            return render_template('nodepage.html',
                                   site=site,
                                   node_id=node)
    return 'mildly defensive'

@app.route('/<site>/nodepage/<node>/<variable>/')
def route_poh_node_var(site,node,variable):
    """plotly page for a single variable"""
    if site in ['poh','coconut']:
        return render_template('varplotly.html',
                               site=site,
                               node_id=node,
                               variable=variable)
    return 'thought provoking'

# TODO
# pretty sure I can merge this with dashboard.py::data_dashboard()
# the difference: read_latest_non_null() vs. read_latest_group_average()
# the former find the latest non-null reading;
# the latter just get the last group mean, which could be None
@app.route('/<site>/nodepage/<node>.json')
def data_site_node(site,node):
    if site in ['poh','coconut']:
        dbfile = get_dbfile(site)
        S = [get_name(site,node),
             get_location(site,node),
             get_note(site,node),]
        #location = 'Paepae o He\'eia, Kane\'ohe'
        
        units = get_unit_map(site,node)
        R = []
        variables = sorted(get_list_of_disp_vars(site,node),key=lambda x: x.lower())
        for var in variables:
            d = read_latest_group_average(dbfile,time_col,node,var)
            r = [var,round(d[0],1),round(d[1],3),units[var]]
            
            b = get_range(site,node,var)
            if b is not None:
                r.append([None if tmp == float('inf') else tmp for tmp in b.to_tuple()])

            R.append(r)
        S.append(R)
        return dumps(S,separators=(',',':'))
    return 'creeping normality'
