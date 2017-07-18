from s1 import query_time_range
import xmlrpclib,math


# test the functions directly
# querey multiple params in one go, when "time_col" is within "begin" and "end"
# this does not strip None or float('nan')
# query_time_range() no longer perform POSIX timestamp to datetime.datetime conversion. All time
# data in db should now be in POSIX timestamp.
keys = ['Timestamp','d2w','t']
r = query_time_range('node-047',['Timestamp','d2w','t'],1500000000,1500081792,'ReceptionTime')
assert (len(keys) + 1) == len(r)
assert all([len(r[tmp]) == len(r['ReceptionTime']) for tmp in r])
assert len(r['ReceptionTime']) > 0




# via proxy, when accessed using xmlrpc
proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')

#print proxy.query_time_range('node-021','PH_EXT',1482820675,1482825675)
#print proxy.get_last_N_minutes('node-021','PH_EXT',10)

#https://grogdata.soest.hawaii.edu/poh/data/location/makaha1/depth.json?begin=1487412000&end=1491818400https://grogdata.soest.hawaii.edu/poh/data/location/makaha1/depth.json?begin=&end=
d = proxy.query_time_range('node-009','d2w',1487412000,1491818400,'ReceptionTime')
#d = proxy.query_time_range('node-047',['Timestamp','d2w','t'],1500040946,1500076946,'ReceptionTime')

assert len(d['d2w'])
assert all([not math.isnan(tmp) for tmp in d['d2w']])
assert all([tmp is not None for tmp in d['d2w']])


exit()


from random import randint
for i in range(100):
    N = randint(1,1000)
    lim = randint(1,N)
    a = range(N)
    assert len(proxy.condense(a,lim)) <= lim

