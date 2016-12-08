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
from datetime import date


application = Flask(__name__)
application.config.from_pyfile('config.py')

# OAuth and Facebook object for social login
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
    # Main page
    session['previous_page'] = '/'
    reco_comps = retrieve_reco_comps()
    featured_comp = retrieve_featured_comp()
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
        next=request.args.get('referrer'), _external=True))

@application.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    # This is the route that gets hit after a successful login
    # The code below is a bit convoluted but it figures out how to redirect
    # Users back to the page they were at before they were asked to log in
    # And then removes that from the session so that you don't get stuck
    # In a weird redirect loop
    next_url = session.get('previous_page') or request.args.get('referrer') or url_for('index')
    if next_url == 'view':
        session.pop('previous_page')
        next_url = url_for('view', contest_id=session.pop('contest_id'))
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)

    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')

    data = facebook.get('/me').data
    # There's a lot more data we could be storing but we're privacy positive
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
    # This is the pattern for login required pages, could probably be better
    # done with a decorator
    if not session.get('logged_in'):
        session['previous_page'] = '/manage'
        return redirect(url_for('login_required'))
    return render_template('manage.html')


@application.route('/browse')
def browse():
    ongoing = retrieve_ongoing_comps()
    completed = retrieve_completed_comps()
    return render_template('browse.html', ongoing=ongoing, completed=completed)


@application.route('/create',methods=['GET','POST'])
def create():
    # This function is a bit rough around the edges, Goutam wrote it before
    # We totally figured out some of the patterns we wanted to use
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
            for f in cform.options:
                file_name = f.image_url
                cur = f.data

                files = request.files[file_name.name]
                location = os.path.join(application.config['UPLOAD_FOLDER'],files.filename)
                location_indb = "images/"+files.filename

                create_option(str(cur["description"]),location_indb,comp_id)
                files.save(location)

            return redirect('/view/'+str(comp_id))
    return render_template('create.html',form = cform)


@application.route('/view/<contest_id>')
def view(contest_id):
    details = competition_details(contest_id)
    options = competition_options(contest_id)
    # Logic for whether a campaign is completed or not happens in the template
    completed = details[0][4] < date.today()
    return render_template('view.html', details=details, options=options, completed=completed)

@application.route('/view/')
def view_generic():
    return render_template('view.html')


@application.route('/order/', methods=['POST', 'GET'])
def order():
    # Orders have a fairly complex route. When someone hits vote it sends a 
    # POST to this method which needs to make sure they're logged in, otherwise
    # It sends them to log in and returns them back to the campaign

    if request.method == 'GET':
        return redirect(url_for('browse'))
    if not session.get('logged_in'):
        session['previous_page'] = 'view'
        session['contest_id'] = request.referrer.split('/')[-1]
        return redirect(url_for('login_required'))

    option_id = request.form.get('group1')
    if not option_id:
        return redirect(url_for('browse'))
    return redirect(url_for('order_with_id', option_id=option_id))


@application.route('/order_with_id')
def order_without_id():
    return redirect(url_for('browse'))


@application.route('/order_with_id/<option_id>', methods=['GET', 'POST'])
def order_with_id(option_id):
    # Assuming they are logged in, this route collects their payment details
    if option_id == 1:
        return redirect(url_for('browse'))
    option_details = one_competition_option(option_id)[0]
    details = competition_details(option_details[3])
    form = forms.OrderForm(competition_id=option_details[3],
                           option_id=option_details[0])
    return render_template('order.html', option_details=option_details, 
                           competition_details=details, form=form)

@application.route('/place_order', methods=['POST'])
def place_order():
    # Once they enter payment details, the form is posted to this method
    # Which collects the details from the form, puts those in the orders DB
    # Then increments the vote totals
    name = request.form['name']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    zip_code = request.form['zip_code']
    billing_name = request.form['zip_code']
    credit_card_number = request.form['credit_card_number']
    competition_id = request.form['competition_id']
    option_id = request.form['option_id']

    add_order(name, address, city, state, zip_code,
              billing_name, credit_card_number,
              competition_id, option_id)

    add_vote(option_id)

    option_votes = get_total_votes_for_id(option_id)
    competition_votes = get_total_votes_for_competition(competition_id)
    competition_end_date = get_competition_end_date(competition_id)


    return render_template('success.html', option_votes=option_votes, total_votes=competition_votes, competition_end_date=competition_end_date)


######################################
# Everything down here should be in a models.py file, but we were never able to
# Find the pattern to get config variables from the application into that file
# So we just put models.py down here
# We also never spent the time to create a proper data access layer and instead
# Just made a new function for every piece of data we needed
# An ORM would certainly have been a better idea, but there was some...
# ...disagreement in the group about that.
# Forgive the code below.

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
    cursor.execute("SELECT * from comp_option where id={}".format(comp_option_id))
    result = cursor.fetchall()
    db.close()
    return result


def add_order(name, address, city, state, zip_code,
              billing_name, credit_card_number,
              competition_id, option_id):

    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    print( (name, address, city, state, zip_code,
                   billing_name, credit_card_number,
                   competition_id, option_id) )
    cursor = db.cursor()
    flag = 1
    while flag ==1:
        try:
            id =  int(time.time()) + int(random.random())
            cursor.execute("""INSERT INTO orders (id, name, address, city, state, zip_code,
                   billing_name, credit_card_number, competition_id, option_id)
                   VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                  (id,name, address, city, state, zip_code,
                   billing_name, credit_card_number,
                   competition_id, option_id))
            flag = 0
        except pymysql.IntegrityError as e:
            if 'PRIMARY' in e.message:
                continue

    db.commit()
    db.close()

def add_vote(option_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute('UPDATE comp_option SET votes = votes + 1 WHERE id = %s', (option_id,))
    db.commit()
    db.close()


def get_total_votes_for_id(option_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute('SELECT votes FROM comp_option WHERE id = %s', (option_id,))
    result = cursor.fetchall()
    db.close()
    return result[0][0]


def get_total_votes_for_competition(competition_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute('SELECT sum(votes) FROM comp_option WHERE comp_id = %s', (competition_id,))
    result = cursor.fetchall()
    db.close()
    return result[0][0]
    
def get_competition_end_date(competition_id):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    cursor.execute('SELECT date from competitions WHERE id = {}'.format(competition_id))
    result = cursor.fetchall()
    db.close()
    return result[0][0]  



if __name__ == '__main__':
    application.run(host='0.0.0.0')
