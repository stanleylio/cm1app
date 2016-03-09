activate_this = '/home/nuc/cm1app/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys,logging
logging.basicConfig(stream=sys.stderr)
sys.path.append('/home/nuc/cm1app')
from cm1app.f4 import app as application
