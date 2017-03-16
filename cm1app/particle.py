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
    fish_map = {u'1f0024001751353338363036':'node-016'}
    #if request.form['coreid'] not in [u'1f0024001751353338363036']:
    #    return

    if request.form['coreid'] not in fish_map:
        #print('unknown coreid')
        return

    if request.form['event'] != u'd2w':
        #print('not d2w')
        return

    if request.form['data'] == u'test-event':
        #print('this is a test')
        return
    
    nodeid = fish_map[request.form['coreid']]
    published_at = request.form['published_at']
    published_at = datetime.strptime(published_at,'%Y-%m-%dT%H:%M:%S.%fZ')
    published_at = dt2ts(published_at)

    return nodeid,parse_electron_msg(published_at,request.form['data'])