from flask import Blueprint, render_template, redirect, url_for, request
from app.src.models.LoginForm import LoginForm

template_path = 'site/'

site = Blueprint('site', __name__)


@site.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for("site.index"))

    return render_template(template_path+'index.html', form=form)


@site.route('/installation')
def installation():
    return render_template(template_path+'installation.html')
