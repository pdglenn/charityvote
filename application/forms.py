from flask_wtf import Form
from wtforms import StringField, FileField, HiddenField
from flask_wtf.html5 import EmailField, DateField
from wtforms.validators import DataRequired

class OptionForm(Form):
    description = StringField('description', validators=[DataRequired()])
    image_url = FileField('image',validators =[DataRequired()])

# form for creating a campaign
class CreateForm(Form):
    title = StringField('title', validators=[DataRequired()])
    comp_description = StringField('title', validators=[DataRequired()])
    amount = StringField('amount', validators=[DataRequired()])
    comp_img = FileField('image',validators =[DataRequired()])
    date = DateField('expiry', validators=[DataRequired()],format='%Y-%m-%d')
    options = FieldList(FormField(OptionForm),min_entries = 1)

# form for voting and creating an order
class OrderForm(Form):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = StringField('state',validators =[DataRequired()])
    zip_code = StringField('zip_code',validators =[DataRequired()])
    billing_name = StringField('billing_name',validators =[DataRequired()])
    credit_card_number = StringField('credit_card_number',validators =[DataRequired()])
    competition_id = HiddenField('competition_id')
    option_id = HiddenField('option_id')
