from flask import Flask

application = Flask(__name__)
# application.config.from_object('config')
application.config.from_pyfile('config.py', silent=True)