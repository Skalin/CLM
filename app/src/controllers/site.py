import sys

from flask import Blueprint, render_template, request, flash, session, redirect, url_for, Response
import requests
import json
from app.src.models.LoginForm import LoginForm
from app.src.models.Migrator import Migrator
import urllib.parse

template_path = 'site/'

site = Blueprint('site', __name__)


@site.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        if not form.migrate():
            flash("Form migration was not successful!")
            return render_template(template_path + 'index.html', form=form)

    return render_template(template_path + 'index.html', form=form)


@site.route('/login', methods=['GET', 'POST'])
def login():
    ...


@site.route('/download/<dataset>')
def download(dataset):
    if 'migrator' not in session:
        flash('Please reinsert data into form, to be able to submit data')
        redirect(url_for('site.login'))

    migrator = session['migrator']
    migrator_cls = Migrator(migrator['lkod']['url'], migrator['ckan']['url'], migrator['ckan']['api_key'],
                            migrator['vatin'], migrator['variant'])
    form_data = json.dumps(migrator_cls.get_new_dataset(dataset), separators=(',', ':'))
    return Response(
        form_data,
        mimetype="application/json",
        headers={"Content-disposition":
                     "attachment; filename=" + dataset + ".json"})


@site.route('/migrate/<dataset>', methods=['GET'])
def migrate(dataset):
    print(dataset)
    if 'lkod' not in session:
        flash('Please log in again to migrate data')
        redirect(url_for('site.login'))

    if 'migrator' not in session:
        flash('Please reinsert data into form, to be able to submit data')
        redirect(url_for('site.login'))

    migrator = session['migrator']
    lkod = session['lkod']
    migrator_cls = Migrator(migrator['lkod']['url'], migrator['ckan']['url'], migrator['ckan']['api_key'],
                            migrator['vatin'], migrator['variant'])
    form_data = json.dumps(migrator_cls.get_new_dataset(dataset), separators=(',', ':'))
    response = requests.post(lkod['url'] + '/datasets', data={'organizationId': 1},
                             headers={'Authorization': 'Bearer ' + lkod['accessToken']}).json()
    if 'id' in response:
        session_response = requests.post(lkod['url'] + '/sessions', data={'datasetId': response['id']},
                                         headers={'Authorization': 'Bearer ' + lkod['accessToken']}).json()
        print(session_response)
        url = 'https://data.gov.cz/formul%C3%A1%C5%99/registrace-datov%C3%A9-sady'
        params = urllib.parse.urlencode({'returnUrl': migrator['lkod']['url'] + '/form-data'})
        return redirect(url + '?' + params, code=301)
    return redirect(url_for('site.index'))


@site.route('/installation')
def installation():
    return render_template(template_path + 'installation.html')
