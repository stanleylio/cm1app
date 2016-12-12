# -*- coding: utf-8 -*-
import sys,traceback
sys.path.append('/home/nuc')
from flask import Flask,render_template,Markup,request
from cm1app import app
from json import dumps
#from node.helper import dt2ts
from node.storage.storage2 import storage_read_only as store2
from node.config.config_support import get_list_of_nodes,get_list_of_disp_vars,\
     get_name,get_unit,get_dbfile,\
     get_location,get_note,get_google_earth_link,get_range


time_col = 'ReceptionTime'

# ?
site_base_map = {'poh':'base-003',\
                 'makaipier':'base-002',\
                 'sf':'base-005'}


@app.route('/<site>/data/dashboard.json')
def data_dashboard(site):
    if site in site_base_map.keys():
        nodes = get_list_of_nodes(site)
        store = store2()
        
        S = {}
        for node in nodes:
            S[node] = {}
            S[node]['name'] = get_name(site,node)
            S[node]['location'] = get_location(site,node)
            S[node]['latest_non_null'] = {}
            #print node,S[node]['name']
            for var in get_list_of_disp_vars(site,node):
                tmp = store.read_latest_non_null(node,time_col,var)
                if tmp is not None:
                    r = [tmp[time_col],tmp[var],get_unit(site,node,var)]
                else:
                    r = [None,None,get_unit(site,node,var)]

                # put in the boundaries/limits/range of the variable, if defined
                b = get_range(site,node,var)
                if b is not None:
                    b = b.to_tuple()
                    b = [None if tmp == float('inf') else tmp for tmp in b]
                    #r.extend(b)
                    r.append(b)
                #print r
                
                S[node]['latest_non_null'][var] = r

        
        base = site_base_map[site]
        r = {'site':site,
             'data_src':base,
             'data_src_name':get_note(site,base),
             'location':get_location(site,base),
             'gmap_link':get_google_earth_link(site,base),
             'nodes':S}
        return dumps(r,separators=(',',':'))
    return 'Error: Unknown site: {}'.format(site)
