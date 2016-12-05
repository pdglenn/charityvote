from __future__ import print_function
from application import forms
from flask import Flask, render_template, request, url_for, redirect
from flask_oauth import OAuth
import os
import uuid
import pymysql
import random,time
from flask import session
import time


application = Flask(__name__)
application.config.from_pyfile('config.py')

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


@application.route('/')
def index():
    session['previous_page'] = '/'
    reco_comps = retrieve_reco_comps()
    featured_comp = retrieve_featured_comp()
    print("*********")
    print(featured_comp)
    return render_template('index.html', featured=featured_comp,
                           reco=reco_comps)

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
    next_url = session.get('previous_page') or request.args.get('next') or url_for('index')
    if next_url == 'order_with_id':
        session.pop('previous_page')
        return redirect(url_for('order_with_id', option_id=session.get('option_id')))
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)

    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')

    data = facebook.get('/me').data
    if 'id' in data and 'name' in data:
        session['user_id'] = data['id']
        session['user_name'] = data['name']

    return redirect(next_url)

@application.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))


@application.route('/login_required')
def login_required():
    return render_template('login_required.html')

@application.route('/manage')
def manage():
    if not session.get('logged_in'):
        session['previous_page'] = '/manage'
        return redirect(url_for('login_required'))
    return render_template('manage.html')


@application.route('/browse')
def browse():
    ongoing = retrieve_ongoing_comps()
    completed = retrieve_completed_comps()
    print('completed', completed)
    return render_template('browse.html', ongoing=ongoing, completed=completed)


@application.route('/create',methods=['GET','POST'])
def create():
    if not session.get('logged_in'):
        session['previous_page'] = '/create'
        return redirect(url_for('login_required'))
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

            comp_id = create_competition(title,description,amount,date,location_indb,str(session ["user_id"]))
            files.save(location)
            print(cform.options)
            for f in cform.options:
                file_name = f.image_url
                cur = f.data
                print (cur)
                print ("OK" + str(file_name.name))

                files = request.files[file_name.name]
                location = os.path.join(application.config['UPLOAD_FOLDER'],files.filename)
                location_indb = "images/"+files.filename
                print ("trial and error "+ str(cur["description"]))
                print('description', f.description)
                create_option(str(cur["description"]),location_indb,comp_id)
                files.save(location)


                print(files.filename)
            # return redirect({{ url_for('view', contest_id=comp_id) }})
            return redirect('/view/'+str(comp_id))
    return render_template('create.html',form = cform)


@application.route('/view/<contest_id>')
def view(contest_id):
    details = competition_details(contest_id)
    options = competition_options(contest_id)
    return render_template('view.html', details=details, options=options)

@application.route('/view/')
def view_generic():
    return render_template('view.html')


@application.route('/order/', methods=['POST', 'GET'])
def order():
    if request.method == 'GET':
        return redirect(url_for('browse'))
    if not session.get('logged_in'):
        session['previous_page'] = 'order_with_id'
        session['option_id'] = request.form.get('group1')
        return redirect(url_for('login_required'))

    option_id = request.form.get('group1')
    if not option_id:
        return redirect(url_for('browse'))
    return redirect('order_with_id', option_id=option_id)


@application.route('/order_with_id/<option_id>', methods=['GET'])
def order_with_id(option_id):
    if not session.get('logged_in'):
        session['previous_page'] = '/create'
        return redirect(url_for('login_required'))
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

            comp_id = create_competition(title,description,amount,date,location_indb,str(session ["user_id"]))
            files.save(location)
            print(cform.options)
            for f in cform.options:
                file_name = f.image_url
                cur = f.data
                print (cur)
                print ("OK" + str(file_name.name))

                files = request.files[file_name.name]
                location = os.path.join(application.config['UPLOAD_FOLDER'],files.filename)
                location_indb = "images/"+files.filename
                print ("trial and error "+ str(cur["description"]))
                print('description', f.description)
                create_option(str(cur["description"]),location_indb,comp_id)
                files.save(location)


                print(files.filename)
            # return redirect({{ url_for('view', contest_id=comp_id) }})
            return redirect('/view/'+str(comp_id))
    return render_template('create.html',form = cform)
    
    return option_id


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
            print ("trying")
            id =  int(time.time()) + int(random.random())
            cursor.execute("insert into competitions(id,title,description,amount,date,image_url,user_id) values (%s,%s,%s,%s,%s,%s,%s) ",(id,title,description,amount,expiry_date,image_url,user_id))
            # print("insert into competitions(id,title,description,amount,date,image_url,user_id) values (%s,%s,%s,%s,%s,%s,%s) ",(id,title,description,amount,expiry_date,image_url,user_id))
            flag = 0
        except pymysql.IntegrityError as e:
            print ("problem")
            print (str (id))
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
    db.close()
    return result

def retrieve_featured_comp():
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute("SELECT * from competitions ORDER BY RAND() LIMIT 1")
    result = cursor.fetchall()
    db.close()
    return result

def retrieve_ongoing_comps():
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    today = time.strftime('%Y-%m-%d')
    cursor.execute("SELECT * from competitions where date >= '{}'".format(today))
    result = cursor.fetchall()
    db.close()
    return result

def retrieve_completed_comps():
    '''This function is wet'''
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    today = time.strftime('%Y-%m-%d')
    cursor.execute("SELECT * from competitions where date <= '{}'".format(today))
    result = cursor.fetchall()
    db.close()
    return result

def competition_details(contest_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute("SELECT * from competitions where id={}".format(contest_id))
    result = cursor.fetchall()
    db.close()
    return result

def competition_options(contest_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute("SELECT * from comp_option where comp_id={}".format(contest_id))
    result = cursor.fetchall()
    db.close()
    return result


def one_competition_option(comp_option_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute("SELECT * from comp_option where id={}".format(contest_id))
    result = cursor.fetchall()
    db.close()
    return result

if __name__ == '__main__':
    application.run(host='0.0.0.0')
