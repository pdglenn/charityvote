from flask import Flask

application = Flask(__name__)
application.config.from_pyfile('config.py')
# application.config.from_envvar('PROD_CONFIG', silent=True)
