import os
from dotenv import load_dotenv


class Config(object):
    load_dotenv()

    SECRET_KEY = os.getenv('SECRET_KEY') or 'secret-key'
    ENV = os.getenv("ENV") or "DEVELOPMENT"
    DEBUG = os.getenv("DEBUG") or False
    if DEBUG is False:
        TEMPLATES_AUTO_RELOAD = os.getenv('TEMPLATES_AUTO_RELOAD') or False
