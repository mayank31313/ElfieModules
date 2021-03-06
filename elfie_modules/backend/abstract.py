from functools import wraps


class AbstractConnector:
    def __init__(self):
        self.config = None
        self.channel = None
        self.configuration = dict()

    def setConfig(self, config, configuration=None):
        self.config = config
        name = self.name()
        if configuration is not None and 'usesChannel' in configuration:
            self.channel = list(filter(lambda elfieChannel: elfieChannel.name() == configuration['usesChannel'], self.config.channels))[0]
            return None

        for channel in self.config.channels:
            if name.lower().startswith(channel.name()):
                self.channel = channel
                break
    def getConfiguration(self, key):
        if key in self.configuration:
            return self.configuration.get(key)
        return None

    def name(self):
        pass
    def execute(self, *args):
        pass

FUNCTIONAL_CONNECTORS = dict()

def functionalconnector(name, ignoreParams=[]):
    def innerFunction(func):
        @wraps(func)
        def nestedFunction(*args, **kwargs):
            return func(*args, **kwargs)
        d = list(filter(lambda x: x[0] not in ignoreParams, func.__annotations__.items()))
        func_name = f"{func.__module__}.{func.__name__}"
        FUNCTIONAL_CONNECTORS[func_name] = {
            'annotations': dict(d),
            'func':  nestedFunction,
            'name': name
        }
        return nestedFunction
    return innerFunction