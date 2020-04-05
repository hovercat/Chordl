import datetime

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

    def __init__(self, password, **kwargs):
        self.set_password(password)
        super(User, self).__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, trial_password):
        return check_password_hash(self.password_hash, trial_password)


class Choir(db.Model):
    __tablename__ = "Choir"

    cid = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)
    name = db.Column(db.String(200),
                     nullable=False)


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

    user = db.relationship("User", backref="choirs")
    choir = db.relationship("Choir", backref="users")


User.choirs = association_proxy("User_Choir", "cid")
Choir.users = association_proxy("User_Choir", "uid")


class ChoirSection(db.Model):
    __tablename__ = "ChoirSection"

    csid = db.Column(db.Integer,
                     primary_key=True,
                     autoincrement=True)
    cid = db.Column(db.Integer,
                    db.ForeignKey(Choir.cid))
    name = db.Column(db.String(20),
                     nullable=False)

    parent = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("csid", "cid"),
        db.ForeignKeyConstraint(["parent"], ["ChoirSection.csid"])
    )


class User_ChoirSection(db.Model):
    __tablename__ = "User_ChoirSection"

    uid = db.Column(db.Integer,
                    db.ForeignKey(User.uid),
                    primary_key=True)
    csid = db.Column(db.Integer,
                     primary_key=True)
    cid = db.Column(db.Integer,
                    primary_key=True)

    __table_args__ = (
        db.UniqueConstraint("csid", "cid"),
        db.ForeignKeyConstraint(["cid", "csid", ], ["ChoirSection.cid", "ChoirSection.csid"])
    )

    user = db.relationship("User", backref="choir_sections")
    choir_section = db.relationship("ChoirSection", backref="users")


User.choir_sections = association_proxy("User_ChoirSection", ["csid", "cid"])
ChoirSection.users = association_proxy("User_ChoirSection", "uid")


class Rehearsal(db.Model):
    __tablename__ = "Rehearsal"

    rid = db.Column(db.Integer,
                    primary_key=True)
    cid = db.Column(db.Integer,
                    db.ForeignKey(Choir.cid))
    uid = db.Column(db.Integer,
                    db.ForeignKey(User.uid))  # which user created the rehearsal

    start_date = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.datetime.now())
    end_date = db.Column(db.DateTime,
                         nullable=False)

    __table_args__ = ()

class Song(db.Model):
    __tablename__ = "Song"

    sid = db.Column(db.Integer,
                    primary_key=True)
    title = db.Column(db.String(50),
                      nullable=False)

    cid = db.Column(db.Integer,
                    db.ForeignKey(Choir.cid))  # which choir the song belongs to
    uid = db.Column(db.Integer,
                    db.ForeignKey(User.uid))  # which user created the song

    synchronization_files = db.relationship("Song_File",
                                  back_populates="song",
                                  primaryjoin="and_(Song.sid==Song_File.sid, "
                                              "Song_File.type=='SYNCHRONIZATION')")
    sheetmusic_files = db.relationship("Song_File",
                                  back_populates="song",
                                  primaryjoin="and_(Song.sid==Song_File.sid, "
                                              "Song_File.type=='SHEETMUSIC')")
    musescore_files = db.relationship("Song_File",
                                  back_populates="song",
                                  primaryjoin="and_(Song.sid==Song_File.sid, "
                                              "Song_File.type=='MUSESCORE')")

class File(db.Model):
    __tablename__ = "File"

    fid = db.Column(db.Integer,
                    primary_key=True)
    uid = db.Column(db.Integer,
                    db.ForeignKey(User.uid),
                    nullable=False)
    file_blob = db.Column(LONGBLOB)

class Song_File(db.Model):
    __tablename__ = "Song_File"

    sid = db.Column(db.Integer,
                    db.ForeignKey(Song.sid),
                    primary_key=True)
    fid = db.Column(db.Integer,
                    db.ForeignKey(File.fid),
                    primary_key=True)

    csid = db.Column(db.Integer,
                     db.ForeignKey(ChoirSection.csid),
                     nullable=True)
    type = db.Column(db.String(50),
                     nullable=False)

    comment = db.Column(db.String(512),
                        nullable=True)

    song = db.relationship("Song")
    file = db.relationship("File")


class Rehearsal_Song(db.Model):
    __tablename__ = "Rehearsal_Song"

    rid = db.Column(db.Integer,
                    db.ForeignKey(Rehearsal.rid),
                    primary_key=True)
    sid = db.Column(db.Integer,
                    db.ForeignKey(Song.sid),
                    primary_key=True)

    rehearsal = db.relationship("Rehearsal", backref="songs")
    song = db.relationship("Song", backref="rehearsal")


Rehearsal.songs = association_proxy("Rehearsal_Song", "sid")
Song.rehearsal = association_proxy("Rehearsal_Song", "rid")
