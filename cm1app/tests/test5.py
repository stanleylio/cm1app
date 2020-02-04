import unittest, sys, requests, time, json, random
from datetime import datetime
from os.path import expanduser
sys.path.append('..')
sys.path.append(expanduser('~'))
from particle import coreid2nodeid
from cred import cred


url = 'https://grogdata.soest.hawaii.edu/api/5/electron_us'
coreid = u'000000000000000000000099'
name = 'uhcm'
passwd = cred['uhcm']


class TestPEd2w(unittest.TestCase):

    #def test_PEConfig(self):
        # what's this for?
    #    self.assertTrue('node-046' == coreid2nodeid('360064001951343334363036'))

    def test_submit_api(self):
        """Submit some "data" from virtual Particle Electron gauge node-099, then read it back from the db."""
        
        now = round(time.time())
        end = now
        begin = now - 10*60
        # ... that means it can't be run more frequently than once every 10 minutes or else the groups would overlap

        # data channel (d2w)
        fakedata = []
        for i in range(10):
            fakedata.append([begin + (i+1)*60,
                             round(5000*random.random(), 1),
                             round(100*random.random()),
                             int(60*random.random())],
                            )
        data = json.dumps(fakedata, separators=(',',':'))
        event = u'd2w'
        r = requests.post(url, data={'event': event,
                                    'data': data,
                                    'published_at': datetime.utcnow().isoformat() + 'Z',
                                    'coreid': coreid,
                                    },
                          auth=(name, passwd))
        self.assertTrue(200 == r.status_code)

        # now read it back
        # query recent data, and check that the response contains what we just sent (though checking just the timestamps)
        def get(node, var, time_col, begin, end):
            url = 'https://grogdata.soest.hawaii.edu/data/2/{node}/{time_col},{var}.json?time_col={time_col}&begin={begin}&end={end}'
            url = url.format(node=node, time_col=time_col, var=var, begin=begin, end=end)
            #print(url)
            return requests.get(url).json()

        # give time to make sure the data have made it into the db
        time.sleep(2)
        dbdata = get('node-099', 'd2w', 'ts', begin, end)

        #print('Response non-empty?')
        self.assertTrue(len(dbdata) > 0)
        self.assertTrue(len(fakedata) > 0)
        #print('Data in db?')
        #print(fakedata)
        #print(dbdata)
        # the timestamps in the generated data should be contained in the response
        self.assertTrue(set([x[0] for x in fakedata]).issubset(set([x[0] for x in dbdata])))


    def test_debug_channel(self):
        data = {'ts': time.time(),
                'Vb': round(4*random.random(), 3),
                'SoC': round(100*random.random(), 2)}
        data = json.dumps(data, separators=(',', ':'))
        event = u'debug'
        
        r = requests.post(url, data={'event': event,
                                    'data': data,
                                    'published_at': datetime.utcnow().isoformat() + 'Z',
                                    'coreid': coreid,
                                    },
                          auth=(name, passwd))
        self.assertTrue(200 == r.status_code)
        

if __name__ == '__main__':
    unittest.main()
