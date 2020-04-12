from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class Login_Form(FlaskForm):
    """ Login Form."""
    email = EmailField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Login')


class Register_Form(FlaskForm):
    """ Register Form."""
    email = EmailField('Email', validators=[Email(), DataRequired()])
    first_name = StringField('Vorname', validators=[DataRequired()])
    last_name = StringField('Nachname', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8), EqualTo('password2', message="Passwörter müssen übereinstimmen")])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired()])
    submit = SubmitField('Registrieren')


class Forgot_Password_Form(FlaskForm):
    """ Forgot Password Form."""
    email = EmailField('Email', validators=[Email(), DataRequired()])
    submit = SubmitField('Zurücksetzen')
