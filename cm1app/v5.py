# -*- coding: utf-8 -*-
# experimenting with HTTP Basic Auth instead of public key signing
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# All Rights Reserved. 2017
from cm1app import app
from functools import wraps
from flask import request,Response
from datetime import datetime
import logging,traceback,sys
from os.path import expanduser
sys.path.append(expanduser('~'))
from node.helper import dt2ts
from node.storage.storage2 import storage
#from node.parse_support import parse_message
from particle import fish_handler
from cred import cred


logging.basicConfig(level=logging.DEBUG)


# need to add "WSGIPassAuthorization On" to apache site .conf file

def check_auth(username,password):
    return username in cred and cred[username] == password
    #return username == 'uhcm' and password == 'password'

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
    try:
        msg = request.form['m']
        src = request.form['src']
        with open('/var/uhcm/incoming/api/5/tsraw.txt','a',0) as f:
            dt = datetime.utcnow()
            ts = dt2ts(dt)
            f.write('{},{},{},{}\n'.format(dt.isoformat(),ts,src,msg))
            return '{},ok'.format(dt.isoformat())
    except:
        logging.exception(traceback.format_exc())
        return ''

@app.route('/api/5/uhcm',methods=['POST'])
@requires_auth
def s5uhcmsubmit():
    try:
        msg = request.form['m']
        src = request.form['src']
        #store = storage()
        #d = parse_message(msg)
        #assert 'ReceptionTime' not in d
        #d['ReceptionTime'] = time.time()
        #store.insert(table,d)
        with open('/var/uhcm/incoming/api/5/uhcm_tmp.txt','a',0) as f:
            dt = datetime.utcnow()
            ts = dt2ts(dt)
            f.write('{},{},{},{}\n'.format(dt.isoformat(),ts,src,msg))
            return '{},ok'.format(dt.isoformat())
    except:
        logging.exception(traceback.format_exc())
        return ''

@app.route('/api/5/electron_us',methods=['POST'])
@requires_auth
def s5electronussubmit():
    try:
        tmp = fish_handler(request)
        if tmp is None:
            return ''
        table,d = tmp
        store = storage()
        for s in d:
            store.insert(table,{'ReceptionTime':s[0],'d2w':s[1]})
        #return str(d)
        return '{},ok'.format(datetime.utcnow().isoformat())
    except:
        logging.exception(traceback.format_exc())
        logging.exception(request)
        return ''
