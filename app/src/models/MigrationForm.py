from flask import session
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, HiddenField, BooleanField
from wtforms.validators import DataRequired
from app.src.models.Migrator import Migrator
from app.src.components.clm.MigrationVariant import MigrationVariant

class MigrationForm(FlaskForm):
    user = None
    migrator = None
    datasets = HiddenField('Seznam datových sad', validators=[DataRequired()])
    variant = SelectField('Varianta', validators=[DataRequired()], choices=[(variant.value, variant.label()) for variant in MigrationVariant], default=MigrationVariant.ALL)
    prefill_frequency_check = BooleanField('Předvyplnit frekvenci',default=0)
    prefill_frequency = SelectField('Hodnota frekvence', validators=[DataRequired()], choices=[(0, 'Žádná'), ('irreg', 'Občasná aktualizace'),('never', 'Nikdy neaktualizováno')], default=0)
    prefill_ruian_check = BooleanField('Předvyplnit frekvenci',default=0)
    prefill_ruian = SelectField('Hodnota RÚIAN', validators=[DataRequired()], choices=[(0, 'Žádná'), ('1', 'Celá ČR')], default=0)
    prefill_license_check = BooleanField('Předvyplnit frekvenci',default=0)
    prefill_license = SelectField('Licence', validators=[DataRequired()], choices=[('none', 'Žádná'), ('cc4', 'CC4')], default=0)
    migration_form_submit = SubmitField('Spustit migraci')

    def process_data(self):
        lkod = session['migrator']['lkod']
        ckan = session['migrator']['ckan']
        vatin = session['migrator']['vatin']
        self.migrator = Migrator(lkod['url'], ckan['url'], ckan['api_key'], vatin, self.variant.data, self.datasets.data)
        return self.migrator.migrate(self)

    def get_migration_datasets(self):
        return self.migrator.datasets if self.migrator is not None else []

