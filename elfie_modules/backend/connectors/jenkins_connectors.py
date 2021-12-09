import jenkins
from elfie_modules.backend.channels import Credentials
from elfie_modules.backend.abstract import AbstractConnector
from elfie_modules.backend.connectors import JENKINS_BUILD_JOB, JENKINS_LIST_PIPELINES, JENKINS_LIST_BUILD_JOB

JENKINS_PROJECTS = dict()

class ElfieJenkinsConnector:
    def __init__(self, url, credentials: Credentials):
        self.jenkins_instance = jenkins.Jenkins(url, username=credentials.secret_key, password=credentials.secret_value)

    def build_project(self, project_name):
        self.jenkins_instance.build_job(project_name)

    def getPipelines(self):
        jobs = self.jenkins_instance.get_jobs()
        for job in jobs:
            JENKINS_PROJECTS[job['name']] = job
        return JENKINS_PROJECTS

    def getRunningBuilds(self):
        return self.jenkins_instance.get_running_builds()

class JenkinsListProjects(AbstractConnector):
    def name(self):
        return JENKINS_LIST_PIPELINES

    def execute(self, *args):
        return self.channel.jenkinsConnector.getPipelines()

class JenkinsListCurrentBuilds(AbstractConnector):
    def name(self):
        return JENKINS_LIST_BUILD_JOB

    def execute(self, *args):
        return self.channel.jenkinsConnector.getRunningBuilds()

class JenkinsBuildProjectConnector(AbstractConnector):
    def name(self):
        return JENKINS_BUILD_JOB

    def execute(self, *args):
        self.channel.jenkinsConnector.build_project(args[0])