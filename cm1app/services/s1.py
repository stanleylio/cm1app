import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer


def condense(d,max_count):
    """recursively subsample d until len(d) <= max_count
subsample at a 2:1 ratio"""
    assert type(max_count) in [float,int]
    if len(d) > max_count:
        return condense(d[0::2],max_count)
    return d


server = SimpleXMLRPCServer(("localhost",8000))
server.register_function(condense,"condense")
server.serve_forever()
