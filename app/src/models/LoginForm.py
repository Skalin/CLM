from flask import flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, Length, ValidationError
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
    lkod_company_id = StringField('ID', validators=[])
    username = StringField('LKOD Už. jméno', validators=[DataRequired()])
    password = PasswordField('LKOD Heslo', validators=[DataRequired()])
    login_form_submit = SubmitField('Načíst datové sady')

    def validate_ckan_server_url(self, field):
        if self.check_server(field.data) is False:
            raise ValidationError("CKAN API server není dostupný. Prosím ověřte adresu serveru, případně kontaktujte provozovatele LKOD serveru.")
        if self.login_CKAN() is False:
            raise ValidationError("Přihlášení k lokálnímu katalogu CKAN nebylo úspěšné.")

    def validate_lkod_server_url(self, field):
        if self.check_server(field.data) is False:
            raise ValidationError("LKOD server není dostupný. Prosím ověřte adresu serveru, případně kontaktujte provozovatele LKOD serveru.")
        if self.check_server(field.data+'/health') is False:
            raise ValidationError("LKOD API není dostupné. Prosím ověřte adresu serveru, případně kontaktujte provozovatele LKOD serveru.")

    def validate_company_vatin(self, field):
        if self.lkod_company_id != "":
            return
        if self.login_LKOD() is False or self.user.get_organization(field.data) is False:
            raise ValidationError("Instituce nebyla v LKOD nalezena! Vyplňte prosím ID organizace ")

    def validate_username(self, field):
        if self.login_LKOD() is False:
            raise ValidationError("Přihlášení k lokálnímu katalogu LKOD nebylo úspěšné.")

    def process_data(self):
        self.migrator = Migrator(self.lkod_server_url.data, self.ckan_server_url.data, self.ckan_api_key.data, self.company_vatin.data)
        self.user.get_organization(self.company_vatin.data)
        self.datasets = self.migrator.prepare_datasets()
        session['migrator'] = {'lkod': {'url': self.lkod_server_url.data, 'organizationId': self.user.organization_id if self.user.organization_id is not None else self.lkod_company_id, 'accessToken': self.user.access_token}, 'ckan': {'url': self.ckan_server_url.data, 'api_key': self.ckan_api_key.data}, 'vatin': self.company_vatin.data,}
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

    def login_CKAN(self):
        return True

    def login_LKOD(self):
        try:
            self.user = LKODUser(self.lkod_server_url.data)
            status = self.user.login(self.username.data, self.password.data)
            if status is True:
                session['lkod']['organization'] = self.lkod_company_id.data
            return status
        except requests.exceptions.RequestException as e:
            return False

    def check_server(self, url):
        try:
            requests.get(url, timeout=3)
            return True
        except requests.exceptions.RequestException as e:
            return False

    def is_ready(self):
        return self.status == STATUS_READY