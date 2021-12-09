from cndi.annotations import Bean

from elfie_modules.backend.zoo import ElfieZookeeper
from elfie_modules.phase_neurons.config import ElfieConfig
from elfie_modules.phase_neurons.taskmanager import TaskManager
from paho.mqtt.client import Client
import os
from elfie_modules.phase_neurons.elfie import loadyaml
from pymongo import MongoClient

@Bean()
def getTaskManager(elfie: ElfieConfig)->TaskManager:
    task_manager = TaskManager(elfie.agent)
    task_manager.start()
    return task_manager

@Bean()
def getMqttClient(elfie: ElfieConfig)->Client:
    client = Client()
    return client

@Bean()
def getElfieZookeeper(elfie: ElfieConfig)->ElfieZookeeper:
    return ElfieZookeeper(elfie.nodeId, hosts=elfie.zookeeper['servers'])

@Bean()
def getMongoClient(elfie: ElfieConfig)->MongoClient:
    mongo_client = MongoClient(elfie.db['connectionString'])
    return mongo_client

@Bean()
def loadConfig()->ElfieConfig:
    configpath = os.path.join(os.getcwd(), "elfieConfig.yml")
    ELFIE_CONFIG = "ELFIE_CONFIG"
    print("Using elfieConfig from ", configpath, os.path.exists(configpath))
    if(not os.path.exists(configpath) and ELFIE_CONFIG in os.environ):
        configpath = os.environ[ELFIE_CONFIG]
    elif not os.path.exists(configpath):
        raise FileNotFoundError("Coundnot find elfieConfig.yml")

    data = loadyaml(configpath)
    elfieConfig = ElfieConfig(data=data, loadProjects=True)
    return elfieConfig

