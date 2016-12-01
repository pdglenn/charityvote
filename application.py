from application import forms, models
from flask import Flask, render_template, request
import os
UPLOAD_FOLDER = 'images/'
application = Flask(__name__)
application.debug = True
application.secret_key = ('you_wont_guess')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
            comp_id = models.create_competition(title,amount,date)
            for f in cform.options:
                file_name = f.image_url
                print ("OK" + str(file_name.name))
                files = request.files[file_name.name]
                image_url = os.path.join(application.config['UPLOAD_FOLDER'],files.filename)
                models.create_option(f.description.data,image_url,id)
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

if __name__ == '__main__':
    application.run(host='0.0.0.0')