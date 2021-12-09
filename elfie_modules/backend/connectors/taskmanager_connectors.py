from uuid import uuid4

from elfie_modules.backend.abstract import functionalconnector
from elfie_modules.backend.connectors import TASKMANAGER_ADD_TASK, TASKMANAGER_LIST_TASK_IDS, \
    TASKMANAGER_CREATE_PROJECT, TASKMANAGER_BUILD_PROJECT
from elfie_modules.phase_neurons.builder import ProjectConfig, ProjectLifecycle, ProjectLifeCycleName
from elfie_modules.phase_neurons.builder.pipeplugins import PythonScriptCommand, SimpleCommand
from elfie_modules.phase_neurons.builder.project import BuildProject
from elfie_modules.phase_neurons.taskmanager import TaskManager, Task
import os

@functionalconnector(TASKMANAGER_CREATE_PROJECT, ignoreParams=["project_info"])
def taskmanager_create_project(project_info:dict):
    project_name = project_info['projectName']
    project_config = ProjectConfig(os.path.join("D:/test_project", project_name), project_id=uuid4().__str__())

    lifecycle = ProjectLifecycle(ProjectLifeCycleName.BUILD)
    lifecycle.addPipeCommand(SimpleCommand(cmd=["ls", "-l"], isShellCommand=True))
    project_config.addLifeCycle(lifecycle)
    project_config.toProjectConfig(os.path.join("D:/test_project", project_name))

    return project_config.project_id

@functionalconnector(TASKMANAGER_BUILD_PROJECT, ignoreParams=['project_info'])
def taskmanager_build_project(project_info: dict):
    projectId = project_info['projectId']
    project = BuildProject("D:/test_project/Test")
    project.buildProject()
    project.schedule()
    print(project)

@functionalconnector(TASKMANAGER_ADD_TASK, ignoreParams=['task_info'])
def taskmanager_add_task(task_info, task_manager: TaskManager):
    cmd = task_info['cmd']
    isShell = task_info['isShell']

    task = Task(cmd=cmd, shell=isShell, stdout=None)
    task.onExit(lambda x: print("Task Completed"))
    task_manager.addTask(task)

    return task.tid

@functionalconnector(TASKMANAGER_LIST_TASK_IDS)
def taskmanager_list_ids():
    return list(TaskManager.tasks.keys())