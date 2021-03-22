from flask import session
from flask_socketio import emit, join_room, leave_room
from . import socketIO
from .models import Message, React, Channel
from . import db
from flask_login import login_required, current_user

@socketIO.on('send chat', namespace = "/")
@login_required
def chat(json, methods=['GET', 'POST']):
    print('received my event: ',json)
    if not json['message']:
        return
    json['user_name'] = current_user.name
    room = json['channel']
    msg = Message(content = json['message'], posted_in = room, posted_by = current_user.id)
    db.session.add(msg)
    db.session.commit()
    json['id'] = msg.id
    json['posted_at'] = str(msg.posted_at)
    emit('add chat', dict(msg), room = room)

@socketIO.on('joined', namespace='/')
@login_required
def joined(json):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    print(json)
    room = json['channel']
    print("Room:",room)
    join_room(room)
    channel = Channel.query.get(room)
    chats = [dict(i) for i in channel.get_messages()]
    # emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)
    emit('status', {'chats': chats}, room = current_user.id)

@socketIO.on('left', namespace='/')
def left(json):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = json['channel']
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)


@socketIO.on('reacted', namespace='/')
@login_required
def reacted(json):
    room = json['channel']
    message_id = json['message_id']
    type = json['type']
    react = React(react_type = type, reacted_to = message_id, reacted_by = current_user.id)
    print("Received React in channel : {}, on message : {}, type = {}".format(room, message_id, type))
    db.session.add(react)
    db.session.commit()
    json['id'] = react.id;
    emit('add react' , json, room = room)
