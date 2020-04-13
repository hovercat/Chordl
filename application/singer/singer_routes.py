from flask import Flask, render_template, Blueprint
from flask_login import login_required, current_user

from application.models import Rehearsal

record_blueprint = Blueprint(
    'record_blueprint',
    __name__,
    template_folder="templates",
    static_folder="static"
)


@login_required
@record_blueprint.route('/record/<int:rehearsal_id>')
def record_rehearsal(rehearsal_id):
    rehearsal = Rehearsal.query.filter_by(rid=rehearsal_id).first()
    if rehearsal is None or not current_user.is_authenticated or rehearsal.choir not in current_user.choirs:
        # TODO no rehearsal found or other stuff listed above
        pass

    return render_template('record.jinja2',
                           title="Aufnahme",
                           rehearsal = rehearsal,
                           proben_datum="01.04.2020")
