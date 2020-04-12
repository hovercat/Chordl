import datetime
import os

from flask import make_response
from sqlalchemy.ext.associationproxy import association_proxy

from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.mysql import LONGBLOB


class User(UserMixin, db.Model):
    __tablename__ = "User"

    uid = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)
    email = db.Column(db.String(100),
                      unique=True,
                      nullable=False)
    first_name = db.Column(db.String(30),
                           nullable=False)
    last_name = db.Column(db.String(30),
                          nullable=False)
    password_hash = db.Column(db.String(1024),
                              nullable=False)
    inactive = db.Column(db.Boolean,
                         nullable=False,
                         default=False)
    created_on = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.datetime.now())

    recordings = db.relationship("RecordingFile", back_populates="user")
    choirs = db.relationship("User_Choir", back_populates="user")
    user_choirsections = db.relationship("User_ChoirSection", back_populates="user")
    created_rehearsals = db.relationship("Rehearsal", back_populates="creator")

    def __init__(self, password, **kwargs):
        self.set_password(password)
        super(User, self).__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, trial_password):
        return check_password_hash(self.password_hash, trial_password)

    def get_id(self):
        return self.uid

    __table_args__ = (
        {'extend_existing': True}
    )


class Choir(db.Model):
    __tablename__ = "Choir"

    cid = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)
    name = db.Column(db.String(200),
                     nullable=False)

    users = db.relationship("User_Choir", back_populates="choir")
    choir_sections = db.relationship("ChoirSection", back_populates="choir")
    rehearsals = db.relationship("Rehearsal", back_populates="choir")

    __table_args__ = (
        {'extend_existing': True}
    )


class User_Choir(db.Model):
    __tablename__ = "User_Choir"

    uid = db.Column(db.Integer,
                    db.ForeignKey(User.uid),
                    primary_key=True)
    cid = db.Column(db.Integer,
                    db.ForeignKey(Choir.cid),
                    primary_key=True)

    is_admin = db.Column(db.Boolean,
                         default=False,
                         nullable=False)

    user = db.relationship("User", back_populates="choirs")
    choir = db.relationship("Choir", back_populates="users")

    __table_args__ = (
        {'extend_existing': True}
    )


class ChoirSection(db.Model):
    __tablename__ = "ChoirSection"

    csid = db.Column(db.Integer,
                     primary_key=True,
                     autoincrement=True)
    cid = db.Column(db.Integer,
                    db.ForeignKey(Choir.cid))
    name = db.Column(db.String(20),
                     nullable=False)

    # parent = db.Column(db.Integer, nullable=True)
    sync_files = db.relationship("SynchronizationFile", back_populates="choir_section")
    sheetmusic_files = db.relationship("SheetmusicFile", back_populates="choir_section")
    musescore_files = db.relationship("MusescoreFile", back_populates="choir_section")

    choir = db.relationship("Choir", back_populates="choir_sections")
    user_choirsections = db.relationship("User_ChoirSection", back_populates="choir_section")
    # recordings = db.relationship("RecordingFile", back_populates="choir_section")

    __table_args__ = (
        db.UniqueConstraint("csid", "cid"),
        {'extend_existing': True}
        # db.ForeignKeyConstraint(["parent"], ["ChoirSection.csid"])
    )


class User_ChoirSection(db.Model):
    __tablename__ = "User_ChoirSection"

    uid = db.Column(db.Integer,
                    db.ForeignKey(User.uid),
                    primary_key=True)
    csid = db.Column(db.Integer,
                     db.ForeignKey(ChoirSection.csid),
                     primary_key=True)

    __table_args__ = (
        {'extend_existing': True}
    )

    user = db.relationship("User", back_populates="user_choirsections")
    choir_section = db.relationship("ChoirSection", back_populates="user_choirsections")


# User.choir_sections = association_proxy("User_ChoirSection", "csid")
# ChoirSection.users = association_proxy("User_ChoirSection", "uid")


class File:
    """ Base class for File tables """

    def __init__(self, file_path="/dev/null"):
        with open(file_path, 'rb') as fh:
            self.file = fh.read()
            self.name = os.path.basename(file_path)
            self.ext = os.path.splitext(os.path.basename(file_path))[-1:]

    name = db.Column(db.String(256),
                     nullable=False)
    file = db.Column(LONGBLOB,
                     nullable=False)
    ext = db.Column(db.String(32),
                    nullable=False)

    created_on = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.datetime.now())

    def provide_as_download(self):
        response = make_response(self.file)
        response.headers.set('Content-Type', 'application/octet-stream')
        response.headers.set('Content-Disposition',
                             'attachment',
                             filename='{filename}.{ext}'.format(
                                 filename = self.name,
                                 ext = self.ext)
                             )
        return response


class Song(db.Model):
    __tablename__ = "Song"

    sid = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)
    name = db.Column(db.String(256),
                     nullable=False)

    sync_files = db.relationship("SynchronizationFile", back_populates="song")
    sheetmusic_files = db.relationship("SheetmusicFile", back_populates="song")
    musescore_files = db.relationship("MusescoreFile", back_populates="song")

    choir_sections = db.relationship("Song_ChoirSection", back_populates="song")
    rehearsal_songs = db.relationship("Rehearsal_Song", back_populates="song")



    __table_args__ = (
        {'extend_existing': True}
    )


class Song_ChoirSection(db.Model):
    __tablename__ = "Song_ChoirSection"

    sid = db.Column(db.Integer,
                    db.ForeignKey(Song.sid),
                    primary_key=True)
    csid = db.Column(db.Integer,
                     db.ForeignKey(ChoirSection.csid),
                     primary_key=True)

    song = db.relationship("Song", back_populates="choir_sections")
    choir_section = db.relationship("ChoirSection") # todo add reference on other side?
    recordings = db.relationship("RecordingFile", back_populates="song_choirsection")

    __table_args__ = (
        {'extend_existing': True}
    )


