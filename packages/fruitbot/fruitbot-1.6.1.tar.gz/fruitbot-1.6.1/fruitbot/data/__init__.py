from os.path import join, dirname
from json import dump, load

def saveJson(data: dict, file_name: str):
    path = join(dirname(__file__), file_name)
    with open(path, "w") as file:
        dump(data, file)

def loadJson(file_name: str):
    path = join(dirname(__file__), file_name)
    with open(path, "r") as file:
        data = load(file)
    return data
