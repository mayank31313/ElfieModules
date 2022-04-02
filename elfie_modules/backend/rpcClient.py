import requests
import json

from cndi.env import getContextEnvironment

TOKEN = "this is the secret"


def getOrElseNone(obj,key):
    return obj[key] if key in obj else None

class RPCResponse:
    def __init__(self, **kwargs):
        self.status = getOrElseNone(kwargs, "status")
        self.response = getOrElseNone(kwargs, "response")

def request(method, params=[]):
    host = getContextEnvironment("rpcConfig.host")
    port = getContextEnvironment("rpcConfig.port")

    url = f"http://{host}:{port}/jsonrpc"
    payload = {
        "method":  method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, headers={
        "Authorization": "Bearer " + TOKEN
    }, json=payload).json()
    return response["result"]