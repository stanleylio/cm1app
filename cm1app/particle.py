import sys, json, time, logging
sys.path.append('/home/nuc')
from datetime import datetime, timedelta
from node.helper import dt2ts, ts2dt
from node.config.c import get_list_of_sites, get_list_of_devices, coreid2nodeid

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
    """return (node-id,list of samples) if message is recognized; (None,"reason") otherwise"""
    nodeid = coreid2nodeid(request.form['coreid'])
    if nodeid is None:
        return None, 'Unknown coreid {}'.format(request.form['coreid'])

    try:
        # firmware version p3~latest
        if u'd2w' == request.form['event']:
            rt = time.time()
            D = []
            for k, s in enumerate(json.loads(request.form['data'])):
                if 2 == len(s):
                    D.append({'Timestamp':s[0], 'd2w':s[1]})
                elif 3 == len(s):
                    D.append({'Timestamp':s[0], 'd2w':s[1], 'sample_size':s[2]})
                elif 4 == len(s):
                    D.append({'ts':s[0], 'd2w':s[1], 'std':s[2], 'sc':s[3]})
            return nodeid, D
        
        elif u'a0' == request.form['event']:
            # An example: '1595457639,300.0,0.0,181,360,0.0,0.0,181;3.963'
            # Values in each sample are:
            tags = ['ts', 'd2w', 'std', 'sc']
            # After the semicolon is the battery voltage Vb.
            # ts and d2w are "compressed" somewhat: they are the deltas from the first sample.

            N = len(tags)
            d,v = request.form['data'].split(';')
            d = [float(dd) for dd in d.split(',')]
            assert 0 == len(d)%N
            d = [d[i:i+N] for i in range(0, len(d), N)]
            # restore the original values by adding the deltas to the first
            for k,s in enumerate(d[1:], 1):
                d[k][0] += d[0][0]
                d[k][1] += d[0][1]
            # caller likes it in a list of dicts
            D = [dict(zip(tags, s)) for s in d]
            # Patch Vb back in - the last sample in the report has the Vb (it's closest to when Vb was measured)
            # The other sample(s) don't have Vb so those will show up as NULL in the database.
            D[-1]['Vb'] = float(v)
            return nodeid, D

        elif u'D1XKIMTJGU' == request.form['event']:    # node-047
            # this is not in use. to be removed soon.
            #D = json.loads(request.form['data'])
            D = parse_node_047_msg(request.form['data'])
            return nodeid, D
        
        elif request.form['event'] in [u's', u'debug']:
            # A Particle Photon in Casey's soil warming setup uses this. The debug messages from tide gauges also use this.
            d = json.loads(request.form['data'])
            return nodeid, [d]
        
        else:
            return None, 'Unknown event'
    except:
        logging.exception(str(dict(request.form)))
        raise
