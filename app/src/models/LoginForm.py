from flask import flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, Length
import requests
from app.src.models.LKODUser import LKODUser
from app.src.models.Migrator import Migrator, CONSTANT_JSON_VALID, CONSTANT_JSON_INVALID
from app.src.models.Migration import STATUS_INIT, STATUS_READY


class LoginForm(FlaskForm):
    user = None
    migrator = None
    datasets = []
    status = STATUS_INIT
    ckan_server_url = StringField('URL CKAN API serveru', validators=[DataRequired(), URL()])
    ckan_api_key = StringField('API klíč CKAN', validators=[Length(0, 50)])
    lkod_server_url = StringField('URL LKOD API serveru', validators=[DataRequired(), URL()])
    company_vatin = StringField('IČO', validators=[DataRequired()])
    lkod_company_id = StringField('ID', validators=[DataRequired()])
    username = StringField('LKOD Už. jméno', validators=[DataRequired()])
    password = PasswordField('LKOD Heslo', validators=[DataRequired()])
    login_form_submit = SubmitField('Načíst datové sady')

    def process_data(self):
        if self.check_servers() is False or self.login() is False:
            return False
        self.migrator = Migrator(self.lkod_server_url.data, self.ckan_server_url.data, self.ckan_api_key.data, self.company_vatin.data)
        self.datasets = self.migrator.prepare_datasets()
        session['migrator'] = {'lkod': {'url': self.lkod_server_url.data, 'organizationId': self.lkod_company_id.data, 'accessToken': self.user.access_token}, 'ckan': {'url': self.ckan_server_url.data, 'api_key': self.ckan_api_key.data}, 'vatin': self.company_vatin.data,}
        self.status = STATUS_READY
        return True

    def get_migration_datasets(self):
        return self.migrator.datasets if self.migrator is not None else []

    def get_status_translation(self, status):
        if status == CONSTANT_JSON_VALID:
            return 'Plně zmigrovatelné'
        elif status == CONSTANT_JSON_INVALID:
            return 'Zmigrovatelné s úpravami'

    def logout(self):
        if 'datasets' in session:
            session['datasets'] = []
        if 'lkod' in session:
            session['lkod'] = None

    def login(self):
        if self.login_CKAN() is False:
            flash("Přihlášení k lokálnímu katalogu CKAN nebylo úspěšné.")
            return False

        if self.login_LKOD() is False:
            flash("Přihlášení k lokálnímu katalogu LKOD nebylo úspěšné.")
            return False

        session['lkod']['organization'] = self.lkod_company_id.data
        return True

    def check_servers(self):
        if self.check_server(self.ckan_server_url.data) is False:
            flash("CKAN API není dostupné. Prosím kontaktujte provozovatele svého lokálního katalogu CKAN.")
            return False

        if self.check_server(self.lkod_server_url.data) is False:
            flash("LKOD API není dostupné. Prosím kontaktujte provozovatele svého lokálního katalogu LKOD.")
            return False

        if self.check_server(self.lkod_server_url.data+'/health') is False:
            flash("LKOD API není dostupné. Prosím kontaktujte provozovatele svého lokálního katalogu LKOD.")
            return False

    def login_CKAN(self):
        return True


    def login_LKOD(self):
        self.user = LKODUser(self.lkod_server_url.data)
        return self.user.login(self.username.data, self.password.data)

    def fetch_data(self):
        pass

    def check_server(self, url):
        try:
            requests.get(url, timeout=3)
            return True
        except (requests.ConnectionError, requests.Timeout) as exception:
            return False

    def is_ready(self):
        return self.status == STATUS_READY