class AbstractTemplate:
    def __init__(self, cmd = [], isShellCommand=False):
        self.cmd = cmd
        self.finalCommand = None
        self.isShellCommand = isShellCommand

    def execute(self):
        self.finalCommand = self.cmd

class MavenTemplate(AbstractTemplate):
    def name(self):
        return "maven_template"

    def __init__(self):
        super(MavenTemplate, self).__init__(cmd = ['mvn'], isShellCommand=True)
        self.artifactId = "test"
        self.groupId = "ior"

    def setProperties(self, **kwargs):
        for key, value in kwargs:
            setattr(self, key, value)

    def execute(self):
        self.finalCommand = self.cmd + ["-B", "archetype:generate", f"-DarchetypeGroupId=org.apache.maven.archetypes",
             "-DarchetypeArtifactId=maven-archetype-simple", f"-DgroupId={self.groupId}",
             f"-DartifactId={self.artifactId}", "-DinteractiveMode=false"]

