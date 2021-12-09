USER_UTTERED="user_uttered"
BOT_UTTERED="bot_uttered"
BOT_SPEAK = "backend/speak"

class Message(object):
    def __init__(self):
        self.topic = "default_topic"
        self.text = None

def UserInput(text="") -> Message:
    message = Message()
    message.text = text
    message.topic = USER_UTTERED

    return message

def BotResponse(text=""):
    message = Message()
    message.text = text
    message.topic = BOT_UTTERED

    return message
