# Tests for endpoints used by maitaid app (David)
#
# Stanley H.I. Lio
# hlio@hawaii.edu
# University of Hawaii, 2017
import unittest,requests,logging


logging.basicConfig(level=logging.WARNING)


class TestMaitaidApp(unittest.TestCase):
    
    def test_pastN(self):
        urls = ['https://grogdata.soest.hawaii.edu/poh/data/location/makaha1/depth.json?begin=1508140000&end=1508144219',
                'https://grogdata.soest.hawaii.edu/poh/data/location/makaha2/depth.json?begin=1508140000&end=1508144219',
                'https://grogdata.soest.hawaii.edu/poh/data/location/makaha3/depth.json?begin=1508140000&end=1508144219',
                'https://grogdata.soest.hawaii.edu/poh/data/location/river/depth.json?begin=1508140000&end=1508144219',
                'https://grogdata.soest.hawaii.edu/coconut/data/location/noaa/depth.json?begin=1508140000&end=1508144219',
                'https://grogdata.soest.hawaii.edu/coconut/data/location/bridge/depth.json?begin=1508140000&end=1508144219',
                'https://grogdata.soest.hawaii.edu/poh/data/location/makaha1/salinity.json?begin=1508140000&end=1508144219',
                ]
        for url in urls:
            if not 200 == requests.get(url).status_code:
                logging.info(url)
                self.assertTrue(False)
        

if __name__ == '__main__':
    unittest.main()
