# models.py

# from flask_login import UserMixin
# from flask_sqlalchemy import SQLAlchemy, event
# from . import db

# class User(db.Model):
# 	__tablename__ = 'User'
# 	id = db.Column(db.Integer, primary_key = True, nullable = False)
# 	type = db.Column(db.String(10), nullable = False)
# 	name = db.Column(db.String(100))

# class Bot(db.Model):
# 	__tablename__ = 'Bot'
# 	id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True, nullable = False)
# 	script = db.Column(db.String(1000))
# 	creator = db.Column(db.Integer, db.ForeignKey('Human.id'), nullable = False)

# class Server(db.Model):
# 	__tablename__ = 'Server'
# 	id = db.Column(db.Integer, primary_key = True, nullable = False)
# 	name = db.Column(db.String(100))
# 	dp = db.Column(db.String(500), default = '')
# 	created_at = db.Column(db.DateTime)
# 	description = db.Column(db.String(1000))

# class ServerUser(db.Model):
# 	__tablename__ = 'ServerUser'
# 	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'), primary_key = True)
# 	user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True)
# 	role = db.Column(db.String(20))		 # 'Creator', 'Admin', 'Member'

# class Invitation(db.Model):
# 	__tablename__ = 'Invitation'
# 	id = db.Column(db.Integer, primary_key = True, nullable = False)
# 	server_id = db.Column(db.Integer, db.ForeignKey(Server.id))
# 	user_id = db.Column(db.Integer, db.ForeignKey(User.id))
# 	description = db.Column(db.String(1000))
# 	channel_role = db.Column(db.String(20), default = 'Participant')
# 	hidden = db.Column(db.Boolean, default = False)
# 	accepted = db.Column(db.Boolean, default = False)

# class Channel(db.Model):
# 	__tablename__ = 'Channel'
# 	id = db.Column(db.Integer, primary_key = True, nullable = False)
# 	description = db.Column(db.String(1000))
# 	name = db.Column(db.String(100))
# 	created_at = db.Column(db.DateTime)
# 	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'), nullable = False)
# 	open = db.Column(db.Boolean, default = False)

# class ChannelUser(db.Model):
#     __tablename__ = "ChannelUser"
#     channel_id = db.Column(db.Integer, db.ForeignKey('Channel.id'), primary_key = True)
#     user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True)
#     role = db.Column(db.String(20))		 # 'Creator', 'Admin', 'Participant', 'Spectator'

# class Message(db.Model):
# 	__tablename__ = "Message"
# 	id = db.Column(db.Integer, primary_key = True, nullable = False)
# 	type = db.Column(db.String(10), nullable = False)
# 	content = db.Column(db.String(10000))
# 	link = db.Column(db.String(200))
# 	timestamp = db.Column(db.DateTime)
# 	deleted = db.Column(db.Boolean, default = False)
# 	posted_by = db.Column(db.Integer, db.ForeignKey('User.id'))
# 	posted_by_name = db.Column(db.String(100))
# 	posted_in = db.Column(db.Integer, db.ForeignKey('Channel.id'))
# 	reply_to = db.Column(db.Integer, db.ForeignKey('Message.id'))
# 	def delete_message(self):
# 		self.deleted = True

# class React(db.Model):
# 	__tablename__ = "React"
# 	id = db.Column(db.Integer, primary_key = True, nullable = False)
# 	react_type = db.Column(db.String(10))
# 	reacted_to = db.Column(db.Integer, db.ForeignKey('Message.id'))
# 	reacted_by = db.Column(db.Integer, db.ForeignKey('User.id'))
# 	reacted_at = db.Column(db.DateTime)



from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy, event
from . import db

