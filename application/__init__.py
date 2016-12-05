from flask import Flask

application = Flask(__name__)
print('CONFIGGING WOO OWO')
application.config.from_pyfile('config.py')
print('APP CONFIG PAUL', application.config)
# application.config.from_envvar('PROD_CONFIG', silent=True)
