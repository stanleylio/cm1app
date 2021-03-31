import MySQLdb, logging


def validate_id(nodeid, var=None):
    conn = MySQLdb.connect(host='localhost', user='webapp', charset='utf8mb4')
    c = conn.cursor()
    c.execute("SELECT nodeid FROM uhcm.`devices` WHERE nodeid=%s", (nodeid, ))
    row = c.fetchone()
    if row is None:
        conn.close()
        return False, 'Error: Unknown node'

    if var is None:
        conn.close()
        return True, ''
    
    c.execute("""SELECT name FROM uhcm.`variables`
                WHERE nodeid=%s
                AND name=%s""", (nodeid, var, ))
    row = c.fetchone()
    if row is None:
        conn.close()
        return False, 'Error: Unknown variable'

    conn.close()
    return True, ''


def auto_time_col(nodeid):
    """Find the best time index to plot against. An attempt is made to
    give preference to the instrument's built-in clock (ts/Timestamp),
    but only if its latest reading is ~1hr of ReceptionTime. Otherwise
    ReceptionTime is used.

    Failure cases that prompted this: node-153's ts is always 0; some
    rain gauges's RTC have the wrong time. Also sometimes ts is NULL and
    so the comparison against ReceptionTime fails. That also makes it
    default to ReceptionTime.
    """
    conn = MySQLdb.connect(host='localhost', user='webapp', charset='utf8mb4')
    cur = conn.cursor()

    try:
        # First see if a preferred time column has been explicitly
        # defined.
        # ... nah. Do this in b.py at "compile" time and you can just
        # read it off the db in runtime.
        cur.execute("""SELECT time_col FROM uhcm.devices WHERE nodeid=%s""", (nodeid, ))
        return cur.fetchone()[0]
    
        '''r = cur.fetchone()
        if r:
            # Could be '', could be NULL/None.
            # Now it defaults to "ReceptionTime", set by b.py if it's
            # undefined in the config, so the else should not trigger.
            #return r[0] if r[0] in ['ts', 'Timestamp', 'ReceptionTime'] else 'ReceptionTime'
            return r[0] if len(r[0]) else 'ReceptionTime'

        # return the first one if defined in ['ts', 'Timestamp', 'ReceptionTime']
        for tc in ['ts', 'Timestamp']:
            #print(nodeid, tc)
            cur.execute("""SELECT name FROM uhcm.variables
                            WHERE nodeid=%s
                            AND name=%s""", (nodeid, tc, ))

            # Additional hack/check: use the instrument's clock only if
            # it's not "too far off". Now this is just heuristics/hack.
            # Ultimately you'd want to define the time axis to use
            # explicitly.
            #
            # TODO: convert the idx to ts somehow. Not sure if that can
            # be automated though since how'd you know the instrument's
            # clock is messed up and not that the messages got queued up
            # in the pipeline?
            if cur.fetchone():
                cur.execute("""SELECT ReceptionTime,`{tc}` FROM uhcm.`{nodeid}`
                                ORDER BY ReceptionTime DESC LIMIT 1""".format(tc=tc, nodeid=nodeid))
                # too slow, but that's the idea:
                #WHERE {tc} IS NOT NULL
                r = cur.fetchone()
                if r is not None:
                    if abs(r[0] - r[1]) < 3600:
                        conn.close()
                        return tc'''
    except:
        logging.exception(nodeid)

    conn.close()
    return 'ReceptionTime'
