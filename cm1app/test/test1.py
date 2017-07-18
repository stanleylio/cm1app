import requests,random,math

host = 'http://grogdata.soest.hawaii.edu'

def test1(ep):
    '''Check that the endpoint is available, and there's no None or NaN in the response.'''
    print('testing {}'.format(ep))
    r = requests.get(ep)
    assert r.status_code == 200
    r = r.json()
    assert 'samples' in r
    #print len(r['samples']['d2w'])
    for k in r['samples']:
        assert all([tmp is not None for tmp in r['samples'][k]])
        assert all([not math.isnan(tmp) for tmp in r['samples'][k]])


# tide gauges
nodes = ['node-008','node-009','node-014','node-015','node-047','node-048']

for node in nodes:
    end = random.randint(1497130276,1500154178)
    begin = end - 6*3600
    # no longer checks if node is in site. site has to be a known site though.
    ep = '/poh/data/{node}/d2w.json?begin={begin}&end={end}'.\
         format(node=node,
                begin=begin,
                end=end)
    ep = host + ep
    test1(ep)

# - - - - -
# misc. stuff, including static files

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
    print('testing {}'.format(ep))
    code = requests.get(ep).status_code
    if code != 200:
        print(code)
        #print(ep)

print('done')

