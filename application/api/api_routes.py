import os
import tempfile

from flask import Flask, render_template, Blueprint, request, abort, make_response
from flask_login import login_required, current_user
from markupsafe import Markup
from werkzeug.utils import secure_filename

from application.models import db, SynchronizationFile, Rehearsal_Song, RecordingFile, Song_ChoirSection, Rehearsal

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


@login_required
@api_bp.route('/api/rehearsal_<int:rehearsal_id>/songs')
def rehearsal_songs(rehearsal_id):
    if not current_user.is_authenticated:
        return abort(403)

    r = Rehearsal.query.filter_by(rid = rehearsal_id).first() #todo


@login_required
@api_bp.route('/api/upload_recording', methods=["POST"])
def upload_recording():
    if request.method != "POST":
        return abort(403)  # todo

    rehearsal_id = request.form['rehearsal_id']
    song_id = request.form['song_id']
    choir_section = request.form['choir_section']

    if len(request.files) == 0:
        return abort(400)

    file = request.files['file']

    file_name = secure_filename(file.filename)
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file_name)
        file.save(file_path)

        rehearsal_song = Rehearsal_Song.query.filter_by(rid=rehearsal_id, sid=song_id).first()
        if rehearsal_song is None:
            return abort(404)

        song_choirsection = Song_ChoirSection.query.filter_by(sid=song_id, csid=choir_section).first()
        if song_choirsection is None:
            #song_choirsection = Song_ChoirSection.query.filter_by(sid=song_id, fallback=True).first() # TODO Fallback
            #if song_choirsection is None:
            return abort(404)

        rec_file = RecordingFile(rehearsal_song, song_choirsection, current_user.uid, file_path)

        db.session.add(rec_file)
        db.session.commit()

    return make_response("Aufnahme hochgeladen!", 200)

# liste mit song_ids für probe
