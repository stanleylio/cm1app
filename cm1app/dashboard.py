# -*- coding: utf-8 -*-
import traceback
import sys
sys.path.append('/home/nuc/node')
from flask import Flask,render_template,Markup,request
from cm1app import app
from json import dumps
from helper import *
from storage.storage import storage_read_only
from config.config_support import get_list_of_nodes,get_list_of_disp_vars,get_name,get_unit_map,get_location,get_range


#dbfile = '/home/nuc/data/base-003/storage/sensor_data.db'
#dbfile = '/home/nuc/node/www/poh/storage/sensor_data.db'
time_col = 'ReceptionTime'

# dashboard... the overview dashboard or the per-site dashboard? TODO
# passing site=coconut argument into render_template -> html -> javascript is gonna be very messy...
'''@app.route('/<site>/widgets/dashboard/')
def route_dashboard(site):
    if 'poh' == site:
        return render_template('dashboard.html')
    return 'liberal SJW'
'''

# TODO
# pretty sure I can merge this with nodepage.py::data_site_node()
# the difference: read_latest_non_null() vs. read_latest_group_average()
# the former find the latest non-null reading;
# the latter just get the last group mean, which could be None/Null
@app.route('/<site>/data/dashboard.json')
def data_dashboard(site):
    if site in ['poh','coconut']:
        dbfile = get_dbfile(site)
        s = storage_read_only(dbfile=dbfile)
        nodes = get_list_of_nodes(site)
        S = {}
        for node in nodes:
            units = get_unit_map(site,node)
            S[node] = {}
            S[node]['name'] = get_name(site,node)
            S[node]['location'] = get_location(site,node)
            S[node]['latest_non_null'] = {}     # these should be optional. dashboard should still show without red/green status TODO
            #print node,S[node]['name']
            for var in get_list_of_disp_vars(site,node):
                tmp = s.read_latest_non_null(node,time_col,var)
                if tmp is not None:
                    r = [dt2ts(tmp[time_col]),tmp[var],units[var]]
                else:
                    r = [None,None,units[var]]

                # put in the boundaries/limits/range of the variable, if defined
                b = get_range(site,node,var)
                if b is not None:
                    b = b.to_tuple()
                    b = [None if tmp == float('inf') else tmp for tmp in b]
                    #r.extend(b)
                    r.append(b)
                #print r
                
                S[node]['latest_non_null'][var] = r

        # TODO: clean this up, use the config files
        if 'poh' == site:
            r = {'site':site,
                 'data_src':'base-003',
                 'data_src_name':'Base Station #3 (Celeron-NUC)',
                 'location':'Paepae o He\'eia, Kane\'ohe',
                 'gmap_link':'https://goo.gl/maps/ECEBgo3UEp82',
                 'nodes':S}
        elif 'coconut' == site:
            r = {'site':site,
                 'data_src':'base-002',
                 'data_src_name':'Base Station #2 (BBB-based)',
                 'location':'In a water tank somewhere on Coconut Island',
                 'gmap_link':'https://goo.gl/maps/2YYpJ6Ru6692',
                 'nodes':S}

        return dumps(r,separators=(',',':'))
    return 'Hi, I\'d like to add you to my professional network on LinkedIn.'

