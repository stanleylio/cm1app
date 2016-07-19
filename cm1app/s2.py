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


cmap = {'poh':r'/home/nuc/data/base-003/from_web_api/comatose2.txt'}
dbmap = {'poh':r'/home/nuc/data/base-003/from_web_api/sensor_data.db'}

@app.route('/<site>/api/s2/submit',methods=['POST'])
def s2submit(site):
    if 'poh' == site:
        client = request.args.get('client',None)
        key = get_public_key(site,client)

        dt = datetime.utcnow()
        
        try:
            m = request.form['m']
            if verify(m,key):
            #if True:
                # Data coming in are already parsed and clean (known nodes, proper name tags
                # for variables etc.). Don't go "parse_message()" on them.
                with open(cmap[site],'a',0) as f:
                    f.write('{},{}\n'.format(datetime.utcnow(),m))

                #d = json.loads(json.loads(m))   # WHAT?? rq5 only works with this
                d = json.loads(m)               # but rq4 works with this?
                #pretty_print(d)    # don't print - anything printed would be considered
                # error message by Apache

                dbfile = dbmap[site]
                store = None
                if not exists(dbfile):
                    s = get_schema(site)
                    for k,v in s.iteritems():
                        v.insert(0,('ReceptionTime','TIMESTAMP'))
                    store = storage(dbfile=dbfile,schema=s)
                else:
                    store = storage(dbfile=dbfile)

                if store is not None:
                    # what the hack?
                    d = {k: ts2dt(d[k]) if k in ['ReceptionTime','Timestamp','dt_seabird'] else d[k] for k in d}
                    # what a hack?? now I need to remember to add any field that is supposed
                    # to be datetime.datetime here.
                    store.write(d['node'],d)
                    return 'sample saved'
                else:
                    print 'sth is wrong with storage::storage()'
        except:
            traceback.print_exc()
            print 's2::s2submit(): the culprit:'
            print m
    return 'Fate saw the jewel in me, and pawed the heart apart to have it.'

