"""
... hum. You can use parameter substitution for some but not all places,
like you can't do
    SELECT %s,%s FROM table
but you can do
    SELECT ts,d2w FROM table WHERE col=%s

But I guess having webapp as a SELECT only user spares me from SQL
injection. I guess.
"""
import logging, xmlrpc.client, socket, json, MySQLdb, time
from flask import Flask, render_template, request, escape, Response
from cm1app import app
from datetime import datetime, timedelta
from node.helper import dt2ts
from node.config.c import config_as_dict, get_list_of_devices, get_list_of_variables, get_variable_attribute
from cm1app import dashboard, nodepage, v5
from cm1app.common import validate_id, auto_time_col


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


@app.route('/')
def route_default():
    return render_template('index.html')


# Q: Wait who is using this again?
# A: That node selector on the dashboard. It's the only place where a
# list of ALL devices are needed. The other places like the dashboard
# are either generated with a given site ID, or a list of nodes is
# explicitly given.
@app.route('/data/2/config/listing')
def get_listing():
    return Response(json.dumps(config_as_dict(), separators=(',',':')),
                    mimetype='application/json; charset=utf-8')


# check __init__.py for the line that enables CORS at this endpoint
@app.route('/data/2/<node>/<variables>.json')
#@cross_origin() this doesn't work for some reason
def get_xy2(node, variables):
    """Examples:
    https://grogdata.soest.hawaii.edu/data/2/node-047/Timestamp,d2w,t.json?begin=1500000000&end=1500082230&time_col=Timestamp
    https://grogdata.soest.hawaii.edu/data/2/node-049/ReceptionTime,d2w.json?time_col=ReceptionTime&begin=1609495200.0&end=1614849169.1146927

    Note: obsolete, but kept for backward compatibility. get_xy3 is more
    performant (~25% response time).
    """
    logger.debug((node, variables))

    variables = variables.split(',')                # assumption: no comma in variable name... it seems most of programming is the problem of encoding and decoding. "Do you mean this word literally or do you mean the thing behind this word"...
    variables = [v.strip() for v in variables]
    begin = request.args.get('begin')
    end = request.args.get('end')
    time_col = request.args.get('time_col').strip()

    if begin is None:
        return 'missing: begin'
    if end is None:
        return 'missing: end'
    if time_col is None:
        return 'missing: time_col'
    if time_col not in variables:
        return '"time_col" must be among the list of variables. Most likely one of {"ReceptionTime","Timestamp","ts"}.'

    try:
        begin = float(begin)
        end = float(end)
    except ValueError:
        return '"begin" and "end" must be numbers.'

    try:
        if node not in get_list_of_devices():
            return 'No such node: {}'.format(escape(node))

        columns = get_list_of_variables(node)
        if time_col not in columns:
            return 'No such time column: {}'.format(escape(time_col))
        for var in variables:
            if var not in columns:
                return 'No such variable: {}'.format(escape(var))

        proxy = xmlrpc.client.ServerProxy('http://127.0.0.1:8000/')
        r = proxy.query_time_range2(node, variables, begin, end, time_col)
        return Response(json.dumps(r, separators=(',', ':')),
                        mimetype='application/json; charset=utf-8')
    except:
        logging.exception('')
        return "it's beyond my paygrade 2"


@app.route('/data/3/<node>/<variables>.json')
def get_xy3(node, variables):
    """Same semantics and function as get_xy2 above, except this talks
    to the db directly. Six years into the project I now know there is
    no other database, and local user can do passwordless login.

    Example:
    https://grogdata.soest.hawaii.edu/data/3/node-049/ReceptionTime,d2w.json?time_col=ReceptionTime&begin=1609495200.0&end=1614849169.1146927
    """
    variables = [v.strip() for v in variables.split(',')]
    begin = request.args.get('begin')
    end = request.args.get('end')
    time_col = request.args.get('time_col', default=None)
    if time_col is None:
        time_col = auto_time_col(node)
    else:
        time_col = time_col.strip()
    if begin is None:
        return 'missing: begin'
    if end is None:
        return 'missing: end'

    # This is tricky. Say if 'ts' is among the list of variables, then
    # select ts,ts gives you nothing useful so you want to use
    # ReceptionTime as your index even if time_col has been explicitly
    # defined.
    #
    # Sure it's ill-defined (if you say "ts" is the time index and not a
    # variable being measured, then having ts in the list of requested
    # variables is an incorrect usage). But I also don't want more
    # "rules" that the API users need to remember ("you are allowed to
    # request any variables listed, except the time indices").
    #
    # On the other hand you can't exclude or hide the ts/Timestamp
    # because for ones that are not as reliable (e.g. the ECO FLNTUSB),
    # you really do want to inspect ts vs. ReceptionTime sometimes to
    # make sure the instrument RTC is working.
    #
    # Without some sort of formal proof it's just an endless game of
    # whack a mole.
    if time_col in variables:
        time_col = 'ReceptionTime'
    if time_col not in variables:
        variables.insert(0, time_col)
    
    try:
        begin = float(begin)
        end = float(end)
    except ValueError:
        return '"begin" and "end" must be numbers.'

    try:
        conn = MySQLdb.connect('localhost', user='webapp', charset='utf8mb4')
        cur = conn.cursor()

        # Wait, is it filtering "any NULL" or "all NULL"? I think I read
        # it as "no NULL" in any *selected* columns, so it's ok if Vb is
        # never in the same row as d2w, because they are not selected in
        # the same call.
        # Turns out coalesce gets you the row that has at least one
        # non-null. I'm looking for all the rows that don't have any
        # null.
        cmd = """SELECT {} FROM uhcm.`{}`
                WHERE {} BETWEEN %s AND %s
                {}""".format(','.join(['`{}`'.format(v) for v in variables]),
                             node,
                             time_col,
                             ' '.join(['AND `{}` IS NOT NULL'.format(v) for v in variables]))
        # Seems to be some kind of bug with parameter substitution. The
        # IS NOT NULL condition is ignored for some reason.
        #' '.join(['AND %s IS NOT NULL' for v in variables]))
        #print(cmd)
        #cur.execute(cmd, (begin, end, *variables, ))
        cur.execute(cmd, (begin, end, ))
        d = {'time_col':time_col,
             'd':list(cur.fetchall()),
             }
        return Response(json.dumps(d),
                        mimetype='application/json; charset=utf-8')
    except MySQLdb.OperationalError as e:
        m = '{}, {}, {}, {}, {}'.format(node, variables, time_col, begin, end, )
        logger.exception(m)
        return "It's beyond my paygrade: {}".format(escape(m))

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/tech/')
def tech():
    return render_template('tech.html')

@app.route('/tech/tidegauge/')
def tidegauge():
    return render_template('tidegauge.html')

@app.route('/tech/logger/')
def kiwilogger():
    return render_template('logger.html')

@app.route('/tech/loggerhd/')
def kiwiloggerhd():
    return render_template('loggerhd.html')

@app.route('/dev/')
def dev():
    return render_template('dev.html')

@app.route('/dev/rtcomm')
def rtcomm():
    return render_template('rtcomm.html')

@app.route('/project_info/')
def project_info():
    return render_template('project_info.html')

@app.route('/data_access/')
def data_access():
    return render_template('data_access.html')
