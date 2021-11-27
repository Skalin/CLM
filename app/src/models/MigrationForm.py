from flask import flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired, URL, Length
import requests
from app.src.models.LKODUser import LKODUser
from app.src.models.Migrator import Migrator, CONSTANT_JSON_VALID, CONSTANT_JSON_INVALID


class MigrationForm(FlaskForm):
    user = None
    migrator = None
    datasets = HiddenField('Seznam datových sad', validators=[DataRequired()])
    variant = SelectField('Varianta', validators=[DataRequired()], choices=[('all', 'Vše'), ('valid', 'Pouze validní'),('invalid', 'Pouze nevalidní')], default=0)
    migration_form_submit = SubmitField('Spustit migraci')

    def process_data(self):
        migration_status = False
        if self.check_servers() is False or self.login() is False:
            return migration_status
        print('still migrating')
        self.migrator = Migrator(self.lkod_server_url.data, self.ckan_server_url.data, self.ckan_api_key.data, self.company_vatin.data, self.variant.data)
        migration_status = self.migrator.migrate()
        session['datasets'] = self.get_migration_datasets()
        session['migrator'] = {'lkod': {'url': self.lkod_server_url.data}, 'ckan': {'url': self.ckan_server_url.data, 'api_key': self.ckan_api_key.data}, 'vatin': self.company_vatin.data, 'variant': self.variant.data}
        return migration_status

    def get_migration_datasets(self):
        return self.migrator.datasets if self.migrator is not None else []

    def get_status_translation(self, status):
        if status == CONSTANT_JSON_VALID:
            return 'Zpracováno'
        elif status == CONSTANT_JSON_INVALID:
            return 'Ke zpracování'

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

    def check_servers(self):
        if self.check_server(self.ckan_server_url.data) is False:
            print("error in ckan")
            flash("CKAN is not available!")
            return False

        if self.check_server(self.lkod_server_url.data) is False:
            print("error in lkod")
            flash("LKOD is not available!")
            return False

        if self.check_server(self.lkod_server_url.data+'/health') is False:
            print("error in lkod")
            flash("LKOD API is not available!")
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

