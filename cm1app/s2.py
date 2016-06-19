# -*- coding: utf-8 -*-
# accept real-time data from base station(s) in the field
import sys,traceback
sys.path.append('/home/nuc/node')
from config.config_support import get_public_key
from flask import request
from datetime import datetime
from cm1app import app

import base64
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA

import json
from config.config_support import *
from storage.storage import storage
from parse_support import pretty_print
from helper import *
from os.path import exists


def PRINT(s):
    #pass
    print(s)

def api_parse1(m,key):
    #signature = base64.b64decode(request.form['s'])
    #key = RSA.importKey(key)
    #h = SHA512.new(m)
    #verifier = PKCS1_v1_5.new(key)
    #if verifier.verify(h,signature):
    if True:
        return {'dt':datetime.utcnow(),'m':m}
    else:
        PRINT('api_parse1(): bad signature')
        return None

@app.route('/<site>/api/s2/submit',methods=['POST'])
def s2submit(site):
    if 'poh' == site:
        client = request.args.get('client',None)
#        key = get_public_key(site,client)
        key = None

        dt = datetime.utcnow()
        
        try:
            m = request.form['m']
            m = api_parse1(m,key)
            if m is not None:
                print 'transmission time {}, reception time {}'.format(m['dt'],dt)
                d = json.loads(json.loads(m['m']))
                pretty_print(d)

                dbfile = r'/home/nuc/data/base-003/from_web_api/sensor_data.db'
                store = None
                if not exists(dbfile):
                    s = get_schema(site)
                    for k,v in s.iteritems():
                        v.insert(0,('ReceptionTime','TIMESTAMP'))
                    store = storage(dbfile=dbfile,schema=s)
                else:
                    store = storage(dbfile=dbfile)

                if store is not None:
                    d = {k: ts2dt(d[k]) if k in ['ReceptionTime','Timestamp'] else d[k] for k in d}
                    #for k in d:
                        #if k in ['ReceptionTime','Timestamp']:
                            #d[k] = ts2dt(d[k])
                    store.write(d['node'],d)

                return 'sample saved'
        except:
            traceback.print_exc()
            print 'the culprit:'
            print m
    return 'Fate saw the jewel in me, and pawed the heart apart to have it.'

