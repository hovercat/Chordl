from flask import Flask, render_template, Blueprint


index_blueprint = Blueprint(
    'index_blueprint',
    __name__,
    template_folder="templates",
    static_folder="static"
)


@index_blueprint.route('/')
def welcome_page():
    return render_template('welcome.jinja2', title="Chorupload stuffz")

