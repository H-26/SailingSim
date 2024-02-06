import numpy as np
from scipy.interpolate import CubicHermiteSpline
import noise
import pygame
import settings

status = 0

# acceleration_function graph
sail_angle_to_wind = np.array([-180, 0, 30, 60, 90, 110, 180])
acceleration = np.array([-0.8, 0, 0.5,0.9, 0.6, 0.8, 0])
acceleration_function = CubicHermiteSpline(x=sail_angle_to_wind, y=acceleration, dydx=np.zeros_like(acceleration))

# Generate perlin noise for wind
map_size = 2048
scale = 2000
status = 0
surface_scale = 10
half_map_size_scaled = (map_size * surface_scale) / 2

noise_map = [[(1.0 + noise.pnoise2(x / scale, y / scale, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=map_size, repeaty=map_size, base=0) * 2) for x in range(map_size)] for y in range(map_size)]

def createWindSurface():
    global wind_surface, centre_wind_surface, centre_wind_surface_h, centre_wind_surface_v, centre_wind_surface_hv , map_wind_surface, map_wind_surface_h, map_wind_surface_v, map_wind_surface_hv, status
    # Create a new surface with the same dimensions as the screen
    wind_surface = pygame.Surface((map_size, map_size))
    for posx in range(map_size):
        for posy in range(map_size):
            colour = np.clip(int((1 + (1 - noise_map[posx][posy])) * 128), 0, 255)
            # print(colour, noise_map[boat_posx][boat_posy])
            wind_surface.set_at((posx, posy), (0, 0, colour))
        status = round((posx / map_size) * 100, 0)
    centre_wind_surface = pygame.transform.scale(wind_surface.copy(), ((map_size * surface_scale * settings.centre_scale), (map_size * surface_scale * settings.centre_scale)))
    centre_wind_surface_h = pygame.transform.flip(centre_wind_surface, True, False)
    centre_wind_surface_v = pygame.transform.flip(centre_wind_surface, False, True)
    centre_wind_surface_hv = pygame.transform.flip(centre_wind_surface, True, True)
    map_wind_surface = pygame.transform.scale(wind_surface.copy(), ((map_size * surface_scale * settings.map_scale), (map_size * surface_scale * settings.map_scale)))
    map_wind_surface_h = pygame.transform.flip(map_wind_surface, True, False)
    map_wind_surface_v = pygame.transform.flip(map_wind_surface, False, True)
    map_wind_surface_hv = pygame.transform.flip(map_wind_surface, True, True)

def findTiles(screen, screenSize, boat_posx, boat_posy, map_posx, map_posy):
    flip = np.array([False, False])
    if settings.center_boat:
        #Floot Division doesn't work with negatives - casted as an int instead
        top_left_corner = np.array([boat_posx*settings.scale - screenSize[0] / 2, boat_posy*settings.scale - screenSize[1] / 2])
        bottom_right_corner = np.array([boat_posx*settings.scale + screenSize[0] / 2, boat_posy*settings.scale + screenSize[1] / 2])
        top_left_grid = np.array([int(top_left_corner[0] / (map_size * surface_scale * settings.scale)) - 1, int(top_left_corner[1] / (map_size * surface_scale * settings.scale)) - 1])
        bottom_right_grid = np.array([int(bottom_right_corner[0] / (map_size * surface_scale * settings.scale)) + 1, int(bottom_right_corner[1] / (map_size * surface_scale * settings.scale)) + 1])
    else:
        top_left_corner = np.array([map_posx - screenSize[0] / 2, map_posy - screenSize[1] / 2])
        bottom_right_corner = np.array([map_posx + screenSize[0] / 2, map_posy + screenSize[1] / 2])
        top_left_grid = np.array([int(top_left_corner[0] / (map_size * surface_scale * settings.scale)) - 1, int(top_left_corner[1] / (map_size * surface_scale * settings.scale)) - 1])
        bottom_right_grid = np.array([int(bottom_right_corner[0] / (map_size * surface_scale * settings.scale)) + 1, int(bottom_right_corner[1] / (map_size * surface_scale * settings.scale)) + 1])
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

