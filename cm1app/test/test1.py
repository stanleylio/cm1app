import requests

host = 'http://grogdata.soest.hawaii.edu'

eps = [
    '/poh/nodepage/node-004.json',
    '/poh/data/node-004/O2Concentration.json?minutes=46080',
    '/makaipier/data/node-010/d2w.json?begin=1480800106&end=1480808106',
    '/poh/data/node-022/PH_EXT.json?begin=1480800106&end=1480808106&max_count=5',
    '/static/img/poh/node-004/AirSaturation.json',
    #'/static/img/poh/node-001/Temperature.json',

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
    '/makaipier/data/location/dock1/depth.json?begin=1478043041&end=1485900000&max_count=1000',
    ]

for ep in eps:
    print('testing {}'.format(ep))
    ep = host + ep
    code = requests.get(ep).status_code
    if code != 200:
        print(code)
        print(ep)

print('done')
