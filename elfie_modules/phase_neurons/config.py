import logging
import os

from elfie_modules.backend.channels import Credentials
from elfie_modules.backend.connectors.jenkins_connectors import ElfieJenkinsConnector
from elfie_modules.phase_neurons.builder.project import ProjectTypes, ProjectConfig
from elfie_modules.phase_neurons.elfie import loadyaml, dumpyaml

class JenkinsChannel:
    @staticmethod
    def name():
        return "jenkins"

    def __init__(self, data):
        self.jenkinsConnector = ElfieJenkinsConnector(data['url'], credentials=Credentials(**data['credentials']))

class ElfiePlugins:
    CONNECTOR='connector'
    def __init__(self, name, module, type):
        self.name = name
        self.module = module
        self.type = type

class ElfieConfig:
    ELFIE_CONFIG="ELFIE_CONFIG"
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

    def loadPlugins(self):
        if "plugins" not in self.data:
            return False
        self.plugins = dict(map(lambda x: (x['name'],ElfiePlugins(x['name'], x['module'], ElfiePlugins.CONNECTOR)),self.data['plugins']['connectors']))


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
            if JenkinsChannel.name() in channels:
                self.channels.append(JenkinsChannel(channels[JenkinsChannel.name()]))

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
                    except Exception as e:
                        logging.error(f"Exception loading project {root}")
                        continue

                for item in self.ignoreList:
                    if item in root:
                        dirs[:] = []
                        files[:] = []