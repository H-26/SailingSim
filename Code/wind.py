import numpy as np
from scipy.interpolate import CubicHermiteSpline
import noise
import pygame
import settings

status = 0

# accelerationFunction graph
sailAngleToWind = np.array([-180, 0, 30, 60, 90, 110, 180])
acceleration = np.array([-0.8, 0, 0.5,0.9, 0.6, 0.8, 0])
accelerationFunction = CubicHermiteSpline(x=sailAngleToWind, y=acceleration, dydx=np.zeros_like(acceleration))

# Generate perlin noise for wind
mapSize = 2048
scale = 2000
status = 0
surfaceScale = 10

noise_map = [[(1.0 + noise.pnoise2(x/scale, y/scale, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=mapSize, repeaty=mapSize, base=0) * 3) for x in range(mapSize)] for y in range(mapSize)]

def createWindSurface():
    global windSurface, centrewindSurface, centrewindSurfaceh, centrewindSurfacev, centrewindSurfacehv , mapwindSurface, mapwindSurfaceh, mapwindSurfacev, mapwindSurfacehv, status
    # Create a new surface with the same dimensions as the screen
    windSurface = pygame.Surface((mapSize, mapSize))
    for posx in range(mapSize):
        for posy in range(mapSize):
            colour = np.clip(int((1 + (1 - noise_map[posx][posy])) * 128), 0, 255)
            # print(colour, noise_map[boat_posx][boat_posy])
            windSurface.set_at((posx, posy), (0, 0, colour))
        status = round((posx / mapSize) * 100, 0)
    centrewindSurface = pygame.transform.scale(windSurface.copy(), ((mapSize * surfaceScale * settings.centreScale), (mapSize * surfaceScale * settings.centreScale)))
    centrewindSurfaceh = pygame.transform.flip(centrewindSurface, True, False)
    centrewindSurfacev = pygame.transform.flip(centrewindSurface, False, True)
    centrewindSurfacehv = pygame.transform.flip(centrewindSurface, True, True)
    mapwindSurface = pygame.transform.scale(windSurface.copy(), ((mapSize * surfaceScale * settings.mapScale), (mapSize * surfaceScale * settings.mapScale)))
    mapwindSurfaceh = pygame.transform.flip(mapwindSurface, True, False)
    mapwindSurfacev = pygame.transform.flip(mapwindSurface, False, True)
    mapwindSurfacehv = pygame.transform.flip(mapwindSurface, True, True)

def findTiles(screen, screenSize, boat_posx, boat_posy, map_posx, map_posy):
    flip = np.array([False, False])
    if settings.centerBoat:
        #Floot Division doesn't work with negatives - casted as an int instead
        top_left_corner = np.array([boat_posx*settings.scale - screenSize[0] / 2, boat_posy*settings.scale - screenSize[1] / 2])
        bottom_right_corner = np.array([boat_posx*settings.scale + screenSize[0] / 2, boat_posy*settings.scale + screenSize[1] / 2])
        top_left_grid = np.array([int(top_left_corner[0] / (mapSize * surfaceScale * settings.scale)) - 1, int(top_left_corner[1] / (mapSize * surfaceScale * settings.scale)) - 1])
        bottom_right_grid = np.array([int(bottom_right_corner[0] / (mapSize * surfaceScale * settings.scale)) + 1, int(bottom_right_corner[1] / (mapSize * surfaceScale * settings.scale)) + 1])
    else:
        top_left_corner = np.array([map_posx - screenSize[0] / 2, map_posy - screenSize[1] / 2])
        bottom_right_corner = np.array([map_posx + screenSize[0] / 2, map_posy + screenSize[1] / 2])
        top_left_grid = np.array([int(top_left_corner[0] / (mapSize * surfaceScale * settings.scale)) - 1, int(top_left_corner[1] / (mapSize * surfaceScale * settings.scale)) - 1])
        bottom_right_grid = np.array([int(bottom_right_corner[0] / (mapSize * surfaceScale * settings.scale)) + 1, int(bottom_right_corner[1] / (mapSize * surfaceScale*settings.scale)) + 1])
    for x in range(top_left_grid[0], bottom_right_grid[0]+1):
        flip[0] = False
        if x % 2 != 0:
            # flip horizontally
            flip[0]= True
        for y in range(top_left_grid[1], bottom_right_grid[1]+1):
            flip[1] = False
            if y % 2 != 0:
                # flip vertically
                flip[1] = True
            drawtile(screen, screenSize, x, y, flip, boat_posx, boat_posy, map_posx, map_posy)

def drawtile(screen, screenSize, x, y, flip, boat_posx, boat_posy, map_posx, map_posy):
    global centrewindSurface, centrewindSurfaceh, centrewindSurfacev, centrewindSurfacehv, mapwindSurface, mapwindSurfaceh, mapwindSurfacev, mapwindSurfacehv
    if settings.centerBoat:
        flip_tuple = tuple(flip.tolist())  # Convert numpy array to tuple
        match flip_tuple:
            case (False, False):
                tempWindSurface = centrewindSurface
            case (True, False):
                tempWindSurface = centrewindSurfaceh
            case (False, True):
                tempWindSurface = centrewindSurfacev
            case (True, True):
                tempWindSurface = centrewindSurfacehv
        windSurfaceRect = tempWindSurface.get_rect()
        windSurfaceRect.center = int(screenSize[0] / 2) + x * windSurfaceRect.w - int(boat_posx * settings.scale), int(screenSize[1] / 2) + y * windSurfaceRect.w - int(boat_posy * settings.scale)
    else:
        flip_tuple = tuple(flip.tolist())  # Convert numpy array to tuple
        match flip_tuple:
            case (False, False):
                tempWindSurface = mapwindSurface
            case (True, False):
                tempWindSurface = mapwindSurfaceh
            case (False, True):
                tempWindSurface = mapwindSurfacev
            case (True, True):
                tempWindSurface = mapwindSurfacehv
        windSurfaceRect = tempWindSurface.get_rect()
        windSurfaceRect.center = screenSize[0] / 2 + x * windSurfaceRect.w - map_posx, screenSize[1] / 2 + y * windSurfaceRect.w - map_posy
    screen.blit(tempWindSurface, windSurfaceRect)


