# models.py

from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
	__tablename__ = "User"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	name = db.Column(db.String(1000))

# class Profile(db.Model):
# 	__tablename__ = "Profile"
# #

class DM(db.Model):
	__tablename__ = "DM"
	id1 = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
	id2 = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)

class Server(db.Model):
    __tablename__ = "Server"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime)
    public = db.Column(db.Boolean)

class ServerUser(db.Model):
	__tablename__ = "ServerUser"
	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'), primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True)

class Invitation(db.Model):
	__tablename__ = "Invitation"
	id = db.Column(db.Integer, primary_key=True)
	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

class Channel(db.Model):
	__tablename__ = "Channel"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(1000))
	created_at = db.Column(db.DateTime)
	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'), primary_key = True)

class ChannelUser(db.Model):
    __tablename__ = "ChannelUser"
    channel_id = db.Column(db.Integer, db.ForeignKey('Channel.id'), primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True)

class Message(db.Model):
	__tablename__ = "Message"
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime)
	deleted = db.Column(db.Boolean)
	posted_by = db.Column(db.Integer, db.ForeignKey('User.id'))
	posted_in = db.Column(db.Integer, db.ForeignKey('Channel.id'))
	reply_to = db.Column(db.Integer, db.ForeignKey('Message.id'))

class React(db.Model):
	__tablename__ = "React"
	id = db.Column(db.Integer, primary_key=True)
	react_type = db.Column(db.String)
	reacted_to = db.Column(db.Integer, db.ForeignKey('Message.id'))
	reacted_by = db.Column(db.Integer, db.ForeignKey('User.id'))
