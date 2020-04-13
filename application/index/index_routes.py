from flask import Flask, render_template, Blueprint, redirect, url_for, request, flash
from flask import current_app as app
from flask_login import current_user, login_user, login_required, logout_user
from markupsafe import Markup

from Chordl.application import db
from Chordl.application.index.forms.authentication_forms import Login_Form, Register_Form
from Chordl.application.models import User

index_bp = Blueprint(
    'index_bp',
    __name__,
    template_folder="templates",
    static_folder="static"
)


@index_bp.route('/')
def welcome_page():
    return render_template('welcome.jinja2', title="Willkommen im Chorupload Tool")


@index_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("Du bist schon eingeloggt.")
        return redirect(url_for("index_bp.welcome_page"))

    login_form = Login_Form()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            email = login_form.data.get("email")
            password = login_form.data.get("password")
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                # login
                login_user(user)

                flash("Erfolgreich angemeldet! Hallo :)")
                # redirect to next page
                next_page = request.args.get('next')
                return redirect(next_page or url_for("index_bp.welcome_page"))

            else:
                flash("Email/Passwort nicht korrekt!")
                return redirect(url_for("index_bp.login"))

        else:
            flash('Stimmt deine Email-Adresse?')
            return redirect(url_for("index_bp.login"))

    else:  # GET
        return render_template('login.jinja2',
                               title='Login',
                               form=login_form)


@index_bp.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    flash("Abgemeldet.")
    return redirect(url_for('index_bp.login'))


@index_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("Du bist bereits eingeloggt.")
        return redirect(url_for("index_bp.welcome_page"))

    register_form = Register_Form()
    if request.method == 'POST':
        if register_form.validate_on_submit():
            email = register_form.data.get("email")
            first_name = register_form.data.get("first_name")
            last_name = register_form.data.get("last_name")

            password = register_form.data.get("password")
            password2 = register_form.data.get("password2")
            if password != password2:
                flash("Passwörter sind noch nicht gleich.")
                return redirect(url_for("index_bp.register"))

            user = User.query.filter_by(email=email).first()
            if user:
                flash("User existiert bereits!")
                return redirect(url_for("index_bp.register"))

            user = User(password, email=email, first_name=first_name, last_name=last_name)
            db.session.add(user)
            db.session.commit()

            flash("User erfolgreich angelegt. Hallo {first_name}, du kannst dich nun einloggen. :)".format(first_name=first_name))
            # redirect to next page
            next_page = request.args.get('next')
            return redirect(next_page or url_for("index_bp.login"))

    return render_template('register.jinja2',
                           title='Registrierung',
                           form=register_form)


@index_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    return Markup("Lorem Ipsum")


@index_bp.route("/about")
def imprint():
    return render_template("imprint.jinja2")