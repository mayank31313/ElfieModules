import logging
import os, sys

import requests

from elfie_modules.backend.channels import Credentials
from elfie_modules.backend.connectors.jenkins_connectors import ElfieJenkinsConnector
from elfie_modules.backend.connectors.proxmox_connector import ElfieProxmoxConnector
from elfie_modules.backend.connectors.weather_connectors import ElfieWeatherApiConnector
from elfie_modules.phase_neurons.builder import ProjectTypes
from elfie_modules.phase_neurons.builder.project import ProjectConfig
from elfie_modules.phase_neurons.elfie import loadyaml, dumpyaml

class JenkinsChannel:
    @staticmethod
    def name():
        return "jenkins"

    def __init__(self, data):
        self.jenkinsConnector = ElfieJenkinsConnector(data['url'], credentials=Credentials(**data['credentials']))

class ProxmoxChannel:
    @staticmethod
    def name():
        return "proxmox"

    def __init__(self, data):
        self.proxmoxConnector = ElfieProxmoxConnector(data['url'], credentials=Credentials(**data['credentials']))

class OpenWeatherMapAPIChannel:
    @staticmethod
    def name():
        return "openweatherapi"

    def __init__(self, data):
        self.apiConnector = ElfieWeatherApiConnector(credentials=Credentials(**data['credentials']))


class ElfiePlugins:
    CONNECTOR='connector'
    def __init__(self, name, module, type, configuration=None, basePath=None):
        self.name = name
        self.module = module
        self.type = type
        self.configuration = configuration
        if basePath is not None:
            print("Adding Path: ", basePath)
            sys.path.append(basePath)



class ElfieConfig:
    ELFIE_CONFIG="ELFIE_CONFIG"
    ELFIE_ENV="ELFIE_ENV"

    def __init__(self, data, loadProjects):
        self.loadProjects = loadProjects
        self.data = data
        self.loadConfig(data)
        self.nodeId = data['nodeId']
        self.plugins = {}

        if loadProjects:
            self.mavenProjects = []
            self.ignoreList = [".git", "node_modules", "target"]
            self.projects = dict()
            self.loadProjectDirs()
            print("Projects Loaded")
        self.loadPlugins()

    def resolvePlugins(self, plugins):
        localPlugins = list(filter(lambda plugin: 'configYaml' not in plugin or plugin['configYaml'] == '', plugins))
        externalPlugins = filter(lambda plugin: not ('configYaml' not in plugin or plugin['configYaml'] == ''),
                                 plugins)
        for externalPlugin in externalPlugins:
            localPlugins.extend(self.resolveExternalPlugins(externalPlugin))
        return localPlugins

    def resolveExternalPlugins(self, plugin: dict):
        configYaml = str(plugin['configYaml'])

        returnPlugins = list()
        if configYaml.startswith("http") or configYaml.startswith("https"):
            response = requests.get(configYaml)
            yamlData = response.text
            raise NotImplementedError("Working on this part of the application")

        elif configYaml.startswith("file://"):
            fileName = configYaml[7:]
            if not os.path.exists(fileName):
                raise FileNotFoundError(f"Config file not found at location: {fileName}")
            plugins = loadyaml(fileName)[0]
            plugins = list(map(lambda x: {
                **x,
                "name": f"{plugin['name']}.{x['name']}"
            }, plugins))
            returnPlugins.extend(plugins)

        return returnPlugins


    def loadPlugins(self):
        if "plugins" not in self.data:
            return False

        connectorPlugins = self.data['plugins']['connectors']
        connectorPlugins = self.resolvePlugins(connectorPlugins)

        self.plugins = dict(map(lambda x: (x['name'],
                                           ElfiePlugins(type=ElfiePlugins.CONNECTOR, **x)
                                           ),connectorPlugins))


    def loadConfig(self, data):
        self.name = data['name']
        self.projectsDir = data['projectsDir']
        self.db = data['db'] if 'db' in data else None
        self.rpc = data['rpcConfig'] if 'rpcConfig' in data else None
        self.agent = data['elfieAgent'] if 'elfieAgent' in data else None
        self.zookeeper = data['zookeeper'] if 'zookeeper' in data else None
        self.mavenConfig = data['mavenTemplate']

        channels = data['channels'] if 'channels' in data else None
        self.channels = list()
        if channels is not None:
            classList = [JenkinsChannel, ProxmoxChannel, OpenWeatherMapAPIChannel]
            for classObject in classList:
                if classObject.name() in channels:
                    self.channels.append(classObject(channels[classObject.name()]))

            # if JenkinsChannel.name() in channels:
            #     self.channels.append(JenkinsChannel(channels[JenkinsChannel.name()]))
            # if ProxmoxChannel.name() in channels:
            #     self.channels.append(ProxmoxChannel(channels[ProxmoxChannel.name()]))
            # if OpenWeatherMapAPIChannel.name() in channels:
            #     self.channels.append(OpenWeatherMapAPIChannel(channels[OpenWeatherMapAPIChannel.name()]))

        if "load_projects" in data:
            self.loadProjects = self.loadProjects or data['load_projects']

    def loadProjectDirs(self):
        for projectDir in self.projectsDir:
            for (root, dirs, files) in os.walk(projectDir, topdown=True):
                tempIgnoreList = self.ignoreList
                projectType=ProjectTypes.NOT_SPECIFIED
                project_id = None

                if "pom.xml" in files:
                    self.mavenProjects.append(root)
                    projectType = ProjectTypes.MAVEN
                if "package.json" in files:
                    projectType = ProjectTypes.NODE
                if ".gitignore" in files:
                    with open(os.path.join(root, ".gitignore"), "r") as stream:
                        tempIgnoreList += stream.read().split("\r\n")

                if "elfieConfig.yml" in files:
                    absolute_path = os.path.join(root, "elfieConfig.yml")
                    try:
                        projectConfig = ProjectConfig.loadProjectConfig(absolute_path)
                        self.projects[projectConfig.project_id] = projectConfig
                        logging.info(f"Project loaded successfully: {projectConfig.name}")
                    except Exception as e:
                        logging.error(f"Exception loading project {root}")
                        continue

                for item in self.ignoreList:
                    if item in root:
                        dirs[:] = []
                        files[:] = []