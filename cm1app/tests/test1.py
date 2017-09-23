import requests,random,math,unittest,logging


logging.basicConfig(level=logging.INFO)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)


host = 'https://grogdata.soest.hawaii.edu'


def test1(ep):
    """Check that the endpoint is available, and there's no None or NaN in the response."""
    logging.debug('Testing {}'.format(ep))
    result = True

    r = requests.get(ep)
    result &= r.status_code == 200
    r = r.json()
    result &= 'samples' in r
    #print(len(r['samples']['d2w']))
    for k in r['samples']:
        result &= all([tmp is not None for tmp in r['samples'][k]])
        result &= all([not math.isnan(tmp) for tmp in r['samples'][k]])
    return result


class TestAPI(unittest.TestCase):

    def testGauges(self):
        # tide gauges
        nodes = ['node-008','node-009','node-014','node-040','node-047','node-048','node-049','node-075']

        for node in nodes:
            end = random.randint(1497130276,1500154178)
            begin = end - 6*3600
            # no longer checks if node is in site. site has to be a known site though.
            ep = '/poh/data/{node}/d2w.json?begin={begin}&end={end}'.\
                 format(node=node,
                        begin=begin,
                        end=end)
            ep = host + ep

            result = test1(ep)
            if not result:
                logging.warning('FAILED: ' + ep)
                self.assertTrue(False)

    def testdataapiformat(self):
        # make sure there's a time_col even though it's not specified in the link
        url = host + '/poh/data/node-003/Chlorophyll_FLNTUS.json?begin=1505513530.79&end=1506118330.79'
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        r = r.json()
        self.assertTrue(all([p in r.keys() for p in [u'unit', u'description', u'samples', u'bounds']]))
        self.assertTrue('ReceptionTime' in r['samples'].keys())
        self.assertTrue('Chlorophyll_FLNTUS' in r['samples'].keys())
        self.assertTrue(len(r['samples']['Chlorophyll_FLNTUS']) > 0)

    def testmisc(self):
        eps = [
            '/poh/nodepage/node-004.json',
            '/poh/nodepage/node-021.json',
            '/poh/data/node-004/O2Concentration.json?minutes=46080',
            '/poh/data/node-021/PH_EXT.json?begin=1480800106&end=1480808106&max_count=5',
            '/makaipier/data/node-010/d2w.json?begin=1480800106&end=1480808106',
            '/poh/data/node-022/PH_EXT.json?begin=1480800106&end=1480808106&max_count=5',
            '/static/uhcm/img/poh/node-004/AirSaturation.json',

            '/poh/data/dashboard.json',
            '/poh/data/meteorological.json',
            #'/poh/data/makaha/makaha1.json',
            #'/poh/data/makaha/makaha2.json',
            #'/poh/data/makaha/triplemakahab.json',

            '/poh/data/location/makaha1/depth.json?minutes=10080&max_count=1000',
            '/poh/data/location/makaha1/depth.json',
            '/poh/data/location/makaha1/depth.json?begin=1485980000&end=1485986255',
            '/poh/data/location/makaha1/depth.json?minutes=60',
            '/poh/data/location/makaha1/depth.json?begin=1478030000&end=1478037569&max_count=1000',
            '/poh/data/location/makaha1/oxygen.json?begin=1485980000&end=1485986255',
            '/poh/data/location/makaha1/air.json?begin=1485980000&end=1485986255',
            '/poh/data/location/makaha1/temperature.json?begin=1485980000&end=1485986255',

            '/poh/data/location/makaha2/depth.json',
            '/poh/data/location/makaha2/depth.json?begin=1485980000&end=1485986255',
            '/poh/data/location/makaha2/depth.json?minutes=60',
            '/poh/data/location/makaha2/depth.json?begin=1478030000&end=1478037569&max_count=1000',

            '/makaipier/data/location/dock1/depth.json',
            '/makaipier/data/location/dock1/depth.json?begin=1485980000&end=1485986255',
            '/makaipier/data/location/dock1/depth.json?minutes=60',
            '/makaipier/data/location/dock1/depth.json?begin=1478400000&end=1485900000&max_count=1000',
            ]

        for ep in eps:
            ep = host + ep
            logging.debug('Testing {}'.format(ep))
            code = requests.get(ep).status_code
            if code != 200:
                logging.warning(ep)
                self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()

