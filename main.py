# main.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for,send_from_directory, redirect
from flask_login import login_required, current_user
from .models import *
from werkzeug.utils import secure_filename
import os

from . import db

main = Blueprint('main', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('./static/files', filename)

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir,'./static/files', filename))
            return redirect(url_for('main.uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    servers = current_user.get_servers()
    invites = current_user.get_invites()
    return render_template('profile.html', name=current_user.name, servers=servers, invites=invites)

@main.route('/users')
def users():
	data = [i.id for i in User.get_all()]
	return {
		"data" : data
	}

@main.route('/server/<id>')
@login_required
def server(id):
	server = Server.query.get(id)
	return render_template('server.html',server = server,
                                         channels = server.get_channels(),
                                         members = server.get_users())

@main.route('/channel/<id>', methods = ['GET'])
@login_required
def channel(id):
    channel = Channel.query.get(id)
    return render_template('channel.html',channel = channel,
                                          members = channel.get_users())

@main.route('/server/<id>/add-channel', methods = ['GET', 'POST'])
@login_required
def add_channel(id):
    if request.method == 'POST':
        newChannel = Channel(name = request.form.get('channelName'), server_id = id)
        db.session.add(newChannel)
        db.session.commit()
        return redirect(f'/server/{id}')
    else:
        server = Server.query.get(id)
        return render_template('add-channel.html', server = server)

@main.route('/server/<id>/add-member', methods = ['GET', 'POST'])
@login_required
def add_server_member(id):
    server = Server.query.get(id)
    matchList = []
    
    if request.method == 'POST':
        searchQuery = request.form.get('searchQuery')
        matchList = User.search_user(searchQuery)

    return render_template('add-server-member.html', server = server, matchList = matchList)

@main.route('/server/<sid>/invite/<uid>', methods = ['POST'])
@login_required
def send_invite(sid, uid):
    invite = Invitation(server_id = sid, user_id = uid)
    db.session.add(invite)
    db.session.commit()
    print(sid,uid)
    return redirect(f'/server/{sid}/add-member')

@main.route('/accept-invite/<id>', methods = ['POST'])
@login_required
def accept_invite(id):
    invite = Invitation.query.get(id)

    member = ServerUser(server_id = invite.server_id, user_id = invite.user_id, role = 'Member')
    db.session.add(member)
    
    # open_channels = ?
    # print('--', invite.hidden)

    db.session.commit()
    return redirect(f'/server/{invite.server_id}')

@main.route('/decline-invite/<id>', methods = ['POST'])
@login_required
def decline_invite(id):
    invite = Invitation.query.get(id)
    # invite.hidden = True
    db.session.commit()
    return redirect(f'/server/{invite.server_id}')


@main.route('/add-server', methods = ['POST', 'GET'])
@login_required
def add_server():
    if request.method == 'POST':
        newServer = Server(name = request.form.get('serverName'), public = False)
        db.session.add(newServer)
        db.session.flush()

        creator = ServerUser(server_id = newServer.id, user_id = current_user.id, role = 'Creator')
        db.session.add(creator)

        general_channel = Channel(name = 'General', server_id = newServer.id)
        db.session.add(general_channel)

        db.session.commit()
        return redirect(f'/server/{newServer.id}')
    else:
        return render_template('add-server.html', user_name = current_user.name)

