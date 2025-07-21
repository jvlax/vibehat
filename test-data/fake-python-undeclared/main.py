import requests
import flask
import pandas as pd

# These imports are NOT in requirements.txt - potential dependency confusion targets
import company_internal_tools
import missing_data_processor
from undeclared_auth import authenticate
from secret_config import load_config

# Relative imports to other files with undeclared deps
from .utils import helper_function

app = flask.Flask(__name__)

@app.route('/')
def index():
    config = load_config()
    user = authenticate(flask.request.headers.get('Authorization'))
    
    data = company_internal_tools.fetch_data(user.id)
    processed = missing_data_processor.clean(data)
    
    return flask.jsonify(processed)

if __name__ == '__main__':
    app.run() 