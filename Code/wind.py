import random
import numpy as np
from scipy.interpolate import CubicHermiteSpline
import noise
import math
import pygame
import settings

status = 0

# accelerationFunction graph
sailAngleToWind = np.array([-180, 0, 20, 35, 70, 180])
acceleration = np.array([-0.3, -0.01, -0.01, 0.2, 0.3, -0.02])
accelerationFunction = CubicHermiteSpline(x=sailAngleToWind, y=acceleration, dydx=np.zeros_like(acceleration))

# maxSpeed graph
boatAngleToWind = np.array([-180, 0, 30, 100, 180, 200])
maxSpeed = np.array([0.5, 0.7, 0.7, 1, 0.75, 0.9])
# y = np.array([1, 1, 1, 1, 1])
maxSpeed = CubicHermiteSpline(x=boatAngleToWind, y=maxSpeed, dydx=np.zeros_like(maxSpeed))

# minSpeed
boatAngleToWind = np.array([-180, 90, 200])
minSpeed = np.array([-0.9, 0, 0])
minSpeed = CubicHermiteSpline(x=boatAngleToWind, y=minSpeed, dydx=np.zeros_like(minSpeed))

# Generate perlin noise for wind
mapSize = 2048
scale = 2000

noise_map = [[noise.pnoise2(x/scale, y/scale, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=mapSize, repeaty=mapSize, base=random.randint(0,0)) for x in range(mapSize)] for y in range(mapSize)]

def createWindSurface(display):
    width, height = mapSize, mapSize
    global windSurface
    # Create a new surface with the same dimensions as the screen
    windSurface = pygame.Surface((width, height))
    for posx in range(width):
        for posy in range(height):
            wind = localWind(posx, posy)
            colour = np.clip(int(wind[0]/wind[2]*255), 0, 255)
            windSurface.set_at((posx, posy), (0, 0, colour))
        status = round((posx / mapSize) * 100, 0)

def draw(screen, screenSize, posx, posy):
    tempWindSurface = windSurface.copy()
    tempWindSurface = pygame.transform.smoothscale(tempWindSurface, ((windSurface.get_width() * 5 * settings.scale), (windSurface.get_height() * 5 * settings.scale)))
    windSurfaceRect = tempWindSurface.get_rect()
    if settings.centerBoat:
        windSurfaceRect.center = screenSize[0] / 2 - posx * settings.scale, screenSize[1] / 2 - posy * settings.scale
    else:
        windSurfaceRect.center = (screenSize[0] / 2), (screenSize[1] / 2)

    screen.blit(tempWindSurface, windSurfaceRect)
    tempWindSurface = pygame.transform.flip(tempWindSurface, True, False)
    screen.blit(tempWindSurface, windSurfaceRect.move(windSurfaceRect.width, 0))
    screen.blit(tempWindSurface, windSurfaceRect.move(-windSurfaceRect.width, 0))
    tempWindSurface = pygame.transform.flip(tempWindSurface, False, True)
    screen.blit(tempWindSurface, windSurfaceRect.move(0, windSurfaceRect.height))
    screen.blit(tempWindSurface, windSurfaceRect.move(0, -windSurfaceRect.height))
    tempWindSurface = pygame.transform.flip(tempWindSurface, True, False)
    screen.blit(tempWindSurface, windSurfaceRect.move(windSurfaceRect.width, windSurfaceRect.height))
    screen.blit(tempWindSurface, windSurfaceRect.move(-windSurfaceRect.width, -windSurfaceRect.height))
    screen.blit(tempWindSurface, windSurfaceRect.move(windSurfaceRect.width, -windSurfaceRect.height))
    screen.blit(tempWindSurface, windSurfaceRect.move(-windSurfaceRect.width, windSurfaceRect.height))

def localWind(posx, posy):
    windspeed = 50
    return (windspeed * ((noise_map[int(posy) % mapSize][int(posx) % mapSize] + 1)) / 2), 0, windspeed
    # return(windspeed,0, windspeed)
    # print(noise.pnoise2(posx, float(posy), octaves=1, persistance=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0.0))
    # return windspeed * int(noise.pnoise2(posx + ((math.sin(math.radians(windspeed)) * windspeed) * (pygame.time.get_ticks() / 50)), posy - ((math.sin(math.radians(windspeed)) * (0.1 * windspeed)) * (pygame.time.get_ticks() / 50)), octaves=1, persistance=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0.0))
    # return (windspeed * (noise.pnoise2(posx, posy - ((math.sin(math.radians(windspeed)) * (0.1 * windspeed)) * (pygame.time.get_ticks() / 50)), octaves=1, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0)), 0)