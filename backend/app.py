# -*- coding:utf-8 -*-

from flask import Flask
from flask_restplus import Api
from flask_cors import CORS
from api.token import api as token

# create flask app
app = Flask(__name__)

# set CORS to allow all sources to use this api
CORS(app, resources={r"*": {"origins": "*"}})

# create flask api and set token based authorization as authorization method
api = Api(app, authorizations={
    'API-KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'AUTH-TOKEN'
    },
},
          security='API-KEY',
          default="Read Recommendation PRO",  # Default namespace
          title="Read Recommendation PRO",  # Documentation Title
          description="A professional read recommendation system")

# api namespaces
# TODO: finish all api
api.add_namespace(token)

if __name__ == '__main__':
    # app.run(debug=True, host='localhost', port=[some_port_number])
    app.run(debug=True)