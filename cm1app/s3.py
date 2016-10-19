# -*- coding: utf-8 -*-
# accept real-time data from base station(s) in the field
import sys,traceback,logging,time
sys.path.append('/home/nuc/node')
from config.config_support import get_public_key
from flask import request
from datetime import datetime
from cm1app import app
from os.path import exists
#from s2 import verify
from authstuff import validate_message


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logging.Formatter.converter = time.gmtime
formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


cmap = {'poh':r'/home/nuc/data/base-004/from_web_api/raw1.txt'}

@app.route('/<site>/api/s3/submit',methods=['POST'])
def s3submit(site):
    if 'poh' == site:
        client = request.args.get('client',None)
        key = get_public_key(site,client)

        try:
            m = request.form['m']
            sig = request.form['s']
            #if verify(m,key):
            if validate_message(m,sig,key):
                with open(cmap[site],'a',0) as f:
                    f.write('{},{}\t{}\n'.format(datetime.utcnow(),site,m))
                return '{"r":"saved"}'
        except:
            logging.error(traceback.format_exc())
            logging.error('s3::s3submit(): the culprit: {}'.format(m))
    return '{"r":"error"}'