class SynchronizationFile(File, db.Model):
    __tablename__ = "SynchronizationFile"

    def __init__(self, song, choir_section, file_path, *args, **kwargs):
        super().__init__(file_path, *args, **kwargs)
        self.song = song
        self.choir_section = choir_section

    sync_id = db.Column(db.Integer,
                        primary_key=True)
    sid = db.Column(db.Integer,
                    db.ForeignKey(Song.sid),
                    nullable=False)
    csid = db.Column(db.Integer,
                     db.ForeignKey(ChoirSection.cid),
                     nullable=True)

    song = db.relationship("Song", back_populates="sync_files")
    choir_section = db.relationship("ChoirSection", back_populates="sync_files")

    def provide_as_download(self):
        response = super().provide_as_download()
        response.headers.set('Content-Type', 'audio/ogg')
        return response

    __table_args__ = (
        #db.ForeignKeyConstraint(["sid", "csid"], ["Song.sid", "ChoirSection.csid"]),
        {'extend_existing': True}
    )


class SheetmusicFile(File, db.Model):
    __tablename__ = "SheetmusicFile"

    def __init__(self, song, choir_section, file_path, *args, **kwargs):
        super().__init__(file_path, *args, **kwargs)
        self.song = song
        self.choir_section = choir_section

    sheet_id = db.Column(db.Integer,
                         primary_key=True)
    sid = db.Column(db.Integer,
                    db.ForeignKey(Song.sid),
                    nullable=False)
    csid = db.Column(db.Integer,
                     db.ForeignKey(ChoirSection.cid),
                     nullable=True)

    song = db.relationship("Song", back_populates="sheetmusic_files")
    choir_section = db.relationship("ChoirSection", back_populates="sheetmusic_files")

    def provide_as_download(self):
        response = super().provide_as_download()
        response.headers.set('Content-Type', 'application/pdf')
        return response

    __table_args__ = (
        #db.ForeignKeyConstraint(["sid", "csid"], ["Song_ChoirSection.sid", "Song_ChoirSection.csid"]),
        {'extend_existing': True}
    )


class MusescoreFile(db.Model, File):
    __tablename__ = "MusescoreFile"

    musescore_id = db.Column(db.Integer,
                             primary_key=True)
    sid = db.Column(db.Integer,
                    db.ForeignKey(Song.sid),
                    nullable=False)
    csid = db.Column(db.Integer,
                     db.ForeignKey(ChoirSection.cid),
                     nullable=True)

    song = db.relationship("Song", back_populates="musescore_files")
    choir_section = db.relationship("ChoirSection", back_populates="musescore_files")

    __table_args__ = (
        db.ForeignKeyConstraint(["sid", "csid"], ["Song_ChoirSection.sid", "Song_ChoirSection.csid"]),
        {'extend_existing': True}
    )


class Rehearsal(db.Model):
    __tablename__ = "Rehearsal"

    rid = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)
    cid = db.Column(db.Integer,
                    db.ForeignKey(Choir.cid))
    uid = db.Column(db.Integer,
                    db.ForeignKey(User.uid))  # which user created the rehearsal

    created_on = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.datetime.now())
    start_date = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.datetime.now())
    end_date = db.Column(db.DateTime,
                         nullable=False)

    rehearsal_songs = db.relationship("Rehearsal_Song", back_populates="rehearsal")
    choir = db.relationship("Choir", back_populates="rehearsals")
    creator = db.relationship("User", back_populates="created_rehearsals")

    __table_args__ = (
        {'extend_existing': True}
    )


class Rehearsal_Song(db.Model):
    __tablename__ = "Rehearsal_Song"

    rid = db.Column(db.Integer,
                    db.ForeignKey(Rehearsal.rid),
                    primary_key=True)
    sid = db.Column(db.Integer,
                    db.ForeignKey(Song.sid),
                    primary_key=True)

    rehearsal = db.relationship("Rehearsal", back_populates="rehearsal_songs")
    song = db.relationship("Song", backref="rehearsals")

    recordings = db.relationship("RecordingFile", back_populates="rehearsal_song")

    __table_args__ = (
        {'extend_existing': True}
    )


class RecordingFile(db.Model, File):
    __tablename__ = "RecordingFile"

    rec_id = db.Column(db.Integer,
                       primary_key=True)
    rid = db.Column(db.Integer,
                    nullable=False)
    sid1 = db.Column(db.Integer,
                    nullable=False)

    csid = db.Column(db.Integer,
                     nullable=False)

    sid2 = db.Column(db.Integer,
                     nullable=False) # TODO THIS IS BÖSE!!!

    uid = db.Column(db.Integer,
                    db.ForeignKey(User.uid),
                    nullable=False)

    song_choirsection = db.relationship("Song_ChoirSection", back_populates="recordings")#, primaryjoin="and_(RecordingFile.rid==Rehearsal_Song.csid, RecordingFile.sid1==Song_ChoirSection.sid2")
    rehearsal_song = db.relationship("Rehearsal_Song", back_populates="recordings")#, primaryjoin="and_(RecordingFile.csid==Rehearsal_Song.csid, RecordingFile.sid2==Rehearsal_Song.sid2")
    user = db.relationship("User", back_populates="recordings")

    __table_args__ = (
        db.ForeignKeyConstraint(["rid", "sid1"], ["Rehearsal_Song.rid", "Rehearsal_Song.sid"]),
        db.ForeignKeyConstraint(["sid2", "csid", ], ["Song_ChoirSection.sid", "Song_ChoirSection.csid"]),
        {'extend_existing': True}
    )
