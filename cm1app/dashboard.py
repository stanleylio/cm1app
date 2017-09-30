# -*- coding: utf-8 -*-
import sys,traceback
sys.path.append('/home/nuc')
from flask import Flask,render_template,Markup,request
from cm1app import app
from json import dumps
from node.storage.storage2 import storage,auto_time_col
from node.config.config_support import get_list_of_devices,get_list_of_disp_vars,\
     get_attr,get_unit,get_range,get_interval


# ... just get rid of this already. so is that blob of public keys.
site_base_map = {'poh':'base-003',
                 'makaipier':'base-002',
                 'sf':'base-000',
                 'coconut':'base-010',
                 'uhm':'base-005',
                 }


@app.route('/<site>/data/dashboard.json')
def data_dashboard(site):
    if site not in site_base_map.keys():
        return 'Error: Unknown site: {}'.format(site)
    
    nodes = get_list_of_devices(site)
    store = storage()
    
    S = {}
    # "only for nodes defined in the site config AND have entries in db"
    # this way I can add/test config file without a db entry while web is running
    for node in set(nodes).intersection(set([tmp.replace('_','-') for tmp in store.get_list_of_tables()])):
        S[node] = {}
        S[node]['name'] = get_attr(node,'name')
        S[node]['location'] = get_attr(node,'location')
        S[node]['latest_non_null'] = {}
        #print(node,S[node]['name'])

        dbcols = store.get_list_of_columns(node)
        time_col = auto_time_col(dbcols)
        for var in set(dbcols).intersection(set(get_list_of_disp_vars(node))):
            # [timestamp,reading,unit,[lower bound,upper bound]]

            tmp = store.read_latest_non_null(node,time_col,var)
            if tmp is not None:
                r = [tmp[time_col],tmp[var]]
            else:
                r = [None,None]

            # add unit
            r.append(get_unit(node,var))

            # put in the boundaries/limits/range of the variable
            # use [None,None] if the limits of a variable are not defined.
            b = get_range(node,var)
            b = [None if tmp in [float('-inf'),float('inf')] else tmp for tmp in b]
            r.append(b)

            r.append(get_interval(node,var))

            S[node]['latest_non_null'][var] = r

    # site info (data source, location etc.)
    #base = site_base_map[site]
    r = {'site':site,
         #'data_src':base,
         #'data_src_name':get_attr(base,'note'),
         #'location':get_attr(base,'location'),
         #'gmap_link':get_attr(base,'google_earth_link'),
         'nodes':S}
    
    return dumps(r,separators=(',',':'))
