import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SOCIAL_FACEBOOK = {
    'consumer_key': '1761103010806827',
    'consumer_secret': 'ea89f06f673f7a2ed5de4abec05bee69'
}
UPLOAD_FOLDER = 'images/'

SQL_HOST = "charityvote.cloalfxvxpbz.us-west-2.rds.amazonaws.com"
SQL_PASSWORD = "tree1234"
SQL_USERNAME = "root"
