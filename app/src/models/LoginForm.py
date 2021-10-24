from flask import flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import requests


class LoginForm(FlaskForm):
    ckan_server_url = StringField('URL CKAN API serveru', validators=[DataRequired(), URL()])
    ckan_api_key = StringField('API klíč CKAN', validators=[DataRequired()])
    lkod_server_url = StringField('URL LKOD API serveru', validators=[DataRequired(), URL()])
    company_vatin = StringField('IČO', validators=[DataRequired()])
    username = StringField('LKOD Už. jméno', validators=[DataRequired()])
    password = PasswordField('LKOD Heslo', validators=[DataRequired()])
    variant = SelectField('Varianta', validators=[DataRequired()], choices=['Vše', 'Pouze validní', 'Pouze nevalidní'], default=0)
    submit = SubmitField('Migrovat')

    def migrate(self):
        if self.check_server(self.ckan_server_url.data) is False:
            flash("CKAN is not available!")
            redirect(url_for('site.index'))

        if self.check_server(self.lkod_server_url.data) is False:
            flash("LKOD is not available!")
            redirect(url_for('site.index'))

        if self.login() is False:
            flash("Login was not successfull! Please try other credentials!")
            redirect(url_for('site.index'))

    def login(self):
        requests.post(self.lkod_server_url.data, data={'username': self.username.data, 'password': self.password.data})

    def fetch_data(self):
        pass

    def check_server(self, url):
        try:
            requests.get(url, timeout=3)
            return True
        except (requests.ConnectionError, requests.Timeout) as exception:
            return False

