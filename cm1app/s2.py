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

def verify(m,key):
    signature = base64.b64decode(request.form['s'])
    key = RSA.importKey(key)
    h = SHA512.new(m)
    verifier = PKCS1_v1_5.new(key)
    return verifier.verify(h,signature)

@app.route('/<site>/api/s2/submit',methods=['POST'])
def s2submit(site):
    if 'poh' == site:
        client = request.args.get('client',None)
        key = get_public_key(site,client)

        dt = datetime.utcnow()
        
        try:
            m = request.form['m']
            if verify(m,key):
                #with open('/home/nuc/cm1app/comatose2.txt','a',0) as f:
                with open('/home/nuc/data/base-003/from_web_api/comatose2.txt','a',0) as f:
                    f.write('{},{}\n'.format(datetime.utcnow(),m))

                #d = json.loads(json.loads(m))     # WHAT???? rq5 only works with this
                d = json.loads(m)  # WHAT?? WHY? rq4 works with this?
                #pretty_print(d)

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
                    store.write(d['node'],d)
                    return 'sample saved'
                else:
                    print 's2::s2submit(): store is None, sth is wrong with storage::storage()'
        except:
            traceback.print_exc()
            print 's2::s2submit(): the culprit:'
            print m
    return 'Fate saw the jewel in me, and pawed the heart apart to have it.'

