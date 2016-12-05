from flask import Flask

application = Flask(__name__)
application.config.from_envvar('PROD_CONFIG')
# application.config.from_pyfile('../.ebextensions/config.py', silent=True)