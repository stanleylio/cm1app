import sys, logging
from os.path import expanduser

sys.path.append(expanduser('~'))
sys.path.append('/var/www/cm1app')

logging.basicConfig(stream=sys.stderr)

from cm1app.f4 import app as application
