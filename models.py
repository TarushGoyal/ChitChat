# models.py

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy, event
from . import db

class User(UserMixin, db.Model):
	__tablename__ = "User"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	name = db.Column(db.String(1000))
	def get_servers(self):
		return Server.query.join(ServerUser).filter(ServerUser.user_id == self.id).all()
	def assign_role(self, server_id, role):
		db.engine.execute('''UPDATE ServerUser SET role = :r WHERE server_id = :s AND user_id = :id''', {'r':role, 's':server_id, 'id':self.id})
	@classmethod
	def get_all(cls):
		return db.engine.execute('''SELECT * FROM User''')
	@classmethod
	def search_user(cls, s):
		comp = '"%' + s + '%"'
		return db.engine.execute('''SELECT * FROM User WHERE name LIKE :ss''', {'ss':comp})

class Server(db.Model):
    __tablename__ = "Server"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime)
    public = db.Column(db.Boolean)
    def get_channels(self):
    	return db.engine.execute('''SELECT * 
    								FROM Channel 
    								WHERE Channel.server_id = :id''', 
    								{'id':self.id})
    def get_users(self):
    	return db.engine.execute('''SELECT User.* 
    								FROM User LEFT JOIN ServerUser 
    								ON ServerUser.server_id = :id AND ServerUser.user_id = User.id''', 
    								{'id':self.id})
    @classmethod
    def get_public_servers(cls):
    	return db.engine.execute('''SELECT * FROM Server WHERE Server.public''')

class ServerUser(db.Model):
	__tablename__ = "ServerUser"
	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'), primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True)
	role = db.Column(db.String(20)) # 'Creator', 'Admin', 'Spectator', 'Participant'

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
	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'))
	def get_messages(self):
		return db.engine.execute('''
		    SELECT User.name AS name, Message.id AS id, Message.content AS content,
		    count(CASE WHEN React.react_type = 'yes' THEN 1 END) AS yes,
		    count(CASE WHEN React.react_type = 'no' THEN 1 END) AS no
		    FROM (Message JOIN User) LEFT OUTER JOIN React
		    ON Message.id = React.reacted_to
		    WHERE Message.posted_by = User.id AND Message.posted_in = :id
		    GROUP BY Message.id, Message.content, User.name''',
		    {'id' : self.id})
	def get_users(self):
		return db.engine.execute('''SELECT User.* 
    								FROM User LEFT JOIN ChannelUser 
    								ON ChannelUser.channel_id = :id AND ChannelUser.user_id = User.id''', 
    								{'id':self.id})
	def add_server_admins(self):
		db.engine.execute('''INSERT INTO ChannelUser
							 SELECT :cid , user_id
							 FROM ServerUser
							 WHERE server_id = :sid AND role = "Admin"''',
							 {'cid':self.id, 'sid':self.server_id})
	@classmethod
	def get_public_channels(cls):
		return db.engine.execute('''SELECT Channel.* 
									FROM Channel INNER JOIN Server 
									ON Channel.server_id = Server.id AND Server.public''')

class ChannelUser(db.Model):
    __tablename__ = "ChannelUser"
    channel_id = db.Column(db.Integer, db.ForeignKey('Channel.id'), primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True)

class Message(db.Model):
	__tablename__ = "Message"
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(10000))
	timestamp = db.Column(db.DateTime)
	deleted = db.Column(db.Boolean)
	posted_by = db.Column(db.Integer, db.ForeignKey('User.id'))
	posted_in = db.Column(db.Integer, db.ForeignKey('Channel.id'))
	reply_to = db.Column(db.Integer, db.ForeignKey('Message.id'))
	def delete_message(self):
		self.deleted = True
	def react_yes(self):
		l = list(db.engine.execute('''SELECT react_type FROM React WHERE React.reacted_to = :id''', {'id':self.id}))
		if l[0] == 'yes':
			db.engine.execute('''DELETE FROM React WHERE reacted_to = :id''', {'id':self.id})
		elif l[0] == 'no':
			db.engine.execute('''UPDATE React SET react_type = 'yes' WHERE reacted_to = :id''', {'id':self.id})
	def react_no(self):
		l = list(db.engine.execute('''SELECT react_type FROM React WHERE React.reacted_to = :id''', {'id':self.id}))
		if l[0] == 'no':
			db.engine.execute('''DELETE FROM React WHERE reacted_to = :id''', {'id':self.id})
		elif l[0] == 'yes':
			db.engine.execute('''UPDATE React SET react_type = 'no' WHERE reacted_to = :id''', {'id':self.id})

class React(db.Model):
	__tablename__ = "React"
	id = db.Column(db.Integer, primary_key=True)
	react_type = db.Column(db.String(10))
	reacted_to = db.Column(db.Integer, db.ForeignKey('Message.id'))
	reacted_by = db.Column(db.Integer, db.ForeignKey('User.id'))