def draw(screen, screenSize, boat_posx, boat_posy, map_posx, map_posy):
    if settings.centerBoat:
        tempWindSurface = centrewindSurface
        windSurfaceRect = tempWindSurface.get_rect()
        windSurfaceRect.center = screenSize[0] / 2 - boat_posx * settings.scale, screenSize[1] / 2 - boat_posy * settings.scale
    else:
        tempWindSurface = mapwindSurface
        windSurfaceRect = tempWindSurface.get_rect()
        windSurfaceRect.center = screenSize[0] / 2 - map_posx, screenSize[1] / 2 - map_posy
        screen.blit(tempWindSurface, windSurfaceRect)

    # screen.blit(tempWindSurface, windSurfaceRect)
    # tempWindSurface = pygame.transform.flip(tempWindSurface, True, False)
    # screen.blit(tempWindSurface, windSurfaceRect.move(windSurfaceRect.width, 0))
    # screen.blit(tempWindSurface, windSurfaceRect.move(-windSurfaceRect.width, 0))
    # tempWindSurface = pygame.transform.flip(tempWindSurface, False, True)
    # screen.blit(tempWindSurface, windSurfaceRect.move(0, windSurfaceRect.height))
    # screen.blit(tempWindSurface, windSurfaceRect.move(0, -windSurfaceRect.height))
    # tempWindSurface = pygame.transform.flip(tempWindSurface, True, False)
    # screen.blit(tempWindSurface, windSurfaceRect.move(windSurfaceRect.width, windSurfaceRect.height))
    # screen.blit(tempWindSurface, windSurfaceRect.move(-windSurfaceRect.width, -windSurfaceRect.height))
    # screen.blit(tempWindSurface, windSurfaceRect.move(windSurfaceRect.width, -windSurfaceRect.height))
    # screen.blit(tempWindSurface, windSurfaceRect.move(-windSurfaceRect.width, windSurfaceRect.height))

def localWind(posx, posy):
    windspeed = 10
    windangle = 0
    flip = np.array([False, False])
    boat_grid = np.array([0, 0])
    if posx >= 0:
        boat_grid[0] = int(((posx / (surfaceScale * (mapSize / 2)) + 1) / 2))
    else:
        boat_grid[0] = int(((posx / (surfaceScale * (mapSize / 2)) - 1) / 2))
    if posy >= 0:
        boat_grid[1] = int(((posy / (surfaceScale * (mapSize / 2))) + 1) / 2)
    else:
        boat_grid[1] = int(((posy / (surfaceScale * (mapSize / 2)) - 1) / 2))
    # boat_grid = np.array([int(((posx / (surfaceScale * (mapSize/2)) + 1) / 2)), int(((posy / (surfaceScale * (mapSize/2))) + 1) / 2)])
    print(boat_grid)
    if boat_grid[0] % 2 != 0:
        # flip horizontally
        flip[0]= True
    if boat_grid[1] % 2 != 0:
        # flip vertically
        flip[1] = True
    flip_tuple = tuple(flip.tolist())  # Convert numpy array to tuple
    match flip_tuple:
        case (False, False):
            return np.array([(windspeed * (noise_map[int((abs(posx) % (mapSize * surfaceScale)) / surfaceScale)][int((abs(posy) % (mapSize * surfaceScale)) / surfaceScale)])), windangle, windspeed])
            # return np.array([(windspeed * (noise_map[int((mapSize)/2 + posx/surfaceScale)][int((mapSize)/2 + posy/surfaceScale)])), windangle, windspeed])
        case (True, False):
            return np.array([(windspeed * (noise_map[int(mapSize - ((abs(posx) % (mapSize * surfaceScale)) / surfaceScale))][int((abs(posy) % (mapSize * surfaceScale)) / surfaceScale)])), windangle, windspeed])
        case (False, True):
            return np.array([(windspeed * (noise_map[int((abs(posx) % (mapSize * surfaceScale)) / surfaceScale)][int(mapSize - ((abs(posy) % (mapSize * surfaceScale)) / surfaceScale))])), windangle, windspeed])
        case (True, True):
            return np.array([(windspeed * (noise_map[int(mapSize - ((abs(posx) % (mapSize * surfaceScale)) / surfaceScale))][int(mapSize - ((abs(posy) % (mapSize * surfaceScale)) / surfaceScale))])), windangle, windspeed])
    # return np.array([(windspeed * (noise_map[int((mapSize)/2 + posx/surfaceScale)][int((mapSize)/2 + posy/surfaceScale)])), windangle, windspeed])
    # return(windspeed,0, windspeed)
    # print(noise.pnoise2(pos, float(boat_posy), octaves=1, persistance=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0.0))
    # return windspeed * int(noise.pnoise2(pos + ((math.sin(math.radians(windspeed)) * windspeed) * (pygame.time.get_ticks() / 50)), boat_posy - ((math.sin(math.radians(windspeed)) * (0.1 * windspeed)) * (pygame.time.get_ticks() / 50)), octaves=1, persistance=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0.0))
    # return (windspeed * (noise.pnoise2(pos, boat_posy - ((math.sin(math.radians(windspeed)) * (0.1 * windspeed)) * (pygame.time.get_ticks() / 50)), octaves=1, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0)), 0)