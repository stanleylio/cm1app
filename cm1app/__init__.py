# see http://flask.pocoo.org/docs/0.10/patterns/packages/
from flask import Flask
# when installing flask_cors, install it within the virtualenv, not system-wide.
from flask_cors import CORS
app = Flask(__name__)
#CORS(app)  # enable on all routes
cors = CORS(app, resources={r"/data/2/*": {"origins": "*"}})
import cm1app.f4

