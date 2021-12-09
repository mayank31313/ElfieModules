class AbstractMessagingConnector(object):
    def __init__(self, connector):
        self.connector = connector

    def connect(self,**kwargs):
        pass

    def send(self, data):
        pass

    def setConfigurations(self):
        pass

from paho.mqtt.client import Client

class MqttMessageConnector(AbstractMessagingConnector):
    def __init__(self):
        self.connector = Client()

    def connect(self,**kwargs):
        on_connect = kwargs['on_connect']
        on_message = kwargs['on_message']

        self.connector.on_connect = on_connect
        self.connector.on_message = on_message

