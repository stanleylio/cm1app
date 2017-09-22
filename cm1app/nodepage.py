# -*- coding: utf-8 -*-
import sys,traceback,time
from os.path import expanduser
sys.path.append(expanduser('~'))
from flask import Flask,render_template,Markup,send_from_directory,request,escape
from cm1app import app
from json import dumps
from node.config.config_support import get_list_of_disp_vars,get_attr,\
     get_unit,get_range,get_description,get_list_of_nodes,config_as_dict,get_interval
from query_data import read_latest_group_average


time_col = 'ReceptionTime'


sites = config_as_dict().keys()


@app.route('/<site>/nodepage/<node>/')
def route_site_node(site,node):
    """Page for individual node"""
    if site not in sites:
        return 'Error: Unknown site: {}'.format(escape(site))

    if node not in get_list_of_nodes(site):
        return 'Error: Unknown node: {}'.format(escape(node))
    
    return render_template('nodepage.html',
                           site=site,
                           node=node)

@app.route('/<site>/dataportal/<node>/<variable>/')
def route_dataportal(site,node,variable):
    if site not in sites:
        return 'Error: Unknown site: {}'.format(escape(site))
    
    end = request.args.get('end',default=time.time(),type=float)
    begin = request.args.get('begin',default=end - 7*24*3600,type=float)
        
    return render_template('varpage.html',
                           site=site,
                           node=node,
                           variable=variable,
                           begin=begin,
                           end=end)

@app.route('/<site>/nodepage/<node>.json')
def data_site_node(site,node):
    if site not in sites:
        return 'Error: Unknown site: {}'.format(escape(site))
    
    S = {'name':get_attr(node,'name'),
         'location':get_attr(node,'location'),
         'note':get_attr(node,'note'),
         }
    
    R = {}
    variables = sorted(get_list_of_disp_vars(node),key=lambda x: x.lower())
    for k,var in enumerate(variables):
        d = read_latest_group_average(site,time_col,node,var)
        if d is not None:
            r = {'var':var,
                 'ts':round(d[0],1),
                 'val':round(d[1],3),
                 'unit':get_unit(node,var),
                 'interval':get_interval(node,var),
                 'desc':get_description(node,var),
                 }
        else:
            r = {'var':var,
                 'ts':None,
                 'val':None,
                 'unit':None,
                 'interval':None,
                 'desc':None,
                 }
        b = get_range(node,var)
        if b is not None:
            r['range'] = [None if tmp in [float('-inf'),float('inf')] else tmp for tmp in b]

        R[k] = r
    S['readings'] = R
    return dumps(S,separators=(',',':'))

