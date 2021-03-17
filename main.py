# main.py

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import *

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    dms1 = [i for i in User.query.join(DM, User.id == DM.id2).filter(DM.id1==current_user.id).all()]
    dms2 = [i for i in User.query.join(DM, User.id == DM.id1).filter(DM.id2==current_user.id).all()]
    servers = [i for i in Server.query.join(ServerUser).filter(ServerUser.user_id == current_user.id).all()]
    return render_template('profile.html', name=current_user.name, dms = dms1 + dms2, servers=servers)

@main.route('/users')
@login_required
def users():
	data = [i.id for i in User.query.all()]
	return {
		"data" : data
	}

@main.route('/dm/<id>')
@login_required
def dm(id):
	return render_template('dm.html',id = id)

@main.route('/dm/<id>', methods=['POST'])
@login_required
def dm_post(id):
	chat = request.form.get('chat')
	message = Message()
	return render_template('dm.html', id = id)

@main.route('/server/<id>')
@login_required
def server(id):
	server = Server.query.get(id)
	channels = Channel.query.filter_by(server_id = id).all()
	members = User.query.join(ServerUser).filter(ServerUser.server_id == id).all()
	return render_template('server.html',server = server, channels = channels, members = members)

@main.route('/channel/<id>', methods = ['GET'])
@login_required
def channel(id):
    channel = Channel.query.get(id)
    chats = db.engine.execute('''
    select User.name as name, Message.id as id, Message.content as content,
    count(case when React.react_type = 'yes' then 1 end) as yes,
    count(case when React.react_type = 'no' then 1 end) as no
    from (Message join User) left outer join React
    on Message.id = React.reacted_to
    where Message.posted_by = User.id
    and Message.posted_in = :id
    group by Message.id, Message.content, User.name
    ''',{'id' : id})
    members = User.query.join(ChannelUser).filter(ChannelUser.channel_id == id).all()
    return render_template('channel.html',channel = channel, chats = chats, members = members)
