import sys, logging, time, MySQLdb
from os.path import expanduser
sys.path.append(expanduser('~'))
from node.helper import dt2ts
from datetime import datetime
from numpy import mean
from scipy.signal import medfilt


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def read_latest_sample(time_col, node, var):
    try:
        conn = MySQLdb.connect('localhost', user='webapp', charset='utf8mb4')
        cur = conn.cursor()

        cmd = """SELECT `{time_col}`,`{var}`
                FROM uhcm.`{node}`
                WHERE {var} IS NOT NULL
                ORDER BY {time_col} DESC LIMIT 1""".format(time_col=time_col, node=node, var=var)
        cur.execute(cmd)
        L = list(cur.fetchone())
        conn.close()
        return L
    except (MySQLdb.OperationalError, TypeError):
        # you get TypeError if fetchone returns no row.
        conn.close()
        return None


if '__main__' == __name__:
    pass
    
