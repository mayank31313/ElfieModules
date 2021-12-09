from yaml import load, Loader, dump, Dumper
import os

def dumpyaml(dictionary, path):
    output = dump(dictionary, Dumper=Dumper)
    with open(path, "w") as stream:
        stream.write(output)

def loadyaml(configpath):
    assert os.path.exists(configpath), f"'{configpath}' not found"
    with open(configpath, "r") as file:
        data = load(file, Loader=Loader)
    return data
