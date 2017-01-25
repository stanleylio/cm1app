# -*- coding: utf-8 -*-
# TODO: GET RID OF THIS FILE: normalize the data interface and push this to client side.
import sys,traceback,logging
from os.path import expanduser
sys.path.append(expanduser('~'))
from flask import Flask,render_template,request
from cm1app import app
from json import dumps
from node.helper import *
from query_data import read_latest_group_average,read_baro_avg,read_water_depth_by_location
import xmlrpclib


time_col = 'ReceptionTime'  # TODO: get rid of this


@app.route('/<site>/widgets/panels/')
def route_debug_panels(site):
    if 'poh' != site:
        return 'No such site: {}'.format(site)
    
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


@app.route('/<site>/data/location/<location>/<var>.json')
def route_makaha_processed_data(site,location,var):
    if site not in ['poh']:
        return 'Unknown site: {}'.format(site)
    if location not in ['makaha1','makaha2']:
        return 'Unknown location: {}'.format(location)
    if 'depth' != var:
        return 'Unknown variable: {}'.format(var)

    var = 'd2w'
    proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')

    minutes = request.args.get('minutes')
    if minutes is None:
        minutes = 1
    minutes = float(minutes)
    max_count = request.args.get('max_count')

    r = read_water_depth_by_location(location,minutes)

    if max_count is not None:
        max_count = int(max_count)
        if max_count > 0:
            assert 2 == len(r.keys())   # a time column and a variable column
            time_col = list(set(r.keys()) - set([var]))[0]
            tmp = zip(r[time_col],r[var])
            tmp = proxy.condense(zip(r[time_col],r[var]),max_count)
            tmp = zip(*tmp)
            r = {time_col:tmp[0],var:tmp[1]}

    r['depth_meter'] = r[var]
    del r[var]

    return dumps(r,separators=(',',':'))


# there is no simple and generic way to write this...
# how would the code know node-002 oxygen is bad but temperature is still good?
@app.route('/<site>/data/location/<name>.json')
def route_makahaN(site,name):
    if 'poh' != site:
        return 'No such site: {}'.format(site)
    if name not in ['makaha1','makaha2','triplemakahab']:
        return 'Unknown location: {}'.format(name)

    #m = {'makaha1':'node-004','makaha2':'node-003','triplemakahab':'node-001'} # map from makaha number to node ID
    m = {'makaha1':'node-004','triplemakahab':'node-001'} # map from makaha number to node ID
    try:
        node = m[name]
        d = {}
        #dbfile = get_dbfile(site)

        # water depth
        d['wd'] = read_water_depth(site,time_col,node)
        if d['wd'][1] < 0:
            d['wd'] = d['wd'][0],None

        # optode stuff
        cols = ['O2Concentration','AirSaturation','Temperature']
        #units = [u'µM','%',u'℃℉']
        for col in cols:
            try:
                d[col] = read_latest_group_average(site,time_col,node,col)
            except:
                traceback.print_exc()
    except KeyError:
        return 'Makaha data not available.'

    # special case for makaha 2...
    # everything is a special case... just like chemistry.
    if 'makaha2' == name:
        d['Turbidity_FLNTU'] = read_latest_group_average(site,time_col,'node-003','Turbidity_FLNTU')
        d['Chlorophyll_FLNTU'] = read_latest_group_average(site,time_col,'node-003','Chlorophyll_FLNTU')

    return dumps(d,separators=(',',':'))

@app.route('/<site>/data/meteorological.json')
def data_meteorological(site):
    if 'poh' != site:
        return 'No such site: {}'.format(site)
    
    air_t = read_latest_group_average(site,time_col,'node-007','T_280')
    baro = read_baro_avg(site,time_col)
    wind_avg = read_latest_group_average(site,time_col,'node-007','Wind_average')
    rh = read_latest_group_average(site,time_col,'node-007','RH_280')

    d = {'air_t':(round(air_t[0],1),round(air_t[1],1)),
         'baro_p':(round(baro[0],1),round(baro[1],1)),
         'wind_avg':(round(wind_avg[0],1),max(0,round(wind_avg[1],1))),     # for now
         'rh':(round(rh[0],1),round(rh[1],0))}
    return dumps(d,separators=(',',':'))

