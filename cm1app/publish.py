import pika, logging, traceback, time, sys
from socket import gethostname
from os.path import expanduser
sys.path.append(expanduser('~'))
from cred import cred


nodeid = gethostname()

# HACK
BROKER = '192.168.0.28'
PORT = 5672


def to_uhcm_xchg(lines, routing_key):
    try:
        exchange = 'uhcm'
        credentials = pika.PlainCredentials(nodeid, cred['rabbitmq'])
        connection = pika.BlockingConnection(pika.ConnectionParameters(BROKER, PORT, '/', credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)

        if type(lines) not in [tuple, list]:
            lines = [lines]

        for line in lines:
            channel.basic_publish(exchange=exchange,
                                  routing_key=routing_key,
                                  body=line,
                                  properties=pika.BasicProperties(delivery_mode=2,
                                                                  content_type='text/plain',
                                                                  expiration=str(30*24*3600*1000)))
        connection.close()
    except:
        logging.exception(traceback.format_exc())


if '__main__' == __name__:
    for i in range(10):
        to_uhcm_xchg('haha!', nodeid + '.debug')
