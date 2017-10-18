import sys,json,time
sys.path.append('/home/nuc')
from datetime import datetime,timedelta
from node.helper import dt2ts,ts2dt


def parse_electron_msg(ts,s,sample_interval=60):
    s = s.split(',')
    s = [float(tmp) for tmp in s]
    t = [tmp*sample_interval for tmp in range(0,len(s))]
    t = t[::-1]
    t = [ts - tmp for tmp in t]
    return zip(t,s)

def fish_handler(request):
    # TODO: grab these from the config files
    fish_map = {u'1f0024001751353338363036':'node-028', # Boston, Amy Mueller
                u'450057000a51343334363138':'node-029', # Boston, Amy Mueller
                u'280021001951353338363036':'node-045', # SF, Jim Trezzo
                u'360064001951343334363036':'node-046', # NOAA, Coconut
                u'410055001951353338363036':'node-047', # T/P/RH test bed
                #u'180033001951353338363036':'node-048',
                u'33002f001851353338363036':'node-048',
                u'3e0042001951353338363036':'node-049', # First Makaha, PoH
                u'2d0039001851353338363036':'node-050',
                u'230053001951353338363036':'node-051', # Storm Makaha, PoH
                u'4e0029001751353338363036':'node-052', # Waikalua Loko
                #u'3a0038001751353338363036':'node-053',
                u'23003b000351353337353037':'node-053',
                u'4e0053001851353338363036':'node-054',
                u'210048001851353338363036':'node-055',
                u'2a002b001751353338363036':'node-056',
                u'190049000251353337353037':'node-057',
                u'40002e001951353338363036':'node-058', # Moonshot
                u'290048001951353338363036':'node-059',
                #u'5d003e001951353338363036':'node-060',
                u'2b001b001951353338363036':'node-060',
                u'4d0038001751353338363036':'node-061', # Moonshot
                u'2d0044001851353338363036':'node-062',
                #u'2f002f001951353338363036':'node-063',
                u'3d0058001751353338363036':'node-063',
                #u'420030001751353338363036':'node-064',
                u'1e0029001751353338363036':'node-064',
                u'2d0055001851353338363036':'node-065',
                u'2e0056001751353338363036':'node-066',
                u'1e002c001751353338363036':'node-067',
                u'470032001951353338363036':'node-068',
                u'4d0057001851353338363036':'node-069',
                u'4b002f001951343334363036':'node-070',
                #u'580052001951353338363036':'node-071',
                u'230048001951353338363036':'node-071',
                u'220026000351353337353037':'node-072',
                u'1d0053000251353337353037':'node-073',
                u'1f0043000251353337353037':'node-074',
                u'25002d001951353338363036':'node-075',
                u'40004f001951353338363036':'node-076', # Moonshot
                u'4d0058001851353338363036':'node-077',
                }

    if request.form['coreid'] not in fish_map:
        return None,'unknown coreid'

    nodeid = fish_map[request.form['coreid']]
    if nodeid in ['node-028','node-029']:
        # firmware version p2
        published_at = request.form['published_at']
        published_at = datetime.strptime(published_at,'%Y-%m-%dT%H:%M:%S.%fZ')
        published_at = dt2ts(published_at)
        d = []
        for s in parse_electron_msg(published_at,request.form['data']):
            d.append({'ReceptionTime':s[0],'d2w':s[1]})
        return nodeid,d
    else:
        # firmware version p3~p5d
        if u'd2w' == request.form['event']:
            rt = time.time()
            d = []
            for k,s in enumerate(json.loads(request.form['data'])):
                # is that cheating?
                # ReceptionTime has to be unique in db, but they do arrive at almost the same time
                if 2 == len(s):
                    #d.append({'ReceptionTime':rt + k*1e-5,'Timestamp':s[0],'d2w':s[1]})
                    d.append({'Timestamp':s[0],'d2w':s[1]})
                elif 3 == len(s):
                    #d.append({'ReceptionTime':rt + k*1e-5,'Timestamp':s[0],'d2w':s[1],'sample_size':s[2]})
                    d.append({'Timestamp':s[0],'d2w':s[1],'sample_size':s[2]})
            return nodeid,d
        elif u'debug' == request.form['event']:
            d = json.loads(request.form['data'])
            d['ReceptionTime'] = time.time()
            return nodeid,[d]

            '''d = json.loads(request.form['data'])
            if 'VbattV' in d:
                d['ReceptionTime'] = time.time()
                return nodeid,[d]
            else:
                return nodeid,None'''
