import MySQLdb

def validate_id(nodeid, var=None):
    conn = MySQLdb.connect(host='localhost', user='webapp', passwd='', db='uhcm', charset='utf8mb4')
    c = conn.cursor()
    c.execute("SELECT nodeid FROM uhcm.`devices` WHERE nodeid=%s", (nodeid,))
    row = c.fetchone()
    if row is None:
        conn.close()
        return False, 'Error: Unknown node'

    if var is None:
        conn.close()
        return True, ''
    
    c.execute("SELECT name from uhcm.`variables` where name=%s", (nodeid, var, ))
    row = c.fetchone()
    if row is None:
        conn.close()
        return False, 'Error: Unknown variable'

    conn.close()
    return True, ''
