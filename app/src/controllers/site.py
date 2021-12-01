import sys
import webbrowser

from flask import Blueprint, render_template, request, flash, session, redirect, url_for, Response
import requests
import json
from app.src.models.LoginForm import LoginForm
from app.src.models.MigrationForm import MigrationForm
from app.src.models.Migrator import Migrator
from flask_wtf import FlaskForm
import urllib.parse

template_path = 'site/'

site = Blueprint('site', __name__)


@site.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    migration_form = MigrationForm()
    if request.method == 'POST' and form.login_form_submit.data and form.validate_on_submit():
        if form.process_data() is not False:
            return render_template(template_path + 'index.html', form=form, migration_form=migration_form)

    print(migration_form.validate_on_submit())
    if request.method == 'POST' and migration_form.migration_form_submit.data and migration_form.validate_on_submit():
        if migration_form.process_data() is not False:
            flash("Migrace provedena úspěšně. Prosíme ověřte datové sady ve svém lokálním katalogu.")

    return render_template(template_path + 'index.html', form=form)

@site.route('/authors', methods=['GET'])
def authors():
    ...

@site.route('/logout', methods=['GET'])
def logout():
    if 'lkod' in session:
        session['lkod'] = None
    if 'migrator' in session:
        session['migrator'] = None
    if 'datasets' in session:
        session['datasets'] = None

    return redirect(url_for('site.index'))


