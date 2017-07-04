import pika,logging,traceback,time,sys
from socket import gethostname
from os.path import expanduser
sys.path.append(expanduser('~'))
from cred import cred


def to_uhcm_xchg(line,routing_key):
    try:
        exchange = 'uhcm'
        credentials = pika.PlainCredentials('nuc',cred['rabbitmq'])
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange,type='topic',durable=True)
        channel.basic_publish(exchange=exchange,
                              routing_key=routing_key,
                              body=line,
                              properties=pika.BasicProperties(delivery_mode=2,
                                                              content_type='text/plain',
                                                              expiration=str(30*24*3600*1000),
                                                              timestamp=time.time()))
        connection.close()
    except:
        logging.exception(traceback.format_exc())


if '__main__' == __name__:
    nodeid = gethostname()
    for i in range(100):
        to_uhcm_xchg('haha!',nodeid + '.debug')
