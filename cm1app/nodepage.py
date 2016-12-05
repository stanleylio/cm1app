# -*- coding: utf-8 -*-
import sys,traceback
from os.path import expanduser
sys.path.append(expanduser('~'))
from flask import Flask,render_template,Markup,send_from_directory
from cm1app import app
from json import dumps
from node.helper import *
from node.storage.storage import storage_read_only
from node.config.config_support import get_list_of_disp_vars,get_name,\
     get_unit_map,get_location,get_note,get_range,get_description,\
     get_list_of_nodes
from query_data import read_latest_group_average


# these hard-coded shortcuts ALWAYS come back and bite me.
# TODO
time_col = 'ReceptionTime'

@app.route('/<site>/nodepage/<node>/')
def route_poh_node(site,node):
    """Page for individual node"""
    if site in ['poh','coconut','makaipier','msb228']:
        #dbfile = get_dbfile(site,node)
        #s = storage_read_only(dbfile=dbfile)
        #if node.replace('-','_') in s.get_list_of_tables():
        if node in get_list_of_nodes(site):
            return render_template('nodepage.html',
                                   site=site,
                                   node=node)
    return 'The answer you didn\'t want, to the question you didn\'t ask'

'''@app.route('/<site>/nodepage/<node>/<variable>/')
def route_poh_node_var(site,node,variable):
    """plotly page for a single variable"""
    if site in ['poh','coconut']:
        return render_template('varplotly.html',
                               site=site,
                               node=node,
                               variable=variable)
    return 'thought provoking'
'''

@app.route('/<site>/dataportal/<node>/<variable>/')
def route_dataportal(site,node,variable):
    return render_template('dataportal.html',
                           site=site,
                           node=node,
                           variable=variable)

# TODO
# pretty sure I can merge this with dashboard.py::data_dashboard()
# the difference: read_latest_non_null() vs. read_latest_group_average()
# the former find the latest non-null reading;
# the latter just get the last group mean, which could be None
@app.route('/<site>/nodepage/<node>.json')
def data_site_node(site,node):
    if site in ['poh','coconut','makaipier','msb228']:
        S = {'name':get_name(site,node),
             'location':get_location(site,node),
             'note':get_note(site,node),
         }
        
        units = get_unit_map(site,node)
        R = {}
        variables = sorted(get_list_of_disp_vars(site,node),key=lambda x: x.lower())
        for k,var in enumerate(variables):
            d = read_latest_group_average(site,time_col,node,var)
            if d is not None:
                r = {'var':var,
                     'ts':round(d[0],1),
                     'val':round(d[1],3),
                     'unit':units[var],
                     'desc':get_description(site,node,var)}
            else:
                # no data for this variable in the db
                r = {'var':var,
                     'ts':None,
                     'val':None,
                     'unit':None,
                     'desc':None}
# Technical debt... you WILL have to pay it back sooner or later.
# There's no shortcut in this cold, harsh world.
            #r = [var,round(d[0],1),round(d[1],3),units[var]]
            
            b = get_range(site,node,var)
            if b is not None:
                r['range'] = [None if tmp == float('inf') else tmp for tmp in b.to_tuple()]

            R[k] = r
        S['readings'] = R
        return dumps(S,separators=(',',':'))
    return 'creeping normality'
