from __future__ import print_function
from application import forms
from flask import Flask, render_template, request, url_for, redirect
from flask_oauth import OAuth
import os
import uuid
import pymysql
import random,time
from flask import session


from flask_social import Social
from flask_social.datastore import SQLAlchemyConnectionDatastore
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required

application = Flask(__name__)
application.debug = True
application.secret_key = ('you_wont_guess')

application.config.from_pyfile('config.py', silent=True)

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=application.config['FACEBOOK_APP_ID'],
    consumer_secret=application.config['FACEBOOK_APP_SECRET'],
    request_token_params={'scope': ('email, ')}
)

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
    reco_comps = retrieve_reco_comps()
    featured_comp = retrieve_featured_comp()
    return render_template('index.html')

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)

@application.route("/facebook_login")
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next'), _external=True))

@application.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)

    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')

    return redirect(next_url)

@application.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))


# @application.route('/profile')
# @login_required
# def profile():
#     return render_template(
#         'profile.html',
#         content='Profile Page',
#         facebook_conn=social.facebook.get_connection())

# @application.route('/login')
# def login():
#     print('hello world')
#     if current_user.is_authenticated():
#         return redirect(request.referrer or '/')

#     return render_template('login.html', form=forms.LoginForm())

@application.route('/manage')
def manage():
    return render_template('manage.html')


@application.route('/browse')
def browse():
    return render_template('browse.html')


@application.route('/create',methods=['GET','POST'])
def create():
    session ["user_id"] =1
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

            comp_file = cform.comp_img.data
            files = request.files[comp_file.name]
            location = os.path.join(application.config['UPLOAD_FOLDER'],files.filename)
            description = cform.comp_description.data
            location_indb = "images/"+files.filename
            comp_id = create_competition(title,description,amount,date,location_indb,str (session ["user_id"]))
            files.save(location)

            for f in cform.options:
                file_name = f.image_url
                cur = f.data
                print (cur)
                print ("OK" + str(file_name.name))
                files = request.files[file_name.name]
                location = os.path.join(application.config['UPLOAD_FOLDER'],files.filename)
                location_indb = "images/"+files.filename
                print ("trial and error "+ str(cur["description"]))
                create_option(f.description,location_indb,comp_id)
                files.save(location)


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

def create_competition (title,description,amount,expiry_date,image_url,user_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    print ("Creating Competition")
    flag = 1
    while flag == 1:
        try:
            id =  int(time.time()) + int(random.random())
            cursor.execute("insert into competitions(id,title,description,amount,date,image_url,user_id) values (%s,%s,%s,%s,%s,%s,%s) ",(id,title,description,amount,expiry_date,image_url,user_id))
            flag = 0
        except pymysql.IntegrityError as e:
            if 'PRIMARY' in e.message:
                continue
    db.commit()
    print ("Creating Done")
    return id

def create_option (description,image_url,comp_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    flag = 1
    while flag ==1:
        try:
            id =  int(time.time()) + int(random.random())
            cursor.execute("insert into comp_option (id,description,image_url,comp_id,votes) values (%s,%s,%s,%s,0) ",(id,description,image_url,comp_id))
            flag = 0
        except pymysql.IntegrityError as e:
            if 'PRIMARY' in e.message:
                continue

    db.commit()

def retrieve_reco_comps():
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute("SELECT * from competitions limit 3")
    result = cursor.fetchall()
    print(result)
    return result

def retrieve_featured_comp():
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute("SELECT * from competitions ORDER BY RAND() LIMIT 1")
    result = cursor.fetchall()
    return result

if __name__ == '__main__':
    application.run(host='0.0.0.0')
