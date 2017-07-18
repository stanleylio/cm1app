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
    fish_map = {u'1f0024001751353338363036':'node-028', # Boston
                u'450057000a51343334363138':'node-029', # Boston
                u'280021001951353338363036':'node-045', # Haley
                u'360064001951343334363036':'node-046', # Haley
                u'410055001951353338363036':'node-047', # test bed
                u'180033001951353338363036':'node-048', # v0.1 PCB
                u'3e0042001951353338363036':'node-049', # ?
                u'2d0039001851353338363036':'node-050', # ?
                u'230053001951353338363036':'node-051', #
                u'4e0029001751353338363036':'node-052', #
                u'3a0038001751353338363036':'node-053',
                u'4e0053001851353338363036':'node-054',
                u'210048001851353338363036':'node-055',
                u'2a002b001751353338363036':'node-056',
                u'190049000251353337353037':'node-057',
                u'40002e001951353338363036':'node-058',
                u'290048001951353338363036':'node-059',
                u'5d003e001951353338363036':'node-060',
                u'4d0038001751353338363036':'node-061',
                u'2d0044001851353338363036':'node-062',
                }

    if request.form['coreid'] not in fish_map:
        return None,'unknown coreid'

    nodeid = fish_map[request.form['coreid']]
    if nodeid in ['node-028','node-029']:   # firmware version p2
        published_at = request.form['published_at']
        published_at = datetime.strptime(published_at,'%Y-%m-%dT%H:%M:%S.%fZ')
        published_at = dt2ts(published_at)
        d = []
        for s in parse_electron_msg(published_at,request.form['data']):
            d.append({'ReceptionTime':s[0],'d2w':s[1]})
        return nodeid,d
    else:   # firmware version p3
        # ... but does that guarantee ReceptionTime's uniqueness?
        if u'd2w' == request.form['event']:
            rt = time.time()
            d = []
            for k,s in enumerate(json.loads(request.form['data'])):
                d.append({'ReceptionTime':rt + k*1e-5,'Timestamp':s[0],'d2w':s[1]}) # is that cheating?
            return nodeid,d
        elif u'debug' == request.form['event']:
            d = json.loads(request.form['data'])
            if 'VbattV' in d:
                d['ReceptionTime'] = time.time()
                return nodeid,[d]
            else:
                return nodeid,None
