from flask import Flask, render_template, Blueprint
from markupsafe import Markup

from application.models import db, SynchronizationFile

api_bp = Blueprint(
    'api_bp',
    __name__
)


@api_bp.route('/api/syncfile/<int:sync_id>')
def get_syncfile(sync_id):
    sync_file = SynchronizationFile.query.filter_by(sync_id=sync_id).first()

    if sync_file is not None:
        return sync_file.provide_as_download()
    else:
        return Markup("404: Synchronization File {sync_id} not found".format(sync_id=sync_id))
