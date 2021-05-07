# main.py

from flask import Blueprint, render_template, request, jsonify, redirect, url_for,send_from_directory, redirect, flash
from flask_login import login_required, current_user
from .models import *
from werkzeug.utils import secure_filename
import os
import random, string
from .decorators import *
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
            filename = file.filename
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
@login_required
def profile(id):
    user = User.query.get(id)
    if user.is_bot:
        bot_user = Bot.query.get(id)
        return render_template('profile_bot.html',user = user, bot_user = bot_user, creator_name = User.query.get(bot_user.creator).name)
    else:
        return render_template('profile.html',user = user)

@main.route('/editprofile', methods = ['POST'])
@login_required
def edit_profile():
    print("edit profile called.......................")
    name = request.form.get('name')
    gender = request.form.get('gender')
    bio = request.form.get('bio')
    current_user.name = name
    current_user.gender = gender
    current_user.bio = bio
    db.session.commit()
    print("editing.......................")
    print('/user/'+str(current_user.id))
    return redirect('/user/'+str(current_user.id))

@main.route('/updateDP', methods = ['POST'])
@login_required
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

# @main.route('/users')
# def users():
# 	data = [i.id for i in User.get_all()]
# 	return {
# 		"data" : data
# 	}

@main.route('/server/<id>')
@login_required
@server_member
def server(id):
	server = Server.query.get(id)
	return render_template('server.html',server = server,
                                         channels = server.get_channels_for(current_user.id),
                                         members = server.get_users(),
                                         )

@main.route('/channel/<channel_id>', methods = ['GET'])
@login_required
@channel_member
def channel(channel_id):
    channel = Channel.query.get(channel_id)
    role = ChannelUser.query.get((channel_id,current_user.id)).role
    return render_template('channel.html',channel = channel,
                                          members = channel.get_users(),
                                          role = role)


@main.route('/chats/<id>', methods = ['POST','GET'])
@login_required
def chats(id):
    if request.method == 'POST':
        keyword = request.form['keyword']
        sender = request.form['sender']
        last_message = request.form.get('last_message')
        channel = Channel.query.get(id)
        chats = [dict(i) for i in channel.get_messages(keyword = keyword, sender = sender, id = last_message)]
        return jsonify({
            'chats' : chats
    })

@main.route('/server/<server_id>/add-channel', methods = ['GET', 'POST'])
@login_required
@server_admin
def add_channel(server_id):
    if request.method == 'POST':
        newChannel = Channel(name = request.form.get('channelName'), server_id = server_id, open = bool(request.form.get('is_open')))
        db.session.add(newChannel)
        db.session.flush()

        for server_member in Server.query.get(server_id).get_users():
            if newChannel.open or server_member.role != 'Member':
                channel_member = ChannelUser(channel_id = newChannel.id, user_id = server_member.id, role = ('Participant' if server_member.role == 'Member' else server_member.role))
                db.session.add(channel_member)

        db.session.commit()
        return redirect(f'/server/{server_id}')
    else:
        server = Server.query.get(server_id)
        return render_template('add-channel.html', server = server)

@main.route('/server/<server_id>/add-member', methods = ['GET', 'POST'])
@login_required
@server_admin
def add_server_member(server_id):
    server = Server.query.get(server_id)
    matchList = []

    if request.method == 'POST':
        searchQuery = request.form.get('searchQuery')
        matchList = User.search_user(searchQuery)

    return render_template('add-server-member.html', server = server, matchList = matchList)

@main.route('/server/<server_id>/invite/<uid>', methods = ['POST'])
@login_required
@server_admin
def send_invite(server_id, uid):
    if ServerUser.query.get((server_id, uid)) is None:
        user = User.query.get(uid)
        if user.is_bot:
            member = ServerUser(server_id = server_id, user_id = uid, role = 'Member')
            db.session.add(member)
            open_channels = Server.query.get(server_id).get_open_channels()
            for ch in open_channels:
                member = ChannelUser(channel_id = ch.id, user_id = uid, role = 'Participant')
                db.session.add(member)
        else:
            invite = Invitation(server_id = server_id, user_id = uid, description = request.form.get('inviteMsg'))
            db.session.add(invite)
        db.session.commit()
    return redirect(f'/server/{server_id}/add-member')

@main.route('/accept-invite/<id>', methods = ['POST'])
@login_required
def accept_invite(id):
    invite = Invitation.query.get(id)
    invite.accepted = True;
    if ServerUser.query.get((invite.server_id, invite.user_id)) is None:
        member = ServerUser(server_id = invite.server_id, user_id = invite.user_id, role = 'Member')
        db.session.add(member)

        open_channels = Server.query.get(invite.server_id).get_open_channels()
        for ch in open_channels:
            member = ChannelUser(channel_id = ch.id, user_id = invite.user_id, role = 'Participant')
            db.session.add(member)

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

        general_channel = Channel(name = 'General', server_id = newServer.id, open = True)
        db.session.add(general_channel)
        db.session.flush()

        creator = ServerUser(server_id = newServer.id, user_id = current_user.id, role = 'Creator')
        db.session.add(creator)

        creator = ChannelUser(channel_id = general_channel.id, user_id = current_user.id, role = 'Creator')
        db.session.add(creator)

        db.session.commit()
        return redirect(f'/server/{newServer.id}')
    else:
        return render_template('add-server.html', user_name = current_user.name)