@site.route('/validate/<dataset>', methods=['GET'])
def validate(dataset):
    if 'lkod' not in session and 'accessToken' not in session['lkod']:
        flash('Please log in again to migrate data')
        redirect(url_for('site.index'))

    if 'migrator' not in session:
        flash('Please reinsert data into form, to be able to submit data')
        redirect(url_for('site.index'))

    migrator = session['migrator']
    migrator_cls = Migrator(migrator['lkod']['url'], migrator['ckan']['url'], migrator['ckan']['api_key'],
                            migrator['vatin'])
    form_data = migrator_cls.get_new_dataset_object(dataset)
    migrator_cls.json_validator.validate_json(form_data, dataset)
    return migrator_cls.json_validator.errors[dataset] if len(migrator_cls.json_validator.errors) else 'Nenalezeny žádné chyby v datové sadě'



    response = requests.post(lkod['url'] + '/datasets', data={'organizationId': 1},
                             headers={'Authorization': 'Bearer ' + lkod['accessToken']}).json()
    print(response)
    if 'id' in response:
        dataset_id = response['id']
        session_response = requests.post(lkod['url'] + '/sessions', data={'datasetId': dataset_id},
                                         headers={'Authorization': 'Bearer ' + lkod['accessToken']}).json()
        session_id = session_response['id']
        user_data = {'accessToken': lkod['accessToken'], 'sessionId': session_id, 'datasetId': dataset_id}

        print(form_data)
        print(
            json.dumps(
                {
                    "@context": "https://ofn.gov.cz/rozhraní-katalogů-otevřených-dat/2021-01-11/kontexty/rozhraní-katalogů-otevřených-dat.jsonld",
                    "typ": "Datová+sada", "název": {"cs": "test+datová+sada přes API"}, "popis": {"cs": "popisek"},
                    "prvek_rúian": [],
                    "geografické_území": [], "prostorové_pokrytí": [],
                    "klíčové_slovo": {"cs": ["slovo+A", "slovo+B"], "en": []},
                    "periodicita_aktualizace": "http://publications.europa.eu/resource/authority/frequency/MONTHLY",
                    "téma": ["http://publications.europa.eu/resource/authority/data-theme/OP_DATPRO"],
                    "koncept_euroVoc": [],
                    "kontaktní_bod": {}, "distribuce": [{"typ": "Distribuce",
                                                         "podmínky_užití": {"typ": "Specifikace+podmínek+užití",
                                                                            "autorské_dílo": "https://data.gov.cz/podmínky-užití/neobsahuje-autorská-díla/",
                                                                            "databáze_jako_autorské_dílo": "https://data.gov.cz/podmínky-užití/není-autorskoprávně-chráněnou-databází/",
                                                                            "databáze_chráněná_zvláštními_právy": "https://data.gov.cz/podmínky-užití/není-chráněna-zvláštním-právem-pořizovatele-databáze/",
                                                                            "osobní_údaje": "https://data.gov.cz/podmínky-užití/neobsahuje-osobní-údaje/"},
                                                         "soubor_ke_stažení": "https://www.seznam.cz",
                                                         "přístupové_url": "https://www.seznam.cz",
                                                         "typ_média": "http://www.iana.org/assignments/media-types/text/csv",
                                                         "formát": "http://publications.europa.eu/resource/authority/file-type/CSV"}]}
            )
        )
        form_response = requests.post(lkod['url'] + '/form-data',
                                      headers={'ContentType': 'application/x-www-form-urlencoded'},
                                      json={'userData': json.dumps(user_data), 'formData': form_data})
        # form_response = requests.post(lkod['url']+'/form-data', headers={'ContentType': 'application/x-www-form-urlencoded'}, json={'userData': json.dumps(user_data), 'formData': json.dumps(
        #    {
        #                 "@context": "https://ofn.gov.cz/rozhraní-katalogů-otevřených-dat/2021-01-11/kontexty/rozhraní-katalogů-otevřených-dat.jsonld",
        #                 "typ": "Datová+sada", "název": {"cs": "test+datová+sada přes API"}, "popis": {"cs": "popisek"}, "prvek_rúian": [],
        #                 "geografické_území": [], "prostorové_pokrytí": [],
        #                 "klíčové_slovo": {"cs": ["slovo+A", "slovo+B"], "en": []},
        #                 "periodicita_aktualizace": "http://publications.europa.eu/resource/authority/frequency/MONTHLY",
        #                 "téma": ["http://publications.europa.eu/resource/authority/data-theme/OP_DATPRO"], "koncept_euroVoc": [],
        #                 "kontaktní_bod": {}, "distribuce": [{"typ": "Distribuce",
        #                                                      "podmínky_užití": {"typ": "Specifikace+podmínek+užití",
        #                                                                         "autorské_dílo": "https://data.gov.cz/podmínky-užití/neobsahuje-autorská-díla/",
        #                                                                         "databáze_jako_autorské_dílo": "https://data.gov.cz/podmínky-užití/není-autorskoprávně-chráněnou-databází/",
        #                                                                         "databáze_chráněná_zvláštními_právy": "https://data.gov.cz/podmínky-užití/není-chráněna-zvláštním-právem-pořizovatele-databáze/",
        #                                                                         "osobní_údaje": "https://data.gov.cz/podmínky-užití/neobsahuje-osobní-údaje/"},
        #                                                      "soubor_ke_stažení": "https://www.seznam.cz",
        #                                                      "přístupové_url": "https://www.seznam.cz",
        #                                                      "typ_média": "http://www.iana.org/assignments/media-types/text/csv",
        #                                                      "formát": "http://publications.europa.eu/resource/authority/file-type/CSV"}]}
        # )})

        # {
        #             "@context": "https://ofn.gov.cz/rozhraní-katalogů-otevřených-dat/2021-01-11/kontexty/rozhraní-katalogů-otevřených-dat.jsonld",
        #             "typ": "Datová+sada", "název": {"cs": "test+datová+sada přes API"}, "popis": {"cs": "popisek"}, "prvek_rúian": [],
        #             "geografické_území": [], "prostorové_pokrytí": [],
        #             "klíčové_slovo": {"cs": ["slovo+A", "slovo+B"], "en": []},
        #             "periodicita_aktualizace": "http://publications.europa.eu/resource/authority/frequency/MONTHLY",
        #             "téma": ["http://publications.europa.eu/resource/authority/data-theme/OP_DATPRO"], "koncept_euroVoc": [],
        #             "kontaktní_bod": {}, "distribuce": [{"typ": "Distribuce",
        #                                                  "podmínky_užití": {"typ": "Specifikace+podmínek+užití",
        #                                                                     "autorské_dílo": "https://data.gov.cz/podmínky-užití/neobsahuje-autorská-díla/",
        #                                                                     "databáze_jako_autorské_dílo": "https://data.gov.cz/podmínky-užití/není-autorskoprávně-chráněnou-databází/",
        #                                                                     "databáze_chráněná_zvláštními_právy": "https://data.gov.cz/podmínky-užití/není-chráněna-zvláštním-právem-pořizovatele-databáze/",
        #                                                                     "osobní_údaje": "https://data.gov.cz/podmínky-užití/neobsahuje-osobní-údaje/"},
        #                                                  "soubor_ke_stažení": "https://www.seznam.cz",
        #                                                  "přístupové_url": "https://www.seznam.cz",
        #                                                  "typ_média": "http://www.iana.org/assignments/media-types/text/csv",
        #                                                  "formát": "http://publications.europa.eu/resource/authority/file-type/CSV"}]}
        print(form_response.url)

    return redirect(url_for('site.index'))


@site.route('/installation')
def installation():
    return render_template(template_path + 'installation.html')
