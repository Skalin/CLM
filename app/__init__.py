from flask import Flask
from flask_bootstrap import Bootstrap
from app.Config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Bootstrap(app)

    from app.src.controllers.site import site
    app.register_blueprint(site, url_prefix='/')
    return app


