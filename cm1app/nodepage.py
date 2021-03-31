import sys, time, json
from os.path import expanduser
sys.path.append(expanduser('~'))
from flask import Response, render_template, send_from_directory, request, escape
from cm1app import app
from node.config.c import get_list_of_disp_vars, get_node_attribute, get_variable_attribute
from cm1app.query_data import read_latest_sample
from cm1app.common import validate_id


@app.route('/<site>/nodepage/<node>/')
def route_site_node(site, node):
    """Page for individual node"""

    b,m = validate_id(node)
    if not b:
        return m

    return render_template('nodepage.html',
                           #site=escape(site),
                           site=get_node_attribute(node, 'site'),
                           node=escape(node))


@app.route('/<site>/dataportal/<node>/<variable>/')
def route_dataportal(site, node, variable):

    b,m = validate_id(node)
    if not b:
        return m
    
    end = request.args.get('end', default=time.time(), type=float)
    begin = request.args.get('begin', default=end - get_variable_attribute(node, variable, 'plot_range_second'), type=float)
        
    return render_template('varpage.html',
                           #site=escape(site),
                           site=get_node_attribute(node, 'site'),
                           node=escape(node),
                           variable=escape(variable),
                           begin=escape(begin),
                           end=escape(end))


@app.route('/<site>/nodepage/<node>.json')
def data_site_node(site, node):
    """Example:
    https://grogdata.soest.hawaii.edu/staging/nodepage/node-200.json
    """
    b,m = validate_id(node)
    if not b:
        return m

    site = get_node_attribute(node, 'site')
    
    S = {'name':get_node_attribute(node, 'name'),
         'location':get_node_attribute(node, 'location'),
         'note':get_node_attribute(node, 'note'),
         'tags':get_node_attribute(node, 'tags'),
         }

    tmp = get_node_attribute(node, 'latitude')
    if tmp is not None:
        S['latitude'] = tmp
    tmp = get_node_attribute(node, 'longitude')
    if tmp is not None:
        S['longitude'] = tmp
    
    R = {}
    variables = sorted(get_list_of_disp_vars(node),key=lambda x: x.lower())
    for k,var in enumerate(variables):
        d = read_latest_sample('ReceptionTime', node, var)
        if d is not None:
            r = {'var':var,
                 'ts':round(d[0], 1),
                 'val':round(d[1], 3),
                 'unit':get_variable_attribute(node, var, 'unit'),
                 'interval':get_variable_attribute(node, var, 'interval_second'),
                 'desc':get_variable_attribute(node, var, 'description'),
                 }
        else:
            r = {'var':var,
                 'ts':None,
                 'val':None,
                 'unit':None,
                 'interval':None,
                 'desc':None,
                 }
        lb = get_variable_attribute(node, var, 'lower_bound')
        ub = get_variable_attribute(node, var, 'upper_bound')
        r['range'] = [lb, ub]

        R[k] = r
    S['readings'] = R
    return Response(json.dumps(S, separators=(',', ':')),
                    mimetype='application/json; charset=utf-8')
