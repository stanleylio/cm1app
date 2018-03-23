# -*- coding: utf-8 -*-
#
# Stuff that requires Auth. Mostly POST.
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# All Rights Reserved. 2017
from cm1app import app
from functools import wraps
from flask import request, Response
from datetime import datetime
import logging, traceback, sys, time, json
from node.helper import dt2ts
from node.z import send
from cm1app.particle import fish_handler
from cm1app.publish import to_uhcm_xchg
from cred import cred


logging.basicConfig(level=logging.DEBUG)


# need to add "WSGIPassAuthorization On" to apache site .conf file to make this work

def check_auth(username,password):
    return username in cred and cred[username] == password

def authenticate():
    return Response(
        'bad credential',
        401,
        {'WWW-Authenticate':'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username,auth.password):
            return authenticate()
        return f(*args,**kwargs)
    return decorated


@app.route('/api/5/raw',methods=['POST'])
@requires_auth
def s5rawsubmit():
    """Store POSTed messages to a text file."""
    try:
        msg = request.form['m']
        src = request.form['src']
        with open('/var/uhcm/incoming/api/5/tsraw.txt', 'a', 1) as f:
            dt = datetime.utcnow()
            ts = dt2ts(dt)
            f.write('{},{},{},{}\n'.format(dt.isoformat(),ts,src,msg))
            return '{},ok'.format(dt.isoformat())
    except:
        logging.exception(traceback.format_exc())
        return 'Error'


@app.route('/api/5/electron_us',methods=['POST'])
@requires_auth
def s5electronussubmit():
    """Accept data from Particle Electrons (via webhooks).
Parse and reformat data into the send() form and redirect them into RabbitMQ.
Also maintains a plain-text copy of all messages."""
    try:
        # debug log
        with open('/var/www/uhcm/electron.txt','a') as f:
            f.write('{},{},{},{},{}\n'.format(datetime.utcnow(),
                                           time.time(),
                                           request.form['coreid'],
                                           request.form['event'],
                                           request.form['data']))

        # processing
        if u'test-event' == request.form['event']:
            return 'a test event. ignore.'

        #if request.form['event'] in [u'd2w',u'debug']:
        table,D = fish_handler(request)
        if table is None:
            return D

        for sample in D:
            to_uhcm_xchg(send(None,sample,src=table),table + '.samples')

        return '{},ok'.format(datetime.utcnow().isoformat())
    except:
        logging.exception(traceback.format_exc())
        logging.exception(request)
        return 'Error'
