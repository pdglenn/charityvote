from application import forms
from flask import Flask, render_template, request
import os
import uuid
import pymysql
import random,time


application = Flask(__name__)
application.debug = True
application.secret_key = ('you_wont_guess')

application.config.from_pyfile('config.py', silent=True)


@application.route('/')
def index():
    return render_template('index.html')


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
                cur = f.data
                print (cur)
                print ("OK" + str(file_name.name))
                files = request.files[file_name.name]
                location = os.path.join(application.config['UPLOAD_FOLDER'],files.filename)
                print ("trial and error "+ str(cur["description"]))
                create_option(f.description,location,comp_id)
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

def create_competition (title,amount,expiry_date):
    db = pymysql.connect(host=host,user = username,passwd=password,db="charityvote",port=port)
    cursor = db.cursor()
    print ("Creating Competition")
    flag = 1
    while flag == 1:
        try:
            id =  int(time.time()) + int(random.random())
            cursor.execute("insert into competitions values (%s,%s,%s,%s) ",(id,title,amount,expiry_date))
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
            cursor.execute("insert into comp_option values (%s,%s,%s,%s) ",(id,description,image_url,comp_id))
            flag = 0
        except pymysql.IntegrityError as e:
            if 'PRIMARY' in e.message:
                continue
                
    db.commit()

if __name__ == '__main__':
    application.run(host='0.0.0.0')