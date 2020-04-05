from flask import Flask
from flask_assets import Environment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session  # TODO No conda install of flask-session, used pip3!
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
login_manager = LoginManager()
sess = Session()
assets = Environment()
csrf = CSRFProtect()
#redis = FlaskRedis()
#celery = Celery()


def create_app():
    """Construct the core of webserver"""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Init plugins
    db.init_app(app)
    login_manager.init_app(app)
    sess.init_app(app)
    assets.init_app(app)
    csrf.init_app(app)

    #redis.init_app(app)
    # Celery
    #celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    #celery.conf.update(app.config)

    with app.app_context():
        from application.index import index_routes
        from application.loggedin import loggedin_routes
        from application.usermanagement import usermanagement_routes

        app.register_blueprint(index_routes.index_blueprint)
        #app.register_blueprint(loggedin_routes.loggedin_blueprint)
        #app.register_blueprint(usermanagement_routes.usermanagement_blueprint))

        # Create tables for our models
        db.create_all()

        return app
