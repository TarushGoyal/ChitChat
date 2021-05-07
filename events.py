from flask import session, render_template
from flask_socketio import emit, join_room, leave_room
from . import socketIO
from .models import Message, React, Channel, User
from . import db
from flask_login import login_required, current_user
from .bot import bot_msg
import os
from .decorators import *

@socketIO.on('send chat', namespace = "/")
@login_required
def chat(json, methods=['GET', 'POST']):
    if not json['message']:
        return
    json['user_name'] = current_user.name
    room = json['channel']
    cu = ChannelUser.query.get((room, current_user.id))
    if not cu or cu.role == 'Spectator':
        return
    reply_id = json['reply_id']
    if not reply_id:
        msg = Message(content = json['message'], type = "text", posted_in = room, posted_by = current_user.id)
    else:
        msg = Message(content = json['message'], type = "text", posted_in = room,
                posted_by = current_user.id, reply_to = reply_id)
    bot_messages = bot_msg(msg, room)
    db.session.add(msg)
    db.session.commit()
    for m in bot_messages:
        db.session.add(m)
    db.session.commit()
    json['id'] = msg.id
    json['posted_at'] = str(msg.posted_at)
    msg_json = msg.__dict__
    del msg_json['_sa_instance_state']
    msg_json['posted_by_name'] = User.query.get(msg_json['posted_by']).name
    msg_json['posted_at'] = str(msg_json['posted_at'])
    print(msg_json)
    emit('add chat', msg_json, room = room)

    for m in bot_messages:
        m.posted_by # ??
        msg_json = m.__dict__
        del msg_json['_sa_instance_state']
        msg_json['posted_by_name'] = User.query.get(msg_json['posted_by']).name
        msg_json['posted_at'] = str(msg_json['posted_at'])
        emit('add chat', msg_json, room = room)

@socketIO.on('upload', namespace = "/")
@login_required
def file(json, methods=['GET', 'POST']):
    if not json['filename']:
        print ("Error: No file name in chat")
        return
    json['user_name'] = current_user.name
    room = json['channel']
    cu = ChannelUser.query.get((room, current_user.id))
    if not cu or cu.role == 'Spectator':
        return
    filename = json['filename']
    folder = json['folder']
    msg = Message(link = '/uploads/' + folder + '/' + filename, type = "file", posted_in = room, posted_by = current_user.id)
    db.session.add(msg)
    db.session.commit()
    json['id'] = msg.id
    json['posted_at'] = str(msg.posted_at)
    msg_json = msg.__dict__
    del msg_json['_sa_instance_state']
    msg_json['posted_by_name'] = User.query.get(msg_json['posted_by']).name
    msg_json['posted_at'] = str(msg_json['posted_at'])
    emit('add chat', msg_json, room = room)

@socketIO.on('joined', namespace='/')
@login_required
def joined(json):
    """Sent by clients when they enter a room"""
    print("join request received by : ",current_user.id)
    room = json['channel']
    join_room(room)
    emit('status', {})

@socketIO.on('left', namespace='/')
def left(json):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = json['channel']
    leave_room(room)
    emit('status2', {'msg': session.get('name') + ' has left the room.'}, room=room)


@socketIO.on('reacted', namespace='/')
@login_required
def reacted(json):
    room = json['channel']
    cu = ChannelUser.query.get((room, current_user.id))
    if not cu:
        return
    message_id = json['message_id']
    message = Message.query.get(message_id)
    if not message or message.deleted:
        return
    type = json['type']
    if type not in ['love', 'laugh', 'like', 'angry', 'wow', 'sad']:
        return
    react = React(react_type = type, reacted_to = message_id, reacted_by = current_user.id)
    db.session.add(react)
    db.session.commit()
    json['id'] = react.id;
    emit('add react' , json, room = room)

@socketIO.on('deleted', namespace='/')
@login_required
def deleted(json):
    room = json['channel']
    cu = ChannelUser.query.get((room, current_user.id))
    if not cu or cu.role == 'Spectator':
        return
    message_id = json['message_id']
    message = Message.query.get(message_id)
    if current_user.id != message.posted_by:
        return
    message.deleted = 1;
    db.session.commit()
    emit('delete chat' , json, room = room)