@main.route('/create-bot', methods = ['POST', 'GET'])
@login_required
def create_bot():
    if request.method == 'POST':
        bot_name = request.form.get('botName')
        bot_user = User(name = bot_name, is_bot = True, bio = request.form.get('botDesc'))
        db.session.add(bot_user)
        db.session.flush()

        snippet = request.form.get('code')

        bot_bot = Bot(id = bot_user.id, creator = current_user.id, code = snippet)
        db.session.add(bot_bot)
        db.session.commit()

        code = f'\ndef temp(read_msg, room):\n  read_content = read_msg.content\n  posted_by = User.query.get(read_msg.posted_by).name\n  get_messages = Channel.query.get(room).get_messages\n  kick = kick_from_channel(room, {bot_user.id}, read_msg.posted_by)\n  messages = []\n{snippet}\n  assert type(messages) == list\n  return messages\nbot_send[{bot_user.id}] = temp\n'

        try:
            with open('ChitChat/bot_actions.py', 'x') as f:
                f.write('from .models import Message, React, Channel, User, ChannelUser\nfrom .bot_api import kick_from_channel\n\nbot_send = {}\n')
        except:
            pass

        with open('ChitChat/bot_actions.py', 'a') as f:
            f.write(code)
        return redirect(f'/home')

    else:
        return render_template('create-bot.html', user_name = current_user.name)

@main.route('/search-users', methods = ['POST', 'GET'])
def search_users():
    matchList = []

    if request.method == 'POST':
        searchQuery = request.form.get('searchQuery')
        matchList = User.search_user(searchQuery)

    return render_template('search-users.html', matchList = matchList)

@main.route('/channel/<channel_id>/add-member', methods = ['GET'])
@login_required
@channel_admin
def add_channel_member(channel_id):
    channel = Channel.query.get(channel_id)
    server = Server.query.get(channel.server_id)
    memberList = server.get_users_not_in(channel_id)
    return render_template('add-channel-member.html', channel = channel, memberList = memberList)

@main.route('/channel/<channel_id>/add/<uid>', methods = ['POST'])
@login_required
@channel_admin
def channel_add(channel_id, uid):
    channel = Channel.query.get(channel_id)
    su = ServerUser.query.get((channel.server_id, uid))
    if not su:
        return render_template('error.html',error = "The user is not in the server!")
    cu = ChannelUser.query.get((channel_id, uid))
    if cu:
        return render_template('error.html',error = "The user is already in the channel!")
    member = ChannelUser(channel_id = channel_id, user_id = uid, role = 'Participant')
    db.session.add(member)
    db.session.commit()
    return redirect(f'/channel/{channel_id}/add-member')

@main.route('/server/<server_id>/promote/<user_id>',methods = ['POST'])
@login_required
@server_admin
def promote(server_id, user_id):
    server_user = ServerUser.query.get((server_id,user_id))
    server_user.promote()
    return redirect('/server/'+str(server_id))

@main.route('/server/<server_id>/demote/<user_id>',methods = ['POST'])
@login_required
@server_admin
def demote(server_id, user_id):
    server_user = ServerUser.query.get((server_id,user_id))
    server_user.demote()
    return redirect('/server/'+str(server_id))

@main.route('/server/<server_id>/kick/<user_id>',methods = ['POST'])
@login_required
@server_admin
def kick(server_id, user_id):
    server_user = ServerUser.query.get((server_id,user_id))
    if not server_user:
        return render_template('error.html',error = "Don't kick someone who is not in the server :/")
    server_user.kick()
    return redirect('/server/'+str(server_id))

@main.route('/channel/<channel_id>/promote/<user_id>',methods = ['POST'])
@login_required
@channel_admin
def promote_channel(channel_id, user_id):
    channel_user = ChannelUser.query.get((channel_id,user_id))
    channel_user.promote()
    return redirect('/channel/'+str(channel_id))

@main.route('/channel/<channel_id>/demote/<user_id>',methods = ['POST'])
@login_required
@channel_admin
def demote_channel(channel_id, user_id):
    channel_user = ChannelUser.query.get((channel_id,user_id))
    channel_user.demote()
    return redirect('/channel/'+str(channel_id))

@main.route('/channel/<channel_id>/kick/<user_id>',methods = ['POST'])
@login_required
@channel_admin
def kick_channel(channel_id, user_id):
    channel_user = ChannelUser.query.get((channel_id,user_id))
    if not channel_user:
        return render_template('error.html',error = "Don't kick someone who is not in the channel :/")
    channel_user.kick()
    return redirect('/channel/'+str(channel_id))

@main.route('/server/<server_id>/leave', methods = ['GET'])
@login_required
def leave_server(server_id):
    server_user = ServerUser.query.get((server_id, current_user.id))
    if not server_user or server_user != 'Creator':
        return render_template('error.html',error = "Can't leave a server if you created it or not in it :)")
    server_user.kick()
    return redirect('/home')
