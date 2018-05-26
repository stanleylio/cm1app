from s1 import query_time_range, logging
import math, unittest
from xmlrpc.client import ServerProxy


logging.basicConfig(level=logging.INFO)


class Testcm1serv(unittest.TestCase):

    def test_query_time_range(self):
        # Test the functions directly
        # Query multiple params in one go, when "time_col" is within "begin" and "end"
        # This does not strip None or float('nan')
        # query_time_range() no longer perform POSIX timestamp to datetime.datetime
        # conversion. All time data in db should now be in POSIX timestamp.
        time_col = 'ReceptionTime'
        keys = [time_col, 'd2w']
        r = query_time_range('node-051', keys, 1506150000, 1506157362, time_col)
        logging.debug(r)
        self.assertTrue(len(keys) == len(r))    # all and only what we asked for
        self.assertTrue(all([len(r[k]) == len(r[time_col]) for k in r]))    # all values (lists) are of the same length
        self.assertTrue(len(r['ReceptionTime']) > 0)

    def test_proxy_get_list_of_tables(self):
        proxy = ServerProxy('http://127.0.0.1:8000/')
        tmp = proxy.get_list_of_tables()
        self.assertTrue(all([t in tmp for t in ['node-003', 'node-004', 'node-009', 'node-009', 'node-020']]))
        self.assertTrue(len(proxy.get_list_of_columns('node-020')) > 0)

    def test_proxy_query_time_range(self):
        proxy = ServerProxy('http://127.0.0.1:8000/')

        r = proxy.query_time_range('node-021', ['PH_EXT'], 1482820675, 1482825675, 'ReceptionTime')
        logging.debug(r)
        self.assertTrue('PH_EXT' in r)
        self.assertTrue(len(r['PH_EXT']) > 0)

        #https://grogdata.soest.hawaii.edu/poh/data/location/makaha1/depth.json?begin=1487412000&end=1491818400https://grogdata.soest.hawaii.edu/poh/data/location/makaha1/depth.json?begin=&end=
        r = proxy.query_time_range('node-009', 'd2w', 1487412000, 1491818400, 'ReceptionTime')
        logging.debug(r)
        self.assertTrue('d2w' in r)
        self.assertTrue(len(r['d2w']))
        self.assertTrue(all([not math.isnan(tmp) for tmp in r['d2w']]))
        self.assertTrue(all([tmp is not None for tmp in r['d2w']]))

    def test_get_last_N_minutes(self):
        proxy = ServerProxy('http://127.0.0.1:8000/')
        r = proxy.get_last_N_minutes('node-021', 'PH_EXT', 10)
        logging.debug(r)
        self.assertTrue('ReceptionTime' in r)
        self.assertTrue('PH_EXT' in r)
        self.assertTrue(len(r['ReceptionTime']) == len(r['PH_EXT']))

    def test_condense(self):
        proxy = ServerProxy('http://127.0.0.1:8000/')
        from random import randint
        for i in range(100):
            N = randint(1, 1000)
            lim = randint(1, N)
            a = list(range(N))
            assert len(proxy.condense(a, lim)) <= lim


if __name__ == '__main__':
    unittest.main()
