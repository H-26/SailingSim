running = True
loading = True
# Imports
import pygame, threading, time, sys
import settings
import numpy as np
from boat import Boat
from map import Map
import wind

# Setup
pygame.init()

# Window initiation
screen = pygame.display.set_mode((settings.screenWidth, settings.screenHeight), pygame.RESIZABLE)

pygame.display.set_caption("SailingSim")
icon = pygame.image.load("Assets/Boat.png")  # To change Icon
pygame.display.set_icon(icon)
print("setup display")

# Start the event loop
pygame.event.pump()

# Loading screen
fontSize = 30
font = pygame.font.Font(None, fontSize)
screenSize = pygame.display.get_surface().get_size()

def loadingScreen():
    timeElapsed = 0
    while loading:
        screen.fill((41, 74, 143))
        loadingMessage = "Sailing Sim by Joseph Henderson"  # Create a loading message
        loadingText = font.render(loadingMessage, True, (255, 255, 255))
        screen.blit(loadingText, (screenSize[0] // 2 - loadingText.get_width() // 2, screenSize[1] // 2 - 65 // 2))
        pygame.display.update()
        time.sleep(0.01)
    # screen.fill((0, 0, 0))  # Fill the screen with black
    # for i in range(0, 255, 5):
    #     loadingMessage = "Joseph Henderson Presents:"  # Create a loading message
    #     loadingText = font.render(loadingMessage, True, (i, i, i))  # Create a text surface
    #     screen.blit(loadingText, (settings.screenWidth // 2 - loadingText.get_width() // 2, settings.screenHeight // 2 - 65 // 2))  # Blit the text surface onto the screen
    #     pygame.display.update()  # Update the display
    #     time.sleep(0.01)
    # for i in range(0, 255, 5):
    #     loadingMessage = "Sailing Sim"  # Create a loading message
    #     loadingText = font.render(loadingMessage, True, (i, i, i))  # Create a text surface
    #     screen.blit(loadingText, (settings.screenWidth // 2 - loadingText.get_width() // 2,settings.screenHeight // 2 - 25 // 2))  # Blit the text surface onto the screen
    #     pygame.display.update() # Update the display
    #     time.sleep(0.01)
    timeElapsed += 1

threading.Thread(target=loadingScreen).start()

scale = settings.scale
keys = pygame.key.get_pressed()

# Debug tick to print variables
def debugtick():
    if running:
        print("================================")
        print("Scale:", settings.scale)
        # print("Boat Angle to Wind:", player.boatAngleToWind)
        # print("Boat Angle:", player.angle)
        # print("Wind Angle:", player.wind[1])
        # print("Pos X:", player.posx)
        # print("Pos Y:", player.posy)
        # print("Tack:", player.tack)
        # print("Sail Angle to Wind:", player.sailAngleToWind)
        # print("Starboard Boat angle", (player.angle + player.wind[1]) % 360)
        # print("Acceleration:", player.acceleration())
        # print("Speed:a", player.speed)
        # print("Speed X:", player.speedx)
        # print("Speed Y:", player.speedy)
        # print("Angular Velocity", player.angularVelocity)
        # print("Wind Speed:", wind.localWind(player.posx, player.posy)[0])
        time.sleep(1)

# Tick to update at regular intervals regardless of framerate
def tick():
    if running:
        global keys
        # Get the current scale from the settings
        # windSurface = drawWind(settings.scale)
        # # Scroll the wind surface down by 1 pixel
        # windSurface.scroll(dy=-1)
        # # If the edge of the surface is reached
        # # Scale the surface based on the scale setting
        # windSurface = pygame.transform.scale(windSurface, (int(pygame.display.get_surface().get_size()[0] * scale),
        #                                                      int(pygame.display.get_surface().get_size()[1] * scale)))
        time.sleep(0.05)

# Player
player = Boat()

# Map
map = Map("Test Map")

# windSurface = wind.createWindSurface(pygame.display)
threading.Thread(target=tick).start()
threading.Thread(target=debugtick).start()
loading = False
font = pygame.font.Font(None, 14)
lastFrameTime = pygame.time.get_ticks()
lastUpdateTime = 50
prev_posx = player.posx
prev_posy = player.posy# Store the player's previous position

# Game loop
while running:
    # Get the current time
    currentTime = pygame.time.get_ticks()

    # Check for events
    for event in pygame.event.get():
        # Check if quit button pressed and quit
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                settings.centerBoat = not settings.centerBoat  # Toggle centerBoat when 'C' key is pressed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 5:
                player.trimSail(-1)
            elif event.button == 4:
                player.trimSail(1)

    keys = pygame.key.get_pressed()
    screenSize = pygame.display.get_surface().get_size()

    settings.scale = np.clip((settings.scale + (keys[pygame.K_EQUALS] - keys[pygame.K_MINUS])*0.01), 0.06, 0.3)

    # Calculate the time difference
    dt = (currentTime - lastFrameTime) / 1000.0  # Convert to seconds

    # Calculate the FPS
    if dt > 0:
        fps = 1.0 / dt
    else:
        fps = 0

    lastFrameTime = currentTime

    # Check if 0.05 seconds have passed since the last update
    if currentTime - lastUpdateTime >= 50:  # 0.05 seconds = 50 milliseconds
        factor = currentTime - lastUpdateTime/50
        # Store the player's current position before updating
        prev_posx = player.posx
        prev_posy = player.posy
        # Update the player
        player.update(keys, factor)
        # Create the HUD
        HUDText = ["X: {}, Y: {}".format(round(player.posx, 0), round(player.posy, 0)),
                   "Speed: {}".format(round(player.speed, 1)),
                   "Wind Speed: {}".format(round(wind.localWind(player.posx, player.posy)[0], 1)),
                   "Wind Angle: {}".format(round(wind.localWind(player.posx, player.posy)[1], 1)),
                   "Boat Angle: {}".format(round(player.angle, 1)),
                   "Boat Angle to Wind: {}".format(round(player.boatAngleToWind, 1)),
                   "Sail Angle to Wind: {}".format(round(player.sailAngleToWind, 1)),
                   "Acceleration: {}".format(round(player.acceleration, 1)), "Tack: {}".format(player.tack),
                   "FPS: {}".format(round(fps, 1))]
        HUD = []
        for line in HUDText:
            HUD.append(font.render(line, True, (255, 255, 255)))
        # Update the last update time
        lastUpdateTime = currentTime

    # Calculate the interpolation factor
    t = (currentTime - lastUpdateTime) / 50.0

    # Calculate the interpolated position
    interpolated_posx = prev_posx + t * (player.posx - prev_posx)
    interpolated_posy = prev_posy + t * (player.posy - prev_posy)

    # Draw the screen
    screen.fill((41, 74, 143))
    width, height = pygame.display.get_surface().get_size()
    # wind.draw(screen, screenSize, interpolated_posx, interpolated_posy)
    player.draw(screen, screenSize, interpolated_posx, interpolated_posy)
    # map.draw(screen, screenSize, interpolated_posx, interpolated_posy)
    for textSurface in enumerate(HUD):
        screen.blit(textSurface[1], (0, screenSize[1] - ((textSurface[0] + 1) * 15)))

    # Update screen
    pygame.display.update()

# Quit
pygame.quit()
sys.exit()