class User(UserMixin, db.Model):
	__tablename__ = "User"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	name = db.Column(db.String(1000))
	DP = db.Column(db.String(500), default = "0.jpeg")
	gender = db.Column(db.String(10), default = "unknown")
	bio = db.Column(db.String(100), default = "Hemlo there I am using Hemlo")
	join_date = db.Column(db.DateTime, server_default = db.func.now())
	def get_servers(self):
		return Server.query.join(ServerUser).filter(ServerUser.user_id == self.id).all()
	def get_invites(self):
		return db.engine.execute('''
			SELECT Invitation.id, Invitation.server_id, Invitation.description, Server.name
			FROM Invitation INNER JOIN Server
			ON Invitation.server_id = Server.id
			WHERE Invitation.user_id = :id
			AND Invitation.accepted = 0
			AND Invitation.hidden = 0
		''', {'id':self.id});
	def assign_role(self, server_id, role):
		db.engine.execute('''UPDATE ServerUser SET role = :r WHERE server_id = :s AND user_id = :id''', {'r':role, 's':server_id, 'id':self.id})
	@classmethod
	def get_all(cls):
		return db.engine.execute('''SELECT * FROM User''')
	@classmethod
	def get_bots(cls):
		return db.engine.execute('''SELECT id FROM User WHERE email IS NULL''')
	@classmethod
	def search_user(cls, s):
		comp = '%' + s + '%'
		return db.engine.execute('''SELECT * FROM User WHERE name LIKE :ss''', {'ss':comp})

class Server(db.Model):
	__tablename__ = "Server"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(1000))
	created_at = db.Column(db.DateTime, server_default = db.func.now())
	public = db.Column(db.Boolean)
	def get_channels(self):
		return db.engine.execute('''SELECT *
									FROM Channel
									WHERE Channel.server_id = :id''',
									{'id':self.id})
	def get_users(self):
		return db.engine.execute('''SELECT User.*, ServerUser.role as role
									FROM User INNER JOIN ServerUser
									ON ServerUser.server_id = :id AND ServerUser.user_id = User.id''',
									{'id':self.id})
    def get_users_not_in(self, chan_id):
    	return db.engine.execute('''SELECT User.*
    								FROM User
    									INNER JOIN ServerUser ON ServerUser.server_id = :sid AND ServerUser.user_id = User.id
    									INNER JOIN Channel ON Channel.server_id = :sid AND Channel.id = :cid
    									LEFT OUTER JOIN ChannelUser ON ChannelUser.channel_id = :cid AND ChannelUser.user_id = User.id
    								WHERE ChannelUser.channel_id IS NULL''',
    								{'sid':self.id, 'cid':chan_id})
	def get_open_channels(self):
		return db.engine.execute('''SELECT *
									FROM Channel
									WHERE Channel.server_id = :id
									AND open = 1
									''',{'id':self.id})
	@classmethod
	def get_public_servers(cls):
		return db.engine.execute('''SELECT * FROM Server WHERE Server.public''')

class ServerUser(db.Model):
	__tablename__ = "ServerUser"
	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'), primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True)
	role = db.Column(db.String(20), nullable = False) # 'Creator', 'Admin', 'Member'
	def add_member(user_id, server_id):
		server_user = ServerUser(server_id = server_id, user_id = user_id, role = 'Member')
		db.session.add(server_user)
		server = Server.query.get(server_id)
		for channel in server.get_open_channels():
			channel_user = ChannelUser(channel_id = channel.id, user_id = user_id, role = 'Participant') # default
			db.session.add(channel_user)
		db.session.commit()
	def kick(self):
		user = User.query.get(self.user_id)
		server = Server.query.get(self.server_id)
		channels = server.get_channels()
		for channel in channels:
			channel_user = ChannelUser.query.get((channel.id, user.id))
			if channel_user:
				db.session.delete(channel_user)
		db.session.delete(self)
		db.session.commit()
	def promote(self):
		if self.role == 'Member':
			self.role = 'Admin'
			user = User.query.get(self.user_id)
			server = Server.query.get(self.server_id)
			channels = server.get_channels()
			for channel in channels:
				channel_user = ChannelUser.query.get((channel.id, user.id))
				if channel_user:
					channel_user.role = 'Admin'
				else:
					new_channel_user = ChannelUser(channel_id = channel.id, user_id = self.user_id, role = 'Admin')
					db.session.add(new_channel_user)
			db.session.commit()
			return True
		elif self.role == 'Admin':
			print("Attempting to promote Admin!!")
		elif self.role == 'Creator':
			print("Attempting to promote Creator!!")
		else:
			print("Unknown Role in promote!!!")
		return False
	def demote(self):
		if self.role == 'Admin':
			self.role = 'Member'
			user = User.query.get(self.user_id)
			server = Server.query.get(self.server_id)
			channels = server.get_channels()
			for channel in channels:
				channel_user = ChannelUser.query.get((channel.id, user.id))
				channel_user.role = 'Participant'
			db.session.commit()
			return True
		elif self.role == 'Member':
			print("Attempting to demote Member!!")
		elif self.role == 'Creator':
			print("Attempting to demote Creator!!")
		else:
			print("Unknown Role in demote!!!")
		return False
