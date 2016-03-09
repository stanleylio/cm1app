# -*- coding: utf-8 -*-
import traceback
import sys
sys.path.append('/home/nuc/node')
from flask import Flask,render_template
from cm1app import app
from json import dumps
from helper import *
from storage.storage import storage_read_only
from query_data import query_data,read_latest_group_average,read_baro_avg,read_water_depth


dbfile = '/home/nuc/node/www/poh/storage/sensor_data.db'    # TODO: centralize
time_col = 'ReceptionTime'

@app.route('/<site>/widgets/panels/')
def route_debug_panels(site):
    if 'poh' == site:
        # AJAX vs. server-side
        '''met_data = route_meteorological()
        m1 = route_makahaN('makaha1')
        m2 = route_makahaN('makaha2')
        tmb = route_makahaN('triplemakahab')
        return render_template('panels.html',
                               met_data=Markup(met_data),
                               makaha1_data=Markup(m1),
                               makaha2_data=Markup(m2),
                               triplemakahab_data=Markup(tmb))'''
        return render_template('panels.html')
    return 'cold war rhetoric'

# there is no simple and generic way to write this...
# how would the code know node-002 oxygen is bad but temperature is still good?
@app.route('/<site>/data/makaha/<name>.json')
def route_makahaN(site,name):
    if 'poh' == site:
        if name not in ['makaha1','makaha2','triplemakahab']:
            return '{}? nice try.'.format(name)

        m = {'makaha1':'node-004','makaha2':'node-003','triplemakahab':'node-001'} # map from makaha number to node ID
        try:
            node = m[name]
            d = {}

            # water depth
            d['wd'] = read_water_depth(dbfile,time_col,node)

            # optode stuff
            cols = ['O2Concentration','AirSaturation','Temperature']
            #units = [u'µM','%',u'℃℉']
            for col in cols:
                try:
                    d[col] = read_latest_group_average(dbfile,time_col,node,col)
                except:
                    traceback.print_exc()
        except KeyError:
            return 'step on a LEGO'

        # special case for makaha 2...
        # everything is a special case... just like chemistry.
        if 'makaha2' == name:
            d['Turbidity_FLNTU'] = read_latest_group_average(dbfile,time_col,'node-003','Turbidity_FLNTU')
            d['Chlorophyll_FLNTU'] = read_latest_group_average(dbfile,time_col,'node-003','Chlorophyll_FLNTU')

        return dumps(d,separators=(',',':'))
    return 'Nessun Dorma'

@app.route('/<site>/data/meteorological.json')
def data_meteorological(site):
    if 'poh' == site:
        air_t = read_latest_group_average(dbfile,time_col,'node-007','T_280')
        baro = read_baro_avg(dbfile,time_col)
        wind_avg = read_latest_group_average(dbfile,time_col,'node-007','Wind_average')
        rh = read_latest_group_average(dbfile,time_col,'node-007','RH_280')

        d = {'air_t':(round(air_t[0],1),round(air_t[1],1)),
             'baro_p':(round(baro[0],1),round(baro[1],1)),
             'wind_avg':(round(wind_avg[0],1),max(0,round(wind_avg[1],1))),     # for now
             'rh':(round(rh[0],1),round(rh[1],0))}
        return dumps(d,separators=(',',':'))
    return 'Hi, I\'d like to add you to my professional network on LinkedIn.'