def drawtile(screen, screen_size, x, y, flip, boat_posx, boat_posy, map_posx, map_posy):
    global centre_wind_surface, centre_wind_surface_h, centre_wind_surface_v, centre_wind_surface_hv, map_wind_surface, map_wind_surface_h, map_wind_surface_v, map_wind_surface_hv
    #Select the correcttly flipped wind surface and position it on the screen
    if settings.center_boat:
        flip_tuple = tuple(flip.tolist())  # Convert numpy array to tuple
        match flip_tuple:
            case (False, False):
                temp_wind_surface = centre_wind_surface
            case (True, False):
                temp_wind_surface = centre_wind_surface_h
            case (False, True):
                temp_wind_surface = centre_wind_surface_v
            case (True, True):
                temp_wind_surface = centre_wind_surface_hv
        windSurfaceRect = temp_wind_surface.get_rect()
        windSurfaceRect.center = int(screen_size[0] / 2) + x * windSurfaceRect.w - int(boat_posx * settings.scale), int(screen_size[1] / 2) + y * windSurfaceRect.w - int(boat_posy * settings.scale)
    else:
        flip_tuple = tuple(flip.tolist())
        match flip_tuple:
            case (False, False):
                temp_wind_surface = map_wind_surface
            case (True, False):
                temp_wind_surface = map_wind_surface_h
            case (False, True):
                temp_wind_surface = map_wind_surface_v
            case (True, True):
                temp_wind_surface = map_wind_surface_hv
        windSurfaceRect = temp_wind_surface.get_rect()
        windSurfaceRect.center = screen_size[0] / 2 + x * windSurfaceRect.w - map_posx, screen_size[1] / 2 + y * windSurfaceRect.w - map_posy
    # Draw the wind on the screen
    screen.blit(temp_wind_surface, windSurfaceRect)

# Draw the wind on the screen
def draw(screen, screenSize, boat_posx, boat_posy, map_posx, map_posy):
    if settings.center_boat:
        tempWindSurface = centre_wind_surface
        windSurfaceRect = tempWindSurface.get_rect()
        windSurfaceRect.center = screenSize[0] / 2 - boat_posx * settings.scale, screenSize[1] / 2 - boat_posy * settings.scale
    else:
        tempWindSurface = map_wind_surface
        windSurfaceRect = tempWindSurface.get_rect()
        windSurfaceRect.center = screenSize[0] / 2 - map_posx, screenSize[1] / 2 - map_posy
        screen.blit(tempWindSurface, windSurfaceRect)

# Function to find local wind
def localWind(posx, posy):
    global relative_posx, relative_posy
    windspeed = 10
    windangle = 0
    flip = np.array([False, False])
    boat_grid = np.array([0, 0])
    #Find the grid the boat is in and the relative position of the boat to that grid
    if posx >= 0:
        boat_grid[0] = int(((posx / (surface_scale * (map_size / 2)) + 1) / 2))
        relative_posx = int(((posx + half_map_size_scaled) % (map_size * surface_scale)) / surface_scale)
    else:
        boat_grid[0] = int(((posx / (surface_scale * (map_size / 2)) - 1) / 2))
        relative_posx = int(map_size - ((abs(posx) + half_map_size_scaled) % (map_size * surface_scale)) / surface_scale)
    if posy >= 0:
        boat_grid[1] = int((posy / (surface_scale * (map_size / 2)) + 1) / 2)
        relative_posy = int(((posy + half_map_size_scaled) % (map_size * surface_scale)) / surface_scale)
    else:
        boat_grid[1] = int(((posy / (surface_scale * (map_size / 2)) - 1) / 2))
        relative_posy = int(map_size - ((abs(posy) + half_map_size_scaled) % (map_size * surface_scale)) / surface_scale)
    #Flip the wind surface depending on what grid the boat is in
    if boat_grid[0] % 2 != 0:
        # Flip horizontally
        flip[0]= True
    if boat_grid[1] % 2 != 0:
        # Flip vertically
        flip[1] = True
    flip_tuple = tuple(flip.tolist())  # Convert numpy array to tuple
    match flip_tuple:
        case (False, False):
            return np.array([windspeed * (noise_map[int(relative_posx) - 1][int(relative_posy) - 1]), windangle, windspeed])
        case (True, False):
            return np.array([windspeed * (noise_map[int(map_size - relative_posx) - 1][int(relative_posy) - 1]), windangle, windspeed])
        case (False, True):
            return np.array([windspeed * (noise_map[int(relative_posx) - 1][int(map_size - relative_posy) - 1]), windangle, windspeed])
        case (True, True):
            return np.array([windspeed * (noise_map[int(map_size - relative_posx) - 1][int(map_size - relative_posy) - 1]), windangle, windspeed])