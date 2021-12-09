from builtins import super


class SimpleCommand:
    def __init__(self, cmd=[], isShellCommand=False):
        self.cmd = cmd
        self.isShellCommand = isShellCommand

    def execute(self):
        self.finalCommand = self.cmd

class PythonScriptCommand(SimpleCommand):
    def __init__(self, cmd=[]):
        super(PythonScriptCommand, self).__init__(cmd=["python"] + cmd, isShellCommand=True)

    def execute(self):
        self.finalCommand = self.cmd

class MavenInstallCommand(SimpleCommand):
    def __init__(self):
        super(MavenInstallCommand, self).__init__(cmd=["mvn", "clean", "install"],
                                                  isShellCommand=True)


class MavenDeployCommand(SimpleCommand):
    def __init__(self):
        super(MavenDeployCommand, self).__init__(cmd=["mvn", "deploy"],
                                                 isShellCommand=True)

