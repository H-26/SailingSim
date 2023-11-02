import platform
import os
import json

default = '{"wind":}'

def checkSettings(json):
    if json == default

match platform.system():
    case "Linux":
        path = "/home/" + os.getlogin() + "/.config/SailingSim/settings.json"
    case "Darwin":
        path = "/Users/" + os.getlogin() + "/Library/Application Support/SailingSim/settings.json"
    case "Windows":
        path = "\\Users\\" + os.getlogin() + "\\AppData\\Local\\SailingSim\\settings.json"

