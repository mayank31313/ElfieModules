import requests
import json

TOKEN = "this is the secret"


def getOrElseNone(obj,key):
    return obj[key] if key in obj else None

class RPCResponse:
    def __init__(self, **kwargs):
        self.status = getOrElseNone(kwargs, "status")
        self.response = getOrElseNone(kwargs, "response")

def request(method, params=[], host="localhost"):
    url = f"http://{host}:4000/jsonrpc"
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