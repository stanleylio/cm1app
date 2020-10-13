import requests, random, math, unittest, logging, json
from datetime import timedelta


logging.basicConfig(level=logging.INFO)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)


host = 'https://grogdata.soest.hawaii.edu'
#host = 'http://192.168.0.30'


def test1(ep):
    """Check that the endpoint is available, and there's no None, NaN, or inf/-inf in the response."""
    logging.debug('Testing {}'.format(ep))
    result = True

    r = requests.get(ep)
    result &= r.status_code == 200
    r = r.json()
    x,y = zip(*r)

    def p(v):
        return v is not None and not math.isnan(v) and v not in [float('-inf'),float('inf')]

    result &= all([p(tmp) for tmp in x])
    result &= all([p(tmp) for tmp in y])
    return result


class TestAPI(unittest.TestCase):

    def testGauges(self):
        # tide gauges
        nodes = ['node-008',
                 'node-009',
                 'node-014',
                 'node-046',
                 'node-048',
                 'node-049',
                 'node-051',
                 'node-070',
                 'node-092',
                 'node-097',]

        for node in nodes:
            end = random.randint(1497130276, 1501054178)
            begin = end - timedelta(days=7).total_seconds()
            # no longer checks if node is in site.
            ep = '/data/2/{node}/ReceptionTime,d2w.json?begin={begin}&end={end}&time_col=ReceptionTime'.\
                 format(node=node,
                        begin=begin,
                        end=end)
            ep = host + ep
            try:
                result = test1(ep)
            except:
                print(ep)
                result = False
                
            if not result:
                logging.warning('FAILED: ' + ep)
                self.assertTrue(False)

    def testdataapiformat(self):
        # make sure there's a time_col even though it's not specified in the link
        url = host + '/data/2/node-009/ReceptionTime,d2w.json?begin=1505513530.79&end=1506118330.79&time_col=ReceptionTime'
        r = requests.get(url)
        self.assertTrue(r.status_code == 200)
        r = r.json()
        self.assertTrue(len(r) > 0)

    def test_no_inf(self):
        ep = '/data/2/base-005/ReceptionTime,uptime_second.json?begin=1506802303.13&end=1509394303.13&time_col=ReceptionTime'
        ep = host + ep
        logging.debug('Testing {}'.format(ep))
        self.assertTrue(test1(ep))
        r = requests.get(ep).json()
        x,y = zip(*r)
        self.assertTrue(float('inf') not in x)
        self.assertTrue(float('-inf') not in x)
        self.assertTrue(float('nan') not in x)
        self.assertTrue(float('inf') not in y)
        self.assertTrue(float('-inf') not in y)
        self.assertTrue(float('nan') not in y)

    def testmisc(self):
        eps = [
            '/poh/nodepage/node-004.json',
            '/poh/nodepage/node-021.json',
            #'/poh/data/node-021/PH_EXT.json?begin=1480800106&end=1480808106&max_count=5',
            #'/makaipier/data/node-010/d2w.json?begin=1480800106&end=1480808106',
            #'/poh/data/node-022/PH_EXT.json?begin=1480800106&end=1480808106&max_count=5',
            '/static/uhcm/img/poh/node-004/AirSaturation.json',

            '/poh/data/dashboard.json',
            #'/poh/data/meteorological.json',
            #'/poh/data/makaha/makaha1.json',
            #'/poh/data/makaha/makaha2.json',
            #'/poh/data/makaha/triplemakahab.json',

            #'/poh/data/location/makaha1/depth.json?minutes=10080&max_count=1000',
            #'/poh/data/location/makaha1/depth.json',
            #'/poh/data/location/makaha1/depth.json?begin=1485980000&end=1485986255',
            #'/poh/data/location/makaha1/depth.json?minutes=60',
            #'/poh/data/location/makaha1/depth.json?begin=1478030000&end=1478037569&max_count=1000',
            #'/poh/data/location/makaha1/oxygen.json?begin=1485980000&end=1485986255',
            #'/poh/data/location/makaha1/air.json?begin=1485980000&end=1485986255',
            #'/poh/data/location/makaha1/temperature.json?begin=1485980000&end=1485986255',

            #'/poh/data/location/makaha2/depth.json',
            #'/poh/data/location/makaha2/depth.json?begin=1485980000&end=1485986255',
            #'/poh/data/location/makaha2/depth.json?minutes=60',
            #'/poh/data/location/makaha2/depth.json?begin=1478030000&end=1478037569&max_count=1000',

            #'/makaipier/data/location/dock1/depth.json',
            #'/makaipier/data/location/dock1/depth.json?begin=1485980000&end=1485986255',
            #'/makaipier/data/location/dock1/depth.json?minutes=60',
            #'/makaipier/data/location/dock1/depth.json?begin=1478400000&end=1485900000&max_count=1000',
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

