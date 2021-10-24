from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    ckan_server_url = StringField('CKAN Server URL', validators=[DataRequired()])
    ckan_api_key = StringField('CKAN API Key', validators=[DataRequired()])
    lkod_server_url = StringField('LKOD Server URL', validators=[DataRequired()])
    company_vatin = StringField('VATIN', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    variant = SelectField('Variant', validators=[DataRequired()], choices=['All', 'Only valid', 'Only invalid'], default=0)
    submit = SubmitField('Migrate')
