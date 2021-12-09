import enum
import os

from elfie_modules.phase_neurons.builder.pipeplugins import MavenInstallCommand
from elfie_modules.phase_neurons.elfie import loadyaml, dumpyaml

class ProjectTypes(enum.Enum):
    NOT_SPECIFIED=0
    MAVEN=1
    NODE=2
    REACTJS=3
    REACTNATIVE=4
    CMAKE=5
    PYTHON_ML=6

class ProjectLifeCycleName(enum.Enum):
    CREATE=0
    BUILD=1
    TEST=2
    DEPLOY=3
    RUN=4

class ProjectLifecycle:
    def __init__(self, lifecycleName):
        self.name = lifecycleName if isinstance(lifecycleName, str) else lifecycleName.name
        self.pipeline = []

    def addPipeCommand(self, command):
        if isinstance(command, dict):
            self.pipeline.append(command)
        elif isinstance(command, object):
            dictObj = {
                "_module": command.__class__.__module__,
                "_class": command.__class__.__name__,
                **command.__dict__,
                "finalCommand": None
            }
            self.pipeline.append(dictObj)
        else:
            raise Exception("Not a valid pipe command of type: ", type(command))

class ProjectConfig:
    def __init__(self,root, name=None, projectType=ProjectTypes.NOT_SPECIFIED, hasGit=False, project_id=None):
        assert project_id is not None, "Project ID cannot be NULL"
        if not os.path.exists(root):
            os.makedirs(root)

        self.name = name
        self.project_id = project_id
        self.lifecycle = dict()
        self.projectPath = root
        self.projectType = projectType.name
        self.hasGit = hasGit

    def addLifeCycle(self, lifecycle):
        if isinstance(lifecycle, dict):
            self.lifecycle[lifecycle.name] = lifecycle
        elif isinstance(lifecycle, object):
            dictObj = {
                "_module": lifecycle.__class__.__module__,
                "_class": lifecycle.__class__.__name__,
                **lifecycle.__dict__,
            }
            self.lifecycle[lifecycle.name] = dictObj

    @staticmethod
    def loadProjectConfig(absolutePath):
        dictionary = loadyaml(absolutePath)
        if "elfieAgent" in dictionary:
            raise Exception("Not a valid project, should be instanciated with ElfieConfig")
        config = ProjectConfig(os.path.dirname(absolutePath), project_id=dictionary['project_id'])
        for key, value in dictionary.items():
            setattr(config, key, value)
        return config

    def toProjectConfig(self, absoultePath):
        if not os.path.exists(absoultePath):
            os.makedirs(absoultePath)
        dumpyaml(self.__dict__, os.path.join(absoultePath, "elfieConfig.yml"))