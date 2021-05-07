from .models import Message, React, Channel, User, ChannelUser
from . import db

def kick_from_channel(channel_id):
	def kick(user_name):
		users = list(db.engine.execute('''
									SELECT User.id
									FROM ChannelUser INNER JOIN User
										ON ChannelUser.channel_id = :cid AND ChannelUser.user_id = User.id
									WHERE User.name = :uname
									''', {'cid':channel_id, 'uname':user_name}))
		if len(list(users)) == 1:
			ChannelUser.query.get((channel_id, users[0].id)).kick()
			return True
		else:
			return False
	return kick
