from elfie_modules.backend.abstract import AbstractConnector, functionalconnector
from elfie_modules.backend.connectors import BUILD_PROJECT, LIST_PROJECT
from elfie_modules.backend.rpcClient import request
from elfie_modules.phase_neurons.builder.project import BuildProject
from elfie_modules.phase_neurons.config import ElfieConfig
from elfie_modules.pipeline import BOT_SPEAK

def processProjectBuild(project, task, status):
    if status == "success":
        request(BOT_SPEAK, params=[f"Build completed for project {project.projectConfig.name}"])
    elif status == "failed":
        request(BOT_SPEAK, params=[f"Their was an error while building the project {project.projectConfig.name},"
                                   f" I will this incident in error logs"])

@functionalconnector("test_function")
def testFunction(config: ElfieConfig):
    print("WORKED",config)
    return "WORKED"

@functionalconnector(BUILD_PROJECT)
def buildProject(project_id, config: ElfieConfig):
    projectPath = config.projects[project_id].projectPath
    project = BuildProject(projectPath)
    project.buildProject()
    project.schedule(callback=lambda *x: processProjectBuild(project,x[0],x[1]))

@functionalconnector(LIST_PROJECT)
def listProjects(config:ElfieConfig):
    return dict((config.name, config.project_id) for config in config.projects.values())