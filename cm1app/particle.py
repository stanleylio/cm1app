import sys
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
    fish_map = {u'1f0024001751353338363036':'node-028',
                u'450057000a51343334363138':'node-029'}
    #if request.form['coreid'] not in [u'1f0024001751353338363036']:
    #    return

    if request.form['coreid'] not in fish_map:
        return None,'unknown coreid'

    if request.form['event'] == u'test-event':
        return None,'this is a test'
    
    if request.form['event'] != u'd2w':
        return None,'not d2w'

    nodeid = fish_map[request.form['coreid']]
    published_at = request.form['published_at']
    published_at = datetime.strptime(published_at,'%Y-%m-%dT%H:%M:%S.%fZ')
    published_at = dt2ts(published_at)

    return nodeid,parse_electron_msg(published_at,request.form['data'])
