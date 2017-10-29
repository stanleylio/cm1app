import sys,json,time
sys.path.append('/home/nuc')
from datetime import datetime,timedelta
from node.helper import dt2ts,ts2dt
from node.config.config_support import get_config,get_list_of_sites,get_list_of_nodes


fish_map = {}

def coreid2nodeid(coreid):
    # WARNING: coreid is probably of type "unicode"...
    global fish_map

    if coreid not in fish_map:
        for site in sorted(get_list_of_sites()):
            for node in get_list_of_nodes(site):
                tmp = get_config('coreid',node)
                if tmp is not None:
                    fish_map[tmp] = node
    return fish_map.get(coreid,None)


def parse_electron_msg(ts,s,sample_interval=60):
    s = s.split(',')
    s = [float(tmp) for tmp in s]
    t = [tmp*sample_interval for tmp in range(0,len(s))]
    t = t[::-1]
    t = [ts - tmp for tmp in t]
    return zip(t,s)

def fish_handler(request):
    nodeid = coreid2nodeid(request.form['coreid'])
    if nodeid is None:
        return None,'unknown coreid'

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
        # firmware version p3~p5e
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
