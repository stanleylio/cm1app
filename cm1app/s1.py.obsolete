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


def PRINT(s):
    #pass
    print(s)

@app.route('/<site>/api/s1/submit',methods=['POST'])
def s1submit(site):
    if 'poh' == site:
        client = request.args.get('client',None)
        key = get_public_key(site,client)
        
        try:
            m = request.form['m']
            signature = base64.b64decode(request.form['s'])
            key = RSA.importKey(key)
            h = SHA512.new(m)
            verifier = PKCS1_v1_5.new(key)
            if verifier.verify(h,signature):
                with open('/home/nuc/cm1app/comatose.txt','a',0) as f:
                    f.write('{},{}\n'.format(datetime.utcnow(),m))
                return 'authentic'
            else:
                PRINT('s1submit(): bad signature')
        except KeyError:
            traceback.print_exc()
    return 'comatose'

