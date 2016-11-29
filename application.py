from application import forms, models
from flask import Flask, render_template, request
UPLOAD_FOLDER = '/path/to/the/uploads'
application = Flask(__name__)
application.debug = True
application.secret_key = ('you_wont_guess')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
        if 'submit_competition' in request.form :
            comp =[]

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