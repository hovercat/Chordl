from sqlalchemy.ext.associationproxy import association_proxy

from application import utils
from . import db

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'User'

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
