import os
from uuid import uuid4

from elfie_modules.phase_neurons.builder.pipeplugins import PythonScriptCommand
from elfie_modules.phase_neurons.taskmanager import TaskManager, Task
from elfie_modules.phase_neurons.builder import ProjectConfig, ProjectTypes, ProjectLifeCycleName, ProjectLifecycle, \
    MavenInstallCommand
from elfie_modules.pipeline import BOT_SPEAK


class BuildProject:
    def __init__(self, elfieConfigDir):
        super(BuildProject, self).__init__()
        self.elfieConfig = os.path.join(elfieConfigDir, "elfieConfig.yml")
        self.projectConfig = ProjectConfig.loadProjectConfig(self.elfieConfig)
        self.wd = elfieConfigDir
        self.pipeInstances = []

    def buildProject(self):
        build_lifecycle = self.projectConfig.lifecycle[ProjectLifeCycleName.BUILD.name]
        for pipeElement in build_lifecycle['pipeline']:
            modules = pipeElement['_module'].split('.')
            moduleInstance = __import__(modules[0])
            for module in modules[1:]:
                moduleInstance = getattr(moduleInstance, module)

            classInstance = getattr(moduleInstance, pipeElement['_class'])
            objInstance = classInstance()
            for key, value in pipeElement.items():
                setattr(objInstance, key, value)
            objInstance.execute()
            self.pipeInstances.append(objInstance)

    def schedule(self, callback=None) -> None:
        for taskCmd in self.pipeInstances:
            task = Task(cmd=taskCmd.finalCommand, shell=taskCmd.isShellCommand)
            if callback is not None:
                task.onExit(lambda *x: callback(*x))
            task.setExecutionDir(self.wd)
            TaskManager.addTask(task)


if __name__ == "__main__":
    output_dir = "D:/test/project"
    filename = "test.py"
    config = ProjectConfig(output_dir,name="Test Project", hasGit=False, project_id=uuid4().__str__())
    buildLifecycle = ProjectLifecycle(ProjectLifeCycleName.BUILD)
    buildLifecycle.addPipeCommand(PythonScriptCommand(cmd=[filename]))
    config.addLifeCycle(buildLifecycle)
    config.toProjectConfig(output_dir)


    project = BuildProject(output_dir)
    project.buildProject()
    project.schedule()
    print(project.pipeInstances)