import socket,sys,logging

sys.path.append('/home/nuc/cm1app')
sys.path.append('/var/www/cm1app')

if 'glazerlab-i7' == socket.gethostname():
	activate_this = '/home/nuc/cm1app/env/bin/activate_this.py'
if 'glazerlab-e5' == socket.gethostname():
	activate_this = '/var/www/cm1app/env/bin/activate_this.py'
if 'base-005' == socket.gethostname():
	activate_this = '/var/www/cm1app/env/bin/activate_this.py'

execfile(activate_this, dict(__file__=activate_this))

logging.basicConfig(stream=sys.stderr)
from cm1app.f4 import app as application
