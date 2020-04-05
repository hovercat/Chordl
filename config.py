from os import environ
#import redis

class Config:
    """Set Flask configuration vars from .env file."""

    DEBUG = True

    # General
    TESTING = environ.get('TESTING')
    FLASK_DEBUG = environ.get('FLASK_DEBUG')
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_ENV = environ.get('FLASK_ENV')
    FLASK_APP = environ.get('FLASK_APP')

    # Session
    SESSION_TYPE = environ.get('SESSION_TYPE')
#    SESSION_REDIS = redis.from_url(environ.get("SESSION_REDIS"))

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')

    # Message-Broker
    #CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL')
    #CELERY_RESULT_BACKEND = environ.get('CELERY_RESULT_BACKEND')

    # Assets and CSS
    LESS_BIN = '/usr/bin/lessc'
    SASS_BIN = '/usr/bin/sassc'
    ASSETS_DEBUG = True
    ASSETS_AUTO_BUILD = True
