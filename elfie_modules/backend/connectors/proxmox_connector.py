import os

from proxmoxer import ProxmoxAPI

from elfie_modules.backend.abstract import functionalconnector, AbstractConnector
from elfie_modules.backend.channels import Credentials
from elfie_modules.backend.connectors import PROXMOX_STATUS


class ElfieProxmoxConnector:
    def __init__(self,url ,credentials: Credentials):

        self.proxmox = ProxmoxAPI(url, user=credentials.secret_key,
                                           token_name=credentials.token, token_value=credentials.secret_value,
                             verify_ssl=False,  service='PVE')

    def getKubernetesMasterState(self):
        kubernetes_master_vm_id = "109"
        return self.proxmox.get("nodes", self.cloudName, "qemu", kubernetes_master_vm_id, "status", "current")

    def shutdownVM(self, vm_id):
        return self.proxmox.post("nodes", self.cloudName, "qemu", vm_id, "status", "shutdown")
    def startVM(self, vm_id):
        return self.proxmox.post("nodes", self.cloudName, "qemu", vm_id, "status", "start")

    @property
    def cloudName(self):
        return "iorcloud"

class ProxmoxStatus(AbstractConnector):
    def name(self):
        return PROXMOX_STATUS

    def execute(self, *args):
        return self.channel.proxmoxConnector.getKubernetesMasterState()