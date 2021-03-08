import unittest, sys, requests


class TestAPI2(unittest.TestCase):

    def test_fetch(self):
        # experimental api
        url = 'https://grogdata.soest.hawaii.edu/data/2/node-020/ReceptionTime,t0,t1.json?time_col=ReceptionTime&begin=1506070000&end=1506079094'
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        #r = r.json()
        #print(len(r))
        #print(len(r[0]))
        #print(r)