class Invitation(db.Model):
	__tablename__ = "Invitation"
	id = db.Column(db.Integer, primary_key=True)
	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	description = db.Column(db.String(1000))
	# server_role = db.Column(db.String(20), default = 'Member')
	# channel_role = db.Column(db.String(20), default = 'Participant')
	hidden = db.Column(db.Boolean, default = False)
	accepted = db.Column(db.Boolean, default = False)

class Channel(db.Model):
	__tablename__ = "Channel"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(1000))
	created_at = db.Column(db.DateTime, server_default = db.func.now())
	server_id = db.Column(db.Integer, db.ForeignKey('Server.id'))
	description = db.Column(db.String(1000))
	open = db.Column(db.Boolean, default = False)
	def get_messages(self, keyword, sender):
		query = '''
		SELECT User.name AS name,
		Message.id AS id, Message.content, Message.posted_at,
		Message.deleted, Message.reply_to, Message.type, Message.link,
		count(CASE WHEN React.react_type = 'like' THEN 1 END) AS "like",
		count(CASE WHEN React.react_type = 'love' THEN 1 END) AS love,
		count(CASE WHEN React.react_type = 'angry' THEN 1 END) AS angry,
		count(CASE WHEN React.react_type = 'laugh' THEN 1 END) AS laugh,
		count(CASE WHEN React.react_type = 'wow' THEN 1 END) AS wow,
		count(CASE WHEN React.react_type = 'sad' THEN 1 END) AS sad
		FROM (Message JOIN User) LEFT OUTER JOIN React
		ON Message.id = React.reacted_to
		WHERE Message.posted_by = User.id AND Message.posted_in = :id
		'''
		args = {'id' : self.id}
		if sender != "":
			query += ''' AND User.name = :sender '''
			args['sender'] = sender
		if keyword != "":
			query += ''' AND Message.content LIKE :pattern '''
			args['pattern'] = '%' + keyword + '%'
		query += ''' GROUP BY Message.id, Message.content, User.name '''
		return db.engine.execute(query,args)
	def get_users(self):
		return db.engine.execute('''SELECT User.*, ChannelUser.role AS role
    								FROM User INNER JOIN ChannelUser
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
    role = db.Column(db.String(20), nullable = False)		 # 'Creator', 'Admin', 'Participant', 'Spectator'

# class Message(db.Model):
# 	__tablename__ = "Message"
# 	id = db.Column(db.Integer, primary_key=True)
# 	content = db.Column(db.String(10000))
# 	posted_at = db.Column(db.DateTime, server_default = db.func.now())
# 	deleted = db.Column(db.Boolean)
# 	posted_by = db.Column(db.Integer, db.ForeignKey('User.id'))
# 	posted_in = db.Column(db.Integer, db.ForeignKey('Channel.id'))
# 	reply_to = db.Column(db.Integer, db.ForeignKey('Message.id'))
# 	def delete_message(self):
# 		self.deleted = True

class Message(db.Model):
	__tablename__ = "Message"
	id = db.Column(db.Integer, primary_key = True, nullable = False)
	type = db.Column(db.String(10), nullable = False)
	content = db.Column(db.String(10000))
	link = db.Column(db.String(200))
	posted_at = db.Column(db.DateTime, server_default = db.func.now())
	deleted = db.Column(db.Boolean, default = False)
	posted_by = db.Column(db.Integer, db.ForeignKey('User.id'))
	# posted_by_name = db.Column(db.String(100))
	posted_in = db.Column(db.Integer, db.ForeignKey('Channel.id'))
	reply_to = db.Column(db.Integer, db.ForeignKey('Message.id'))
	def delete_message(self):
		self.deleted = True
class React(db.Model):
	__tablename__ = "React"
	id = db.Column(db.Integer, primary_key=True)
	react_type = db.Column(db.String(10))
	reacted_to = db.Column(db.Integer, db.ForeignKey('Message.id'))
	reacted_by = db.Column(db.Integer, db.ForeignKey('User.id'))
