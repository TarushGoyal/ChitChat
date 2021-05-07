# main.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for,send_from_directory, redirect, flash
from flask_login import login_required, current_user
from .models import *
from werkzeug.utils import secure_filename
import os
import random, string

from . import db

main = Blueprint('main', __name__)

@main.route('/uploads/<folder>/<filename>')
def uploaded_file(folder,filename):
    return send_from_directory('./static/files/'+folder, filename)

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        print("---main.py upload_file()---")
        if 'file' not in request.files:
            print("file argument missing in form data")
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print("file name missing in form data")
            flash('No selected file')
            return redirect(request.url)
        if file:
            print("valid file")
            filename = secure_filename(file.filename)
            basedir = os.path.abspath(os.path.dirname(__file__))
            folder = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            os.mkdir(os.path.join(basedir,'./static/files',folder))
            file.save(os.path.join(basedir,'./static/files/' + folder + "/", filename))
            # return redirect(url_for('main.uploaded_file',
                                    # folder=folder,filename=filename))
            return jsonify({"folder" : folder})
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new'No selected file') File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@main.route('/')
def index():
    if current_user.is_authenticated:
         return redirect('/home')
    else:
         return redirect('/login')

@main.route('/home')
@login_required
def home():
    servers = current_user.get_servers()
    invites = current_user.get_invites()
    return render_template('home.html', name=current_user.name, servers=servers, invites=invites)

@main.route('/user/<id>')
def profile(id):
    user = User.query.get(id)
    return render_template('profile.html',user = user)

@main.route('/updateDP', methods = ['POST'])
def updateDP():
    if 'file' not in request.files:
        print("file argument missing in form data")
        return redirect(url_for('main.profile', id = current_user.id))
    file = request.files['file']
    if '.' not in file.filename:
        print("file name missing in form data")
        return redirect(url_for('main.profile', id = current_user.id))
    ext = file.filename.split('.')[-1]
    if file and ext in ['jpg','png','jpeg']:
        basedir = os.path.abspath(os.path.dirname(__file__))
        file.save(os.path.join(basedir,'./static/DPs/', str(current_user.id) + '.' + ext))
        current_user.DP = str(current_user.id) + '.' + ext
        db.session.commit()
        return redirect(url_for('main.profile', id = current_user.id))
    print("Error-----------------------")
    return redirect(url_for('main.profile', id = current_user.id))

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


@main.route('/chats/<id>', methods = ['POST','GET'])
@login_required
def chats(id):
    if request.method == 'POST':
        keyword = request.form['keyword']
        sender = request.form['sender']
        channel = Channel.query.get(id)
        chats = [dict(i) for i in channel.get_messages(keyword = keyword, sender = sender)]
        return jsonify({
            'chats' : chats
    })

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
    invite = Invitation(server_id = sid, user_id = uid, description = request.form.get('inviteMsg'))
    db.session.add(invite)
    db.session.commit()
    print(sid,uid)
    return redirect(f'/server/{sid}/add-member')

@main.route('/accept-invite/<id>', methods = ['POST'])
@login_required
def accept_invite(id):
    invite = Invitation.query.get(id)
    invite.accepted = True;
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
    invite.hidden = True
    db.session.commit()
    return redirect(url_for('main.home'))


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

@main.route('/create-bot', methods = ['POST', 'GET'])
@login_required
def create_bot():
    if request.method == 'POST':
        bot_name = request.form.get('botName')
        bot_user = User(name = bot_name)
        db.session.add(bot_user)
        db.session.commit()

        snippet = request.form.get('code')
        code = f'\ndef temp(read_msg, room):\n  read_content = read_msg.content\n  posted_by_name = User.query.get(read_msg.posted_by).name\n  messages = []\n{snippet}\n  assert type(messages) == list\n  return messages\nbot_send[{bot_user.id}] = temp'
        with open('ChitChat/bot_actions.py', 'a') as f:
            f.write(code)
        return redirect(f'/home')
    else:
        return render_template('create-bot.html', user_name = current_user.name)

