from cndi.annotations import Bean

from elfie_modules.phase_neurons.config import ElfieConfig
from elfie_modules.phase_neurons.taskmanager import TaskManager
from paho.mqtt.client import Client
import os
from elfie_modules.phase_neurons.elfie import loadyaml

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
def loadConfig()->ElfieConfig:
    configpath = os.path.join(os.getcwd(), "elfieConfig.yml")
    ELFIE_CONFIG = "ELFIE_CONFIG"
    print("Using elfieConfig from ", configpath, os.path.exists(configpath))
    if(not os.path.exists(configpath) and ELFIE_CONFIG in os.environ):
        configpath = os.environ[ELFIE_CONFIG]
    elif not os.path.exists(configpath):
        raise FileNotFoundError("Coundnot find elfieConfig.yml")

    data = loadyaml(configpath)
    if isinstance(data, list):
        if ElfieConfig.ELFIE_ENV not in os.environ:
            raise NotImplementedError(f"{ElfieConfig.ELFIE_ENV} not set")
        data = list(filter(lambda x: x['activeEnvironment'] == os.environ[ElfieConfig.ELFIE_ENV], data))[0]

    elfieConfig = ElfieConfig(data=data, loadProjects=True)
    return elfieConfig