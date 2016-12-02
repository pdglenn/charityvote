from __future__ import print_function
from application import forms
from flask import Flask, render_template, request
import os
import uuid
import pymysql


from flask_social import Social
from flask_social.datastore import SQLAlchemyConnectionDatastore
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required

application = Flask(__name__)
application.debug = True
application.secret_key = ('you_wont_guess')

application.config.from_pyfile('config.py', silent=True)

print('database is: ',application.config['SQLALCHEMY_DATABASE_URI'])

application.config['SECURITY_POST_LOGIN'] = '/profile'
db = SQLAlchemy()
db.init_app(application)

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    full_name = db.Column(db.String(512))
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))
    rank = db.Column(db.Integer)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(application, user_datastore)
social = Social(application, SQLAlchemyConnectionDatastore(db, Connection))
# Create a user to test with
@application.before_first_request
def create_user():
    db.create_all()
    # user_datastore.create_user(email='matt@nobien.net', password='password')
    db.session.commit()
    pass

@application.route('/')
def index():
    comps = retrieve_all_comps()
    return render_template('index.html')

@application.route('/profile')
@login_required
def profile():
    return render_template(
        'profile.html',
        content='Profile Page',
        facebook_conn=social.facebook.get_connection())

@application.route('/manage')
def manage():
    return render_template('manage.html')


@application.route('/browse')
def browse():
    return render_template('browse.html')


@application.route('/create',methods=['GET','POST'])
def create():
    cform = forms.CreateForm()
    if request.method =="POST":
         if 'add_option' in request.form  :
             optionform = forms.OptionForm()
             optionform.description=""
             optionform.image_url=""
             cform.options.append_entry(optionform)
         if 'submit_comp' in request.form :
            print("submiting ")
            title = cform.title.data
            amount = cform.amount.data
            date = cform.date.data
            comp_id = create_competition(title,amount,date)
            for f in cform.options:
                file_name = f.image_url
                print ("OK" + str(file_name.name))
                files = request.files[file_name.name]
                image_url = os.path.join(application.config['UPLOAD_FOLDER'],files.filename)
                create_option(f.description.data,image_url,comp_id)
                files.save(image_url)

                print(files.filename)

    return render_template('create.html',form = cform)




@application.route('/view/<contest_id>')
def view(contest_id):
    return render_template('view.html')

@application.route('/view/')
def view_generic():
    return render_template('view.html')

@application.route('/results/<contest_id>')
def results(contest_id):

    return render_template('results.html')

@application.route('/results/')
def results_generic():
    return render_template('results.html')

@application.route('/confirmation/<contest_id>')
def confirmation(contest_id):
    return render_template('confirmation.html')
@application.route('/confirmation/')
def gen_confirmation():
    form = form
    return render_template('confirmation.html')

host = application.config['SQL_HOST']
port = 3306
password = application.config['SQL_PASSWORD']
username = application.config['SQL_USERNAME']

def create_competition (title,amount,expiry_date):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    id =  uuid.uuid4()
    cursor.execute("insert into competitions values (%s,%s,%s,%s) ",(id,title,amount,expiry_date))
    db.commit()
    return id

def create_option (description,image_url,comp_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    id =  uuid.uuid4()
    cursor.execute("insert into comp_option values (%s,%s,%s,%s) ",(id,description,image_url,comp_id))
    db.commit()

def retrieve_all_comps():
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    result = cursor.execute("SELECT * from competitions").fetchall()
    return result


if __name__ == '__main__':
    application.run(host='0.0.0.0')
