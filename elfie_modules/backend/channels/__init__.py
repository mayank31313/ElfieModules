class Credentials:
    def __init__(self, type, secret_key=None, secret_value=None, **kwargs):
        self.type = type
        self.secret_key = secret_key
        self.secret_value = secret_value

        if type == "token_based":
            self.token = kwargs['token']