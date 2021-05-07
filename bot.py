from .models import Message, React, Channel, User

def bot_msg(read_msg, room):
    msgs = []
    try:
        from .bot_actions import bot_send
    except:
        return []
    bots = Channel.query.get(room).get_bots()
    for bot in bots:
        if bot.role != 'Spectator':
            msgs.extend([Message(content = c, type = 'text', posted_in = room, posted_by = bot.id) for c in bot_send[bot.id](read_msg, room)])
    return msgs
