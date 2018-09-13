import sys, json, time
sys.path.append('/home/nuc')
from datetime import datetime, timedelta
from node.helper import dt2ts, ts2dt
from node.config.config_support import get_config, get_list_of_sites, get_list_of_nodes


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
    return fish_map.get(coreid, None)

def parse_electron_msg(ts, s, sample_interval=60):
    s = s.split(',')
    s = [float(tmp) for tmp in s]
    t = [tmp*sample_interval for tmp in range(0, len(s))]
    t = t[::-1]
    t = [ts - tmp for tmp in t]
    return zip(t, s)

def parse_node_047_msg(m):
    d = json.loads(m)
    D = []
    for v in d[:-2]:
        D.append(dict(zip(['ts', 'Ta', 'Pa', 'RH', 'Tw', 'Pw', 'ssa', 'ssw'], v)))
    D[-1]['VbattV'] = d[-2]
    D[-1]['SoC'] = d[-1]
    return D

def fish_handler(request):
    """return (node-id,list of samples) if message is recognized; (None,reason as string) otherwise"""
    nodeid = coreid2nodeid(request.form['coreid'])
    if nodeid is None:
        return None, 'unknown coreid'

    # firmware version p3~p6c
    if u'd2w' == request.form['event']:
        rt = time.time()
        D = []
        for k, s in enumerate(json.loads(request.form['data'])):
            if 2 == len(s):
                D.append({'Timestamp':s[0], 'd2w':s[1]})
            elif 3 == len(s):
                D.append({'Timestamp':s[0], 'd2w':s[1], 'sample_size':s[2]})
        return nodeid, D
    elif u'D1XKIMTJGU' == request.form['event']:    # node-047
        #D = json.loads(request.form['data'])
        D = parse_node_047_msg(request.form['data'])
        return nodeid, D
    elif request.form['event'] in [u's', u'debug']:
        d = json.loads(request.form['data'])
        return nodeid, [d]
    else:
        return None, 'Unknown event'
