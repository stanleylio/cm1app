# -*- coding: utf-8 -*-
import sys,traceback,logging,xmlrpclib
from os.path import expanduser
sys.path.append(expanduser('~'))
from flask import Flask,render_template,request
from cm1app import app
from json import dumps
from node.helper import *
from query_data import read_latest_group_average,read_baro_avg,\
     read_water_depth_by_location,read_optode_by_location,read_ctd_by_location
from datetime import datetime,timedelta


time_col = 'ReceptionTime'  # TODO: get rid of this

makaha1_depth = []


def get_time_boundary(begin,end,minutes):
    if begin is not None:
        begin = float(begin)
        if end is None:
            end = dt2ts()
        else:
            end = float(end)
        if begin >= end:
            errmsg = 'require: begin < end'
            logging.error(errmsg)
            #return dumps({'error':errmsg},separators=(',',':'))
            begin,end = None,None
        else:
            logging.debug('from {} to {}'.format(begin,end))
    elif minutes is not None:
        minutes = float(minutes)
        end = dt2ts()
        begin = end - 60*minutes

    if end is None:
        end = dt2ts()
    if begin is None:
        begin = end - 60

    assert begin is not None
    assert end is not None
    assert begin <= end
    assert type(begin) == type(end)
    assert type(begin) is float
    return begin,end


@app.route('/<site>/data/location/<location>/<var>.json')
def route_processed_data(site,location,var):

    if 'poh' == site:
        if 'makaha1' == location:
            if var not in ['depth','oxygen','air','temperature','salinity']:
                return 'Unknown variable: {}'.format(var)
        elif location in ['makaha2','makaha3','river']:
            if var not in ['depth']:
                return 'Unknown variable: {}'.format(var)
        else:
            return 'Unknown location: {}'.format(location)
    elif 'makaipier' == site:
        if location not in ['dock1']:
            return 'Unknown location: {}'.format(location)
        if 'depth' != var:
            return 'Unknown variable: {}'.format(var)
    elif 'coconut' == site:
        if location not in ['noaa','bridge']:
            return 'Unknown location: {}'.format(location)
        if 'depth' != var:
            return 'Unknown variable: {}'.format(var)
    else:
        return 'Unknown site: {}'.format(site)

    begin,end = get_time_boundary(request.args.get('begin'),
                                  request.args.get('end'),
                                  request.args.get('minutes'))

# - - - - -
#<tide prediction hack>
    if 'makaha1' == location and 'depth' == var:
        global makaha1_depth
        if len(makaha1_depth) <= 0:
            for line in open('/var/www/uhcm/data/tideprediction.csv').readlines():
                line = line.strip().split(',')
                makaha1_depth.append([float(line[0]),float(line[1])])
        tmp = [p for p in makaha1_depth if p[0] >= begin and p[0] <= end]   # window in time
        if len(tmp):
            t,d = zip(*tmp)
        else:
            t,d = [],[]
        d = [tmp/1e3 for tmp in d]  # mm to m
    else:
#</tide prediction hack>
# - - - - -
        if 'depth' == var:
            t,d = read_water_depth_by_location(site,location,begin,end)
        elif var in ['oxygen','air','temperature']:
            t,d = read_optode_by_location(site,location,begin,end,var)
        elif var in ['salinity']:
            t,d = read_ctd_by_location(site,location,begin,end,var)

    max_count = request.args.get('max_count')
    if max_count is not None:
        max_count = int(max_count)
        if max_count > 0:
            proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')
            if len(t) <= 0:
                return dumps({time_col:[],var:[]},separators=(',',':'))
            tmp = proxy.condense(zip(t,d),max_count)
            t,d = zip(*tmp)

    r = {time_col:t,var:d}
    return dumps(r,separators=(',',':'))


@app.route('/<site>/data/meteorological.json')
def data_meteorological(site):
    if 'poh' != site:
        return 'No such site: {}'.format(site)
    
    air_t = read_latest_group_average(site,time_col,'node-007','T_280')
    baro = read_baro_avg(site,time_col)
    wind_avg = read_latest_group_average(site,time_col,'node-007','Wind_avg')
    rh = read_latest_group_average(site,time_col,'node-007','RH_280')

    d = {'air_t':(round(air_t[0],1),round(air_t[1],1)),
         'baro_p':(round(baro[0],1),round(baro[1],1)),
         'wind_avg':(round(wind_avg[0],1),max(0,round(wind_avg[1],1))),     # for now
         'rh':(round(rh[0],1),round(rh[1],0))}
    return dumps(d,separators=(',',':'))

