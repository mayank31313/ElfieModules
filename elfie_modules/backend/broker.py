from functools import wraps
import sys

from cndi.env import loadEnvFromFile, getContextEnvironment
from cndi.initializers import AppInitilizer

sys.path.append("E:\Projects\ElfiePlugins")

from elfie_modules.backend.abstract import FUNCTIONAL_CONNECTORS, functionalconnector
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

from elfie_modules.phase_neurons.config import ElfieConfig
from elfie_modules.backend.rpcClient import request, TOKEN

import paho.mqtt.client as mqtt
import socket, json, os
import importlib
from paho.mqtt.client import Client
from cndi.annotations import Autowired, getBeanObject

import logging
from elfie_modules.pipeline import BOT_SPEAK

logging.basicConfig(format=f'%(asctime)s - %(name)s -  %(levelname)s - %(message)s', level=logging.INFO)

clients = dict()

elfie = None
mqtt_client = None
ip_address = None

logger = logging.getLogger(__name__)

@Autowired()
def setElfieAndClient(config: ElfieConfig, client: Client):
    global elfie, mqtt_client, mongo_client, elfieZookeeper
    elfie = config
    logger.info(f"Node ID {elfie.nodeId}")
    mqtt_client = client

def sendInformation(client):
    client.publish("agent/added", json.dumps({
        "uid": elfie.agent['uid'],
        "ip": [ip_address]
    }))

def on_connect(client: mqtt.Client, userdata, flags, rc):
    logger.info("Connected with result code "+str(rc))

    client.subscribe("agent/added")
    client.subscribe("agent/disconnected")
    client.subscribe(f"agent/{elfie.agent['uid']}")
    client.subscribe("agent/pong")

    client.publish("agent/pong")

def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    if "agent/pong" == msg.topic:
        print("Sending Information")
        sendInformation(client)

    if msg.payload == b'':
        return

    payload = json.loads(msg.payload.decode())
    if "agent/added" == msg.topic:
        uid = payload['uid']
        ipaddress = payload['ip'][0]
        if ipaddress != ip_address:
            logger.info(f"Agent Added {request('getUid', host=ipaddress)}")
            clients[uid] = ip_address

def authRequired(func):
    @wraps(func)
    def wrapper(request: Request, *args, **kwargs):
        authorization = request.headers.get("Authorization")
        if authorization is None:
            return Response(status=403)
        elif authorization[7:] == TOKEN:
            return func(request=request, *args, **kwargs)

        return Response(status=401)
    return wrapper

@Request.application
@authRequired
def application(request: Request):
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)

    return Response(response.json, mimetype='application/json')

@functionalconnector("getUid")
def getUid():
    return elfie.agent['uid']

@functionalconnector(BOT_SPEAK)
def speak(message):
    mqtt_client.publish(BOT_SPEAK, message)

def wrap(func, params):
    def inside(*x):
        return func(*x, **params)
    return inside

def start(elfieConfig):
    global elfie, ip_address
    os.environ["ELFIE_CONFIG"] = elfieConfig

    loadEnvFromFile("../../application.yml")
    initializer = AppInitilizer()

    initializer.componentScan("elfie_modules.configs")
    initializer.componentScan("elfie_connectors")
    initializer.run()

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    assert elfie.agent is not None, "Not a valid agent configuration"

    ip_address = getContextEnvironment("host.address")
    if ip_address is None:
        ip_address = socket.gethostbyname(socket.gethostname())

    skipList = ['AbstractConnector', 'ElfieConfig', '__builtins__', '__cached__', '__doc__', '__file__',
                '__loader__', '__name__', '__package__', '__spec__']

    connectorPlugins = list(elfie.plugins.values())
    modules = map(lambda connector: importlib.import_module(connector.module), connectorPlugins)
    for plugin_index, module in enumerate(modules):
        connectorsList = filter(lambda x: x not in skipList, dir(module))
        for connector in connectorsList:
            classInstance = getattr(module, connector)
            if "__base__" not in dir(type(classInstance)):
                continue
            baseClass = '.'.join([classInstance.__base__.__module__, classInstance.__base__.__name__])
            if baseClass.endswith("backend.abstract.AbstractConnector"):

                objInstance = classInstance()
                plugin = connectorPlugins[plugin_index]
                objInstance.setConfig(elfie, plugin.configuration)

                logger.info(f"Found Connector {classInstance.__module__}.{classInstance.__name__} {objInstance.name()}")
                dispatcher[objInstance.name()] = objInstance.execute

    for func_name in FUNCTIONAL_CONNECTORS:
        function_info = FUNCTIONAL_CONNECTORS[func_name]
        logger.info(f"Found Functional Connector {func_name} {function_info['name']}")
        params = dict()
        for param_name, param_type in function_info['annotations'].items():
            object_type = ".".join([param_type.__module__, param_type.__name__])
            params[param_name] = getBeanObject(object_type)

        dispatcher[function_info['name']] = wrap(function_info['func'], params)

    host = getContextEnvironment("mqtt.host")
    port = int(getContextEnvironment("mqtt.port"))

    mqtt_client.connect(host, port)
    mqtt_client.loop_start()

    run_simple("0.0.0.0", 4000, application)
    # task_manager.join()

if __name__ == '__main__':
    start("../../elfieConfig.yml")