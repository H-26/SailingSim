import platform
import os
import json

centreScale = 0.1
mapScale = 0.06
scale = 0.1
screenWidth = 900
screenHeight = 700
centerBoat = True

default = '{"wind":}'

# def checkSettings(json):
#     if json == default
# # Check which platform is being used and set path accordingly
# match platform.system():
#     case "Linux":
#         path = "/home/" + os.getlogin() + "/.config/SailingSim/settings.json"
#     case "Darwin":
#         path = "/Users/" + os.getlogin() + "/Library/Application Support/SailingSim/settings.json"
#     case "Windows":
#         path = "\\Users\\" + os.getlogin() + "\\AppData\\Local\\SailingSim\\settings.json"

