import datetime
import unittest

from flask import Flask
from flask_assets import Environment
from flask_login import LoginManager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask import current_app as app
from redis import Redis

from application import db
from application.models import User, Choir, User_Choir, Rehearsal, Song, ChoirSection, User_ChoirSection, \
    SynchronizationFile, Song_ChoirSection, SheetmusicFile


class ApiTests(unittest.TestCase):

    def db_stuff(self):
        # Create tables for our models
        db.drop_all()
        db.session.commit()
        db.create_all()
        db.session.commit()

        choir = Choir(name="TU Wien Chor")

        db.session.add(choir)

        alle = ChoirSection(name="Alle")

        sopran = ChoirSection(name="Sopran")
        alt = ChoirSection(name="Alt")
        tenor = ChoirSection(name="Tenor")
        bass = ChoirSection(name="Bass")

        sopran1 = ChoirSection(name="Sopran1")
        sopran2 = ChoirSection(name="Sopran2")
        mezzo = ChoirSection(name="Mezzo")
        alt1 = ChoirSection(name="Alt1")
        alt2 = ChoirSection(name="Alt2")
        tenor1 = ChoirSection(name="Tenor1")
        tenor2 = ChoirSection(name="Tenor2")
        bass1 = ChoirSection(name="Bass1")
        bass2 = ChoirSection(name="Bass2")

        choir.choir_sections.extend(
            [alle,
             sopran, alt, tenor, bass,
             sopran1, sopran2, mezzo, alt1, alt2, tenor1, tenor2, bass1, bass2]
        )

        db.session.flush()

        u0 = User("password", email="andi@ipp.at", first_name="Andi", last_name="Ipp")
        u1 = User("password", email="kanon@gnaore.at", first_name="Kanon", last_name="Gnaore")
        u2 = User("password", email="aschl@posteo.at", first_name="Ulrich", last_name="Aschl")

        db.session.add_all([u0, u1, u2])

        db.session.flush()

        tenor_u0 = User_ChoirSection(user=u0, choir_section=tenor)
        # tenor_u0.user = u0
        # tenor_u0.choir_section = tenor
        tenor1_u0 = User_ChoirSection()
        tenor1_u0.user = u0
        tenor1_u0.choir_section = tenor1
        u0.user_choirsections.extend([tenor_u0, tenor1_u0])

        tenor_u1 = User_ChoirSection()
        tenor_u1.user = u1
        tenor_u1.choir_section = tenor
        tenor2_u1 = User_ChoirSection()
        tenor2_u1.user = u1
        tenor2_u1.choir_section = tenor2
        u1.user_choirsections.extend([tenor_u1, tenor2_u1])

        bass_u2 = User_ChoirSection()
        bass_u2.user = u2
        bass_u2.choir_section = bass
        bass2_u2 = User_ChoirSection()
        bass2_u2.user = u2
        bass2_u2.choir_section = bass2
        u2.user_choirsections.extend([bass_u2, bass2_u2])

        #   db.session.add(u0)
        #   db.session.add(u1)
        #   db.session.add(u2)

        choiruser0 = User_Choir(is_admin=True)
        choiruser0.user = u0
        choiruser0.choir = choir

        choiruser1 = User_Choir(is_admin=False)
        choiruser1.user = u1
        choiruser1.choir = choir

        choiruser2 = User_Choir(is_admin=False)
        choiruser2.user = u2
        choiruser2.choir = choir

        choir.users.extend([choiruser0, choiruser1, choiruser2])

        db.session.flush()

        rehearsal = Rehearsal(start_date=datetime.datetime.now(), end_date=datetime.datetime.now())
        rehearsal.choir = choir

        song_21guns = Song(name="21 Guns")
        song_21guns.choir_sections.append(
            Song_ChoirSection(song=song_21guns, choir_section=alle)
        )

        sync_files = [
            SynchronizationFile(song=song_21guns, choir_section=alle,
                                file_path="resources/somenights/alle.ogg"),
            SynchronizationFile(song=song_21guns, choir_section=alt,
                                file_path="resources/somenights/alt.ogg"),
            SynchronizationFile(song=song_21guns, choir_section=bass1,
                                file_path="resources/somenights/bass1.ogg"),
            SynchronizationFile(song=song_21guns, choir_section=bass2,
                                file_path="resources/somenights/bass2.ogg"),
            SynchronizationFile(song=song_21guns, choir_section=None,
                                file_path="resources/somenights/solo.ogg"),
            SynchronizationFile(song=song_21guns, choir_section=sopran1,
                                file_path="resources/somenights/sopran1.ogg"),
            SynchronizationFile(song=song_21guns, choir_section=sopran2,
                                file_path="resources/somenights/sopran2.ogg"),
            SynchronizationFile(song=song_21guns, choir_section=tenor,
                                file_path="resources/somenights/tenor.ogg")
        ]
        song_21guns.sync_files.extend(sync_files)

        sheet_music = [
            SheetmusicFile(song=song_21guns, choir_section=alle,
                           file_path="resources/somenights/sheetmusic.pdf")
        ]
        song_21guns.sheetmusic_files.extend(sheet_music)

        db.session.add(song_21guns)

        db.session.commit()

        pass

    def setUp(self):
        app = Flask(__name__,
                    static_url_path='/static',
                    static_folder='../static'
                    )
        #app.config['SESSION_REDIS'] = "redis://127.0.0.1:6379"
        #app.config['SESSION_TYPE'] = "redis"
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://test:test@127.0.0.1/chordl_test'
        app.config['SECRET_KEY'] = 'dev'

        db = SQLAlchemy()
        login_manager = LoginManager()
        sess = Session()
        assets = Environment()
        csrf = CSRFProtect()
        #redis = Redis()

        # Init plugins
        db.init_app(app)
        # login_manager.init_app(app)
        sess.init_app(app)
        assets.init_app(app)
        csrf.init_app(app)

        with app.app_context():
            from application.api import api_routes

            app.register_blueprint(api_routes.api_bp)

            self.app = app
            self.db_stuff()

    def tearDown(self):
        pass

    def test_songdownload(self):
        with self.app.test_client() as client:
            sf = SynchronizationFile.query.first()

            response = client.get("/api/syncfile/{id}".format(
                id=sf.sync_id
            ))


        self.assertEqual(sf.file, response.data)


if __name__ == '__main__':
    unittest.main()
