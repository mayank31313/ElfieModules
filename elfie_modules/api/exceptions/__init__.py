from elfie_modules.backend.channels.messaging import AbstractMessagingConnector


class ElfieBaseException(Exception):
    def __init__(self, message):
        self.message = message
        super(ElfieBaseException, self).__init__(message)

    def getMessage(self):
        return self.message


class ElfieExceptionHandler(object):
    def __init__(self):
        self.messageHandler = None

    def setMessageHandler(self, messageHandler: AbstractMessagingConnector):
        self.messageHandler = messageHandler

    def handle(self, exception: ElfieBaseException):
        message = exception.getMessage()
        self.messageHandler.getErrorChannel().send(message)
