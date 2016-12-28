import xmlrpclib


proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8000/')


print proxy.query_time_range('node-021','PH_EXT',1482820675,1482825675)


print proxy.get_last_N_minutes('node-021','PH_EXT',10)


exit()


from random import randint
for i in range(100):
    N = randint(1,1000)
    lim = randint(1,N)
    a = range(N)
    assert len(proxy.condense(a,lim)) <= lim

