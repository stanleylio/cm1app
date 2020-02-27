import unittest, sys, requests, time, json, random
from datetime import datetime
from os.path import expanduser
sys.path.append('..')
sys.path.append(expanduser('~'))
from particle import coreid2nodeid
from cred import cred


# fill in the secrets yourself.
url = 'https://grogdata.soest.hawaii.edu/api/5/electron_us'
coreid = u'000000000000000000000099'
name = '_test_user_3MH44S1v4stUT1qR8Bvy'
passwd = '0MbXIuAmEdngkzwUM9Qr'

class Test_v5_auth(unittest.TestCase):

    def test_debug_channel(self):
        data = {'ts':time.time(),
                'Vb':round(4*random.random(), 3),
                'SoC':round(100*random.random(), 2),
                'B':0,
                'ST':1,
                'M':1,
                }
        data = json.dumps(data, separators=(',', ':'))
        event = u'debug'
        
        r = requests.post(url, data={'event':event,
                                    'data':data,
                                    'published_at':datetime.utcnow().isoformat() + 'Z',
                                    'coreid':coreid,
                                    },
                          auth=(name, passwd))
        self.assertTrue(200 == r.status_code)
        

if __name__ == '__main__':
    unittest.main()
