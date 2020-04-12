from flask import Flask, render_template, Blueprint


record_blueprint = Blueprint(
    'record_blueprint',
    __name__,
    template_folder="templates",
    static_folder="static"
)


@record_blueprint.route('/record')
def welcome_page():
    return render_template('record.jinja2', title="Aufnahme", proben_datum="01.04.2020")

