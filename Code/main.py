running = True
loading = True
debug = False
# Imports
import pygame, threading, time, sys
import settings
import numpy as np
from boat import Boat
from map import Map
from wind import wind

# Setup
pygame.init()

# Window initiation
screen = pygame.display.set_mode((settings.screen_width, settings.screen_height), pygame.RESIZABLE)
pygame.mouse.set_visible(False)

pygame.display.set_caption("SailingSim")
icon = pygame.image.load("Assets/Icon.png")  # To change Icon
pygame.display.set_icon(icon)
print("setup display")

# Start the event loop
pygame.event.pump()

# Loading screen
fontSize = 30
font = pygame.font.Font(None, fontSize)
screen_size = pygame.display.get_surface().get_size()

def loadingScreen():
    timeElapsed = 0
    screen.fill((0, 0, 0))
    for i in range(0, 255, 2):
        loadingMessage = "Joseph Henderson Presents:"  # Create a loading message
        loadingText = font.render(loadingMessage, True, (i, i, i))  # Create a text surface
        screen.blit(loadingText, (settings.screen_width // 2 - loadingText.get_width() // 2, settings.screen_height // 2 - 65 // 2))  # Blit the text surface onto the screen
        pygame.display.update()  # Update the display
        screen.fill((0, 0, 0))
        time.sleep(0.01)
    for i in range(0, 255, 2):
        loadingMessage = "Joseph Henderson Presents:"  # Create a loading message
        loadingText1 = font.render(loadingMessage, True, (255,255,255))  # Create a text surface
        loadingMessage = "Sailing Sim"  # Create a loading message
        loadingText2 = font.render(loadingMessage, True, (i, i, i))  # Create a text surface
        screen.blit(loadingText1, (settings.screen_width // 2 - loadingText1.get_width() // 2, settings.screen_height // 2 - 65 // 2))  # Blit the text surface onto the screen
        screen.blit(loadingText2, (settings.screen_width // 2 - loadingText2.get_width() // 2,settings.screen_height // 2 - 25 // 2))  # Blit the text surface onto the screen
        pygame.display.update() # Update the display
        screen.fill((0, 0, 0))
        time.sleep(0.01)
    for i in range (0, 255, 5):
        screen.fill((i/225 * 41, i/225 * 74, i/225 * 143))
        pygame.display.update()
        time.sleep(0.01)
    while loading:
        screen.fill((41, 74, 143))
        loadingMessage = "Sailing Sim"  # Create a loading message
        loadingText = font.render(loadingMessage, True, (255, 255, 255))
        screen.blit(loadingText, (screen_size[0] // 2 - loadingText.get_width() // 2, screen_size[1] // 2 - 65 // 2 - fontSize))
        loadingMessage2 = font.render("Loading... " + str(wind.status) + "%", True, (255, 255, 255))
        screen.blit(loadingMessage2, (screen_size[0] // 2 - loadingMessage2.get_width() // 2, screen_size[1] // 2 + fontSize))
        pygame.display.update()
        time.sleep(0.01)
    timeElapsed += 1

threading.Thread(target=loadingScreen).start()

keys = pygame.key.get_pressed()

# Debug tick to print variables
def debugtick():
    while running:
        # print("================================")
        # print("Scale:", settings.scale)
        # print("Center Boat:", settings.center_boat)
        # print("Prev Center Boat:", prev_centerboat)
        # print("Boat Angle to Wind:", player.boatAngleToWind)
        # print("Boat Angle:", player.angle)
        # print("Wind Angle:", player.wind[1])
        # print("Pos X:", player.pos[0], "Pos Y:", player.pos[1])
        # print("Tack:", player.tack)
        # print("Sail Angle to Wind:", player.sail_angle_to_wind)
        # print("Starboard Boat angle", (player.angle + player.wind[1]) % 360)
        # print("Acceleration:", player.acceleration())
        # print("Speed:a", player.speed)
        # print("Speed X:", player.speedx)
        # print("Speed Y:", player.speedy)
        # print("Angular Velocity", player.angularVelocity)
        # print("Wind Speed:", wind.localWind(player.pos, player.boat_posy)[0])
        time.sleep(1)

# Tick to update at regular intervals regardless of framerate
def tick():
    if running:
        global keys
        time.sleep(0.05)

# Player
player = Boat()

# Map
map = Map("Test Map")

wind_surface = wind.createWindSurface()
loading = False
# Change font size for HUD
last_frame_time = pygame.time.get_ticks()
last_update_time = 50
prev_pos = player.pos
# Store the player's previous position
prev_centerboat = settings.center_boat
# threading.Thread(target=tick).start()
# threading.Thread(target=debugtick).start()

# Game loop
while running:
    # Set Variables
    current_time = pygame.time.get_ticks()
    screen_size = pygame.display.get_surface().get_size()
    keys = pygame.key.get_pressed()

    # Check for events
    for event in pygame.event.get():
        # Check if quit button pressed and quit
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                settings.center_boat = not settings.center_boat  # Toggle center_boat when 'C' key is pressed
                if settings.center_boat:
                    settings.scale = settings.centre_scale
                else:
                    settings.scale = settings.map_scale
                    map.pos = np.dot(player.pos, settings.scale)
            if event.key == pygame.K_F3:
                debug = not debug
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 5:
                player.trimSail(-1)
            elif event.button == 4:
                player.trimSail(1)
    # Previous way to change the scale, removed to improve performance
    # settings.scale = np.clip((settings.scale + (keys[pygame.K_EQUALS] - keys[pygame.K_MINUS])*0.01), 0.06, 0.3)

    # Calculate the time difference
    dt = (current_time - last_frame_time) / 1000.0  # Convert to seconds

    # Calculate the FPS
    if dt > 0:
        fps = 1.0 / dt
    else:
        fps = 0

    last_frame_time = current_time

    # Check if 0.05 seconds have passed since the last update
    if current_time - last_update_time >= 50:  # 0.05 seconds = 50 milliseconds
        factor = current_time - last_update_time / 50
        # Store the player's current position before updating
        prev_pos = player.pos
        # Update the player
        player.update(keys, factor, screen_size)
        # Create the hud
        if debug:
            fontSize = 14
            font = pygame.font.Font(None, fontSize)
            hud_text = ["Speed: {} kts".format(round(player.speed[2], 1)),
                        "Wind Speed: {} kts".format(round(wind.localWind(player.pos[0], player.pos[1])[0], 1)),
                        "Boat Angle: {}°".format(round(player.angle, 0)),
                        "X: {}, Y: {}".format(round(player.pos[0]/100, 0), round(player.pos[1]/100, 0)),
                        "Relative X: {}, Relative Y: {}".format(round(wind.relative_posx/100, 0),round(wind.relative_posy/100, 0)),
                        "Wind Angle: {}°".format(round(wind.localWind(player.pos[0], player.pos[1])[1], 1)),
                        "Boat Angle to Wind: {}°".format(round(player.boat_angle_to_wind, 1)),
                        "Sail Angle to Wind: {}°".format(round(player.sail_angle_to_wind, 1)),
                        "Acceleration: {} kts/s".format(round(player.acceleration[2]/7, 3)),
                        "Tack: {}".format(player.tack),
                        "FPS: {}".format(round(fps, 0))
                        ]
        else:
            fontSize = 30
            font = pygame.font.Font(None, fontSize)
            hud_text = ["Speed: {} kts".format(round(player.speed[2] / 8, 1)),
                        "Wind Speed: {} kts".format(round(wind.localWind(player.pos[0], player.pos[1])[0], 1)),
                        "Boat Angle: {}°".format(round(player.angle, 1)),
                        ]
        hud = []
        for line in hud_text:
            hud.append(font.render(line, True, (255, 255, 255)))

        if not settings.center_boat:
            map.pos[0] += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 20
            map.pos[1] += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 20
        # Update the last update time
        last_update_time = current_time

    # Calculate the interpolation factor
    t = (current_time - last_update_time) / 50.0

    # Calculate the interpolated position
    interpolated_pos = np.array([int(prev_pos[0] + t * (player.pos[0] - prev_pos[0])), int(prev_pos[1] + t * (player.pos[1] - prev_pos[1]))])

    # Draw the screen
    screen.fill((41, 74, 143))
    width, height = pygame.display.get_surface().get_size()
    wind.findTiles(screen, screen_size, interpolated_pos[0], interpolated_pos[1], map.pos[0], map.pos[1])
    player.draw(screen, screen_size, interpolated_pos[0], interpolated_pos[1], map.pos[0], map.pos[1])
    player.drawPointers(screen, screen_size, interpolated_pos[0], interpolated_pos[1], map.pos[0], map.pos[1])
    # map.draw(screen, screen_size, interpolated_pos[0], interpolated_pos[1], map.pos[0], map.pos[1])
    for text_surface in enumerate(hud):
        screen.blit(text_surface[1], (10, 15 + ((text_surface[0]) * fontSize - 4)))

    # Update screen
    pygame.display.update()

    prev_centerboat = settings.center_boat

# Quit
pygame.quit()
sys.exit()