from yaml import load, Loader, dump, Dumper, load_all, SafeLoader
import os

def dumpyaml(dictionary, path):
    output = dump(dictionary, Dumper=Dumper)
    with open(path, "w") as stream:
        stream.write(output)

def loadyaml(configpath, single=False):
    assert os.path.exists(configpath), f"'{configpath}' not found"
    with open(configpath, "r") as file:
        if single:
            data = load(file, Loader=SafeLoader)
        else:
            data = list(load_all(file, Loader=SafeLoader))
    return data