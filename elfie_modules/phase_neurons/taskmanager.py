import subprocess
import time, os
import threading
from queue import Queue
import uuid
from uuid import uuid4

import paho.mqtt.client as mqtt
import datetime
import json
import os
import logging

from cndi.env import getContextEnvironment

from elfie_modules.backend.connectors import ERROR_ADDERROR
from elfie_modules.backend.elfie_dataclasses import ErrorModel
from elfie_modules.backend.rpcClient import request
from elfie_modules.pipeline import BOT_SPEAK


class Task:
    def __init__(self, cmd, shell=False, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE, stdin = subprocess.PIPE):
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin
        self.cmd = cmd
        self.isShell = shell
        self.onExitMethod = None
        self.tid = uuid.uuid4().__str__()
        self.wd = os.getcwd()
        self.setExecutionDir(self.wd)
        self.pid = None

    def setExecutionDir(self, wd):
        self.executionDir = wd

    def onExit(self, function):
        self.onExitMethod = function

    def getProcess(self):
        return self.process

def pipeWatcher(stream, queue):
    while not stream.closed:
        line = stream.readline()
        if line != b'':
            queue.put(line)

        time.sleep(0.001)

class Executor:
    def __init__(self, queue, agent_uid):
        self.process = threading.Thread(target=self.execute, args=(queue, ))
        self.executorId = uuid4().__str__()
        self.process.start()
        self.current_task_id = None
        self.agentUid = agent_uid
        self.running = False

    def execute(self, queue) -> None:
        time.sleep(4)
        logging.info("Executor Running")
        while True:
            self.running = True
            task_id = queue.get()
            if task_id is not None:
                task = TaskManager.tasks[task_id]
                startupinfo = subprocess.STARTUPINFO()
                TaskManager.mqtt_client.publish("agent/task/build_started", json.dumps({
                    "task_id": task.tid,
                    "timestamp": datetime.datetime.now().timestamp().__str__(),
                    "agent": self.agentUid
                }))
                os.chdir(task.executionDir)
                process = subprocess.Popen(task.cmd, startupinfo=startupinfo, shell=task.isShell,
                                           stdout=task.stdout, stderr=task.stderr)

                TaskManager.tasks[task_id].pid = process.pid
                TaskManager.processes[process.pid] = process

                self.current_task_id = task.tid
                returncode = process.poll()
                out_queue = Queue()
                err_queue = Queue()

                out_thread = threading.Thread(target=pipeWatcher, args=(process.stdout, out_queue))
                out_thread.start()

                err_thread = threading.Thread(target=pipeWatcher, args=(process.stderr, err_queue))
                err_thread.start()
                err_list = list()
                out_list = list()

                while returncode is None or (out_queue.qsize() > 0 or err_queue.qsize() > 0):
                    returncode = process.poll()
                    if not out_queue.empty():
                        line = out_queue.get().decode()
                        if 'ERROR' in line:
                            err_list.append(line)
                        print(line, end="")
                    if not err_queue.empty():
                        err_list.append(err_queue.get().decode())

                    time.sleep(0.2)
                os.chdir(task.wd)

                process.stdout.close()
                process.stderr.close()

                if len(err_list) > 0:
                    error_message = ''.join(err_list)
                    error_model = ErrorModel("Exception", error_message, "EXCEPTION_TASK",
                                             {"task_id": task.tid}, time.time(), uuid4().__str__())
                    request(ERROR_ADDERROR, params=[error_model.__dict__])

                TaskManager.mqtt_client.publish("agent/task/build_completed", json.dumps({
                    "task_id": task.tid,
                    "timestamp": datetime.datetime.now().timestamp().__str__(),
                    "agent": self.agentUid
                }))

                del TaskManager.processes[process.pid]

                if task.onExitMethod is not None:
                    task.onExitMethod(task, "success" if len(err_list) == 0 else "failed")

                self.current_task_id = None
            time.sleep(1)
        self.running = False
        logging.warn("Exiting Executor Thread")
        return None

class TaskManager(threading.Thread):
    tasks = dict()
    executors = list()
    desired_executors = 2
    processes = dict()
    queue = Queue()
    mqtt_client = mqtt.Client()
    uid = None

    def __init__(self):
        super(TaskManager, self).__init__()
        TaskManager.uid = uuid4().__str__()
        logging.info(self.uid)

        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        mqttHost = getContextEnvironment("mqtt.host")
        mqttPort = int(getContextEnvironment("mqtt.port"))
        self.mqtt_client.connect(mqttHost, mqttPort)


    def on_mqtt_connect(self, client: mqtt.Client, userdata, flags, rc):
        logging.info("Connected with result code "+str(rc))

    def on_mqtt_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        logging.info(f"Topic {msg.topic} {msg.payload}")

    @staticmethod
    def addTask(task):
        logging.info("Adding Task " + task.tid)
        TaskManager.tasks[task.tid] = task
        TaskManager.queue.put(task.tid)
        TaskManager.mqtt_client.publish("agent/task/build_queue", json.dumps({
            "task_id": task.tid,
            "timestamp": datetime.datetime.now().timestamp().__str__(),
            "agent": TaskManager.uid
        }))



    def killTask(self, tid):
        if tid in self.tasks:
            self.processes[self.tasks[tid].pid].kill()

    @staticmethod
    def getTasks():
        return list(TaskManager.tasks.values())

    def run(self) -> None:
        while True:
            self.executors = list(filter(lambda x: x.running, self.executors))

            count = self.desired_executors - len(self.executors)
            for i in range(count):
                executor = Executor(self.queue, self.uid)
                logging.info(f"Running Executor {executor.executorId}")
                self.executors.append(executor)
            time.sleep(10)

if __name__ == "__main__":
    task_manager = TaskManager()
    task_manager.start()
    for _ in range(5):
        task = Task(cmd=["ls", "-l"], shell=True)
        task.onExit(lambda x: print("Exited"))
        task_manager.addTask(task)
    task_manager.join()