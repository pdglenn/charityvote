from application import forms, models
from flask import (Flask, request, render_template, session, 
    redirect, url_for, escape, flash, abort)

application = Flask(__name__)
application.debug = True
application.secret_key = ('you_wont_guess')

@application.route('/')
def index():
    return 'Hello world'

if __name__ == '__main__':
    application.run(host='0.0.0.0')