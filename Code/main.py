# Imports
import numpy as np
import pygame, sys, threading
from boat import Boat
from map import Map
import settings
import wind

# Setup
pygame.init()

scale = settings.scale

# Window initiation

screen = pygame.display.set_mode((settings.screenWidth, settings.screenHeight), pygame.RESIZABLE)

pygame.display.set_caption("SailingSim")
icon = pygame.image.load("Assets/Boat.png")  # To change Icon
pygame.display.set_icon(icon)

keys = pygame.key.get_pressed()

# Debug tick to print variables
def debugtick():
    if running:
        print("================================")
        # print("Scale:", settings.scale)
        # print("Boat Angle to Wind:", player.boatAngleToWind)
        # print("Boat Angle:", player.angle)
        # print("Wind Angle:", player.wind[1])
        # print("Pos X:", player.posx)
        # print("Pos Y:", player.posy)
        # print("Tack:", player.tack)
        # print("Sail Angle to Wind:", player.sailAngleToWind)
        # print("Starboard Boat angle", (player.angle + player.wind[1]) % 360)
        print("Acceleration:", player.acceleration())
        print("Speed:", player.speed)
        print("Speed X:", player.speedx)
        print("Speed Y:", player.speedy)
        # print("Angular Velocity", player.angularVelocity)
        threading.Timer(1,debugtick).start()

# Tick to update at regular intervals regardless of framerate
def tick():
    if running:
        global keys
        # width, height = pygame.display.get_surface().get_size()
        player.update(keys)
        # for posx in range(width):
        #     for posy in range(height):
        #         print(0, 0, int(127.5 + wind.localWind(posx/2, posy/2)[0] * 10))
        #         screen.set_at((posx, posy), (0, 0, int(127.5 + wind.localWind(posx/2, posy/2)[0] * 10)))
        threading.Timer(0.05, tick).start()

# Player
player = Boat()

# Map
map = Map("Test Map")

running = True

tick()
debugtick()

# Game loop
while running:

    # Check for events
    for event in pygame.event.get():
        # Check if quit button pressed and quit
        if event.type == pygame.QUIT:
            running = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    player.trimSail(-1)
                elif event.button == 4:
                    player.trimSail(1)

    keys = pygame.key.get_pressed()
    screenSize = pygame.display.get_surface().get_size()

    settings.scale = np.clip((settings.scale + (keys[pygame.K_EQUALS] - keys[pygame.K_MINUS])*0.01), 0, 1)

    screen.fill((41, 74, 143))
    # for posx in range(width):
    #     for posy in range(height):
    #         print(0, 0, int(127.5 + wind.localWind(posx / 2, posy / 2)[0] * 10))
    #         screen.set_at((posx, posy), (0, 0, int(127.5 + wind.localWind(posx / 2, posy / 2)[0] * 10)))
    player.draw(screen, screenSize)
    map.draw(screen, screenSize)
    # Update screen
    pygame.display.update()

# Quit
pygame.quit()
sys.exit()