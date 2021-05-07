from .models import Message, React, Channel, User

def bot_msg(read_msg, room):
    msgs = []
    try:
        from .bot_actions import bot_send
        bots = User.get_bots()
        for bot in bots:
            msgs.extend([Message(content = c, type = 'text', posted_in = room, posted_by = bot.id) for c in bot_send[bot.id](read_msg, room)])
    except:
        pass
    return msgs
