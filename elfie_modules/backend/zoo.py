from kazoo.client import KazooClient, KazooState, KeeperState
import time

from kazoo.exceptions import NoNodeError
from kazoo.protocol.states import WatchedEvent, ZnodeStat, EventType
import re

PATH_TO_FUNCTION = dict()

def watch_children(ezk, path):
    previous_childrens = set()
    def nested_fn(childrens):
        absolute_path_children = set()
        for children in childrens:
            absolute_path = path + "/" + children
            absolute_path_children.add(absolute_path)
            if(absolute_path not in previous_childrens):
                ezk.zk.DataWatch(path + "/" + children, watch_data(ezk, absolute_path))
                ezk.zk.ChildrenWatch(path + "/" + children, watch_children(ezk, absolute_path))
                previous_childrens.add(absolute_path)


        for element in previous_childrens.difference(absolute_path_children):
            previous_childrens.remove(element)


    return nested_fn

def watch_data(ezk, path):
    def nested_fn(data, stat):
        if data is None and stat is None:
            watch_change(path, EventType.DELETED)
            return

        if data is b'' and stat.ctime == stat.mtime:
            watch_change(path[0:path.rindex("/")], EventType.CHILD)
            watch_change(path, EventType.CREATED)
            return

        if data is not None and stat.ctime != stat.mtime:
            watch_change(path, EventType.CHANGED)
            return

        print(f"Data Changed {path} {data}, {stat}")
    return nested_fn

def watch_change(path, type):
    keyset = filter(lambda x: re.match(x, path) is not None, PATH_TO_FUNCTION.keys())
    for key in keyset:
        PATH_TO_FUNCTION[key](path, type)

class ElfieZookeeper:
    def __init__(self, id, hosts):
        self.zk = KazooClient(hosts=hosts)
        self.zk.start()
        self.zk.ChildrenWatch("/elfie", watch_children(self, "/elfie"))
        self.setData(f"/elfie/agents/{id}", b'')

    def recurse(self, path):
        paths = []
        childrens = self.zk.get_children(path)
        for children in childrens:
            paths.append(path + "/" + children)
            paths.extend(self.recurse(path + "/" + children))
        return paths

    def setData(self, path, data):
        self.zk.ensure_path(path)
        self.zk.set(path, data)

    def getData(self, path):
        return self.zk.get(path)

    def register(self, path, fn):
        PATH_TO_FUNCTION[path] = fn

    def deleteTree(self, path):
        for node in sorted(filter(lambda x : x.startswith(path), self.recurse("/elfie")), reverse=True):
            self.zk.delete(node)

    def deleteElfieNodes(self):
        self.deleteTree("/elfie")

    def stop(self):
        self.zk.stop()

if __name__ == "__main__":
    zk = ElfieZookeeper(3)
    zk.register("/elfie/*", lambda path, type: print(path, type))
    zk.setData("/elfie/server/server1", b"HEY")
    print(zk.getData("/elfie/server/server1"))
    time.sleep(10)
    zk.deleteElfieNodes()
    time.sleep(4)
    zk.stop()
