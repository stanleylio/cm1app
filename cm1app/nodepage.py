# -*- coding: utf-8 -*-
import sys, traceback, time
from os.path import expanduser
sys.path.append(expanduser('~'))
from flask import render_template, send_from_directory, request, escape
from cm1app import app
from json import dumps
from node.config.config_support import get_list_of_disp_vars,\
     get_unit, get_range, get_description, get_interval, get_plot_range, get_config, get_site
from cm1app.query_data import read_latest_group_average
from cm1app.common import time_col, validate_id


@app.route('/<site>/nodepage/<node>/')
def route_site_node(site, node):
    """Page for individual node"""

    b,m = validate_id(node)
    if not b:
        return m

    return render_template('nodepage.html',
                           #site=escape(site),
                           site=get_site(node),
                           node=escape(node))

@app.route('/<site>/dataportal/<node>/<variable>/')
def route_dataportal(site, node, variable):

    b,m = validate_id(node)
    if not b:
        return m
    
    end = request.args.get('end', default=time.time(), type=float)
    begin = request.args.get('begin', default=end - get_plot_range(node, variable)*3600, type=float)
        
    return render_template('varpage.html',
                           #site=escape(site),
                           site=get_site(node),
                           node=escape(node),
                           variable=escape(variable),
                           begin=escape(begin),
                           end=escape(end))

@app.route('/<site>/nodepage/<node>.json')
def data_site_node(site, node):
    """Example: https://grogdata.soest.hawaii.edu/staging/nodepage/node-200.json"""
    b,m = validate_id(node)
    if not b:
        return m

    site = get_site(node)
    
    S = {'name':get_config('name', node),
         'location':get_config('location', node),
         'note':get_config('note', node),
         'tags':get_config('tags', node, default=[]),
         }

    tmp = get_config('latitude', node, default=None)
    if tmp is not None:
        S['latitude'] = tmp
    tmp = get_config('longitude', node, default=None)
    if tmp is not None:
        S['longitude'] = tmp
    
    R = {}
    variables = sorted(get_list_of_disp_vars(node),key=lambda x: x.lower())
    for k,var in enumerate(variables):
        d = read_latest_group_average(site, time_col, node, var)
        if d is not None:
            r = {'var':var,
                 'ts':round(d[0], 1),
                 'val':round(d[1], 3),
                 'unit':get_unit(node, var),
                 'interval':get_interval(node, var),
                 'desc':get_description(node, var),
                 }
        else:
            r = {'var':var,
                 'ts':None,
                 'val':None,
                 'unit':None,
                 'interval':None,
                 'desc':None,
                 }
        b = get_range(node, var)
        if b is not None:
            r['range'] = [None if tmp in [float('-inf'),float('inf')] else tmp for tmp in b]

        R[k] = r
    S['readings'] = R
    return dumps(S, separators=(',', ':'))
