from flask import flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, HiddenField, BooleanField
from wtforms.validators import DataRequired, URL, Length
import requests
from app.src.models.LKODUser import LKODUser
from app.src.models.Migrator import Migrator, CONSTANT_JSON_VALID, CONSTANT_JSON_INVALID, FREQUENCY_MAP


class MigrationForm(FlaskForm):
    user = None
    migrator = None
    datasets = HiddenField('Seznam datových sad', validators=[DataRequired()])
    variant = SelectField('Varianta', validators=[DataRequired()], choices=[('all', 'Vše'), ('valid', 'Pouze validní'),('invalid', 'Pouze nevalidní')], default=0)
    prefill_frequency_check = BooleanField('Předvyplnit frekvenci',default=0)
    prefill_frequency = SelectField('Hodnota frekvence', validators=[DataRequired()], choices=[(0, 'Žádná'), ('irreg', 'Občasná aktualizace'),('never', 'Nikdy neaktualizováno')], default=0)
    prefill_ruian_check = BooleanField('Předvyplnit frekvenci',default=0)
    prefill_ruian = SelectField('Hodnota RÚIAN', validators=[DataRequired()], choices=[(0, 'Žádná'), ('1', 'Celá ČR')], default=0)
    prefill_license_check = BooleanField('Předvyplnit frekvenci',default=0)
    prefill_license = SelectField('Licence', validators=[DataRequired()], choices=[('none', 'Žádná'), ('cc4', 'CC4')], default=0)
    migration_form_submit = SubmitField('Spustit migraci')

    def process_data(self):
        print(session)
        if 'migrator' not in session or 'lkod' not in session['migrator'] or 'ckan' not in session['migrator'] or 'vatin' not in session['migrator']:
            return False
        lkod = session['migrator']['lkod']
        ckan = session['migrator']['ckan']
        vatin = session['migrator']['vatin']
        self.migrator = Migrator(lkod['url'], ckan['url'], ckan['api_key'], vatin, self.variant.data, self.datasets.data)
        return self.migrator.migrate(self)

    def get_migration_datasets(self):
        return self.migrator.datasets if self.migrator is not None else []

    def get_status_translation(self, status):
        if status == CONSTANT_JSON_VALID:
            return 'Zpracováno'
        elif status == CONSTANT_JSON_INVALID:
            return 'Ke zpracování'

