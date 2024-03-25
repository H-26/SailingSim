import numpy as np
from scipy.interpolate import CubicHermiteSpline
import noise
import pygame
import settings

class Wind:
    def __init__(self):
        # Variable to track loading status
        self.status = 0
        # Wind tile size variables
        self.map_size = 2048
        self.scale = 2000
        self.surface_scale = 10
        self.half_map_size_scaled = (self.map_size * self.surface_scale) / 2
        # Create Noise map
        self.noise_map = [[(1.0 + noise.pnoise2(x / self.scale, y / self.scale, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=self.map_size, repeaty=self.map_size, base=0) * 2) for x in range(self.map_size)] for y in range(self.map_size)]
        self.shift_map = [[(1.0 + noise.pnoise2(x / self.scale, y / self.scale, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=self.map_size, repeaty=self.map_size, base=5) * 2) for x in range(self.map_size)] for y in range(self.map_size)]
        self.shift_map = (np.array(self.shift_map)-1) * 20
        #Create acceleration function using CubicHermiteSpline to interpolate values
        sail_angle_to_wind = np.array([-180, 0, 35, 60, 90, 110, 180])
        acceleration = np.array([-0.8, 0, 0.5, 0.9, 0.6, 0.8, 0])
        self.acceleration_function = CubicHermiteSpline(x=sail_angle_to_wind, y=acceleration, dydx=np.zeros_like(acceleration))
        #Initiate variables for position relative to wind tiles
        self.relative_posx = 1024
        self.relative_posy = 1024

    # Function to calculate acceleration based on angle of sail to wind
    def accelerationFunction(self, angle):
        return self.acceleration_function(angle)

    # Function to create wind surface based on noise map, executed once during startup
    def createWindSurface(self):
        self.wind_surface = pygame.Surface((self.map_size, self.map_size))
        # Draw noise map onto wind surface
        for posx in range(self.map_size):
            for posy in range(self.map_size):
                colour = np.clip(int((1 + (1 - self.noise_map[posx][posy])) * 128), 0, 255)
                self.wind_surface.set_at((posx, posy), (0, 0, colour))
            self.status = round((posx / self.map_size) * 100, 0)
        # Scale wind surface to different sizes and flip for different grids for connected tiles
        self.centre_wind_surface = pygame.transform.scale(self.wind_surface.copy(), ((self.map_size * self.surface_scale * settings.centre_scale), (self.map_size * self.surface_scale * settings.centre_scale)))
        self.centre_wind_surface_h = pygame.transform.flip(self.centre_wind_surface, True, False)
        self.centre_wind_surface_v = pygame.transform.flip(self.centre_wind_surface, False, True)
        self.centre_wind_surface_hv = pygame.transform.flip(self.centre_wind_surface, True, True)
        self.map_wind_surface = pygame.transform.scale(self.wind_surface.copy(), ((self.map_size * self.surface_scale * settings.map_scale), (self.map_size * self.surface_scale * settings.map_scale)))
        self.map_wind_surface_h = pygame.transform.flip(self.map_wind_surface, True, False)
        self.map_wind_surface_v = pygame.transform.flip(self.map_wind_surface, False, True)
        self.map_wind_surface_hv = pygame.transform.flip(self.map_wind_surface, True, True)

    # Function to draw wind tiles on screen, firstly finding which tiles to draw
    def findTiles(self, screen, screenSize, boat_posx, boat_posy, map_posx, map_posy):
        flip = np.array([False, False])
        # Find the top left and bottom right corners of the screen in terms of wind tiles
        if settings.center_boat:
            top_left_corner = np.array([boat_posx*settings.scale - screenSize[0] / 2, boat_posy*settings.scale - screenSize[1] / 2])
            bottom_right_corner = np.array([boat_posx*settings.scale + screenSize[0] / 2, boat_posy*settings.scale + screenSize[1] / 2])
            top_left_grid = np.array([int(top_left_corner[0] / (self.map_size * self.surface_scale * settings.scale)) - 1, int(top_left_corner[1] / (self.map_size * self.surface_scale * settings.scale)) - 1])
            bottom_right_grid = np.array([int(bottom_right_corner[0] / (self.map_size * self.surface_scale * settings.scale)) + 1, int(bottom_right_corner[1] / (self.map_size * self.surface_scale * settings.scale)) + 1])
        else:
            top_left_corner = np.array([map_posx - screenSize[0] / 2, map_posy - screenSize[1] / 2])
            bottom_right_corner = np.array([map_posx + screenSize[0] / 2, map_posy + screenSize[1] / 2])
            top_left_grid = np.array([int(top_left_corner[0] / (self.map_size * self.surface_scale * settings.scale)) - 1, int(top_left_corner[1] / (self.map_size * self.surface_scale * settings.scale)) - 1])
            bottom_right_grid = np.array([int(bottom_right_corner[0] / (self.map_size * self.surface_scale * settings.scale)) + 1, int(bottom_right_corner[1] / (self.map_size * self.surface_scale * settings.scale)) + 1])
        # Find the flip of the wind tiles based on the grid position and draw the tiles
        for x in range(top_left_grid[0], bottom_right_grid[0]+1):
            flip[0] = False
            if x % 2 != 0:
                flip[0]= True
            for y in range(top_left_grid[1], bottom_right_grid[1]+1):
                flip[1] = False
                if y % 2 != 0:
                    flip[1] = True
                self.drawtile(screen, screenSize, x, y, flip, boat_posx, boat_posy, map_posx, map_posy)

    # Function to draw wind tiles on screen based on position
    def drawtile(self, screen, screen_size, x, y, flip, boat_posx, boat_posy, map_posx, map_posy):
        # Choose the correctly scaled and fliped wind surface based on the view and flip
        if settings.center_boat:
            flip_tuple = tuple(flip.tolist())
            match flip_tuple:
                case (False, False):
                    temp_wind_surface = self.centre_wind_surface
                case (True, False):
                    temp_wind_surface = self.centre_wind_surface_h
                case (False, True):
                    temp_wind_surface = self.centre_wind_surface_v
                case (True, True):
                    temp_wind_surface = self.centre_wind_surface_hv
            windSurfaceRect = temp_wind_surface.get_rect()
            windSurfaceRect.center = int(screen_size[0] / 2) + x * windSurfaceRect.w - int(boat_posx * settings.scale), int(screen_size[1] / 2) + y * windSurfaceRect.w - int(boat_posy * settings.scale)
        else:
            flip_tuple = tuple(flip.tolist())
            match flip_tuple:
                case (False, False):
                    temp_wind_surface = self.map_wind_surface
                case (True, False):
                    temp_wind_surface = self.map_wind_surface_h
                case (False, True):
                    temp_wind_surface = self.map_wind_surface_v
                case (True, True):
                    temp_wind_surface = self.map_wind_surface_hv
            windSurfaceRect = temp_wind_surface.get_rect()
            windSurfaceRect.center = screen_size[0] / 2 + x * windSurfaceRect.w - map_posx, screen_size[1] / 2 + y * windSurfaceRect.w - map_posy
        # Draw the wind tile onto the screen
        screen.blit(temp_wind_surface, windSurfaceRect)

    def localWind(self, posx, posy):
        windspeed = 10
        windangle = 0
        flip = np.array([False, False])
        boat_grid = np.array([0, 0])
        map_sizesub = self.map_size - 1
        if posx >= 0:
            boat_grid[0] = int(((posx / (self.surface_scale * (self.map_size / 2)) + 1) / 2))
            self.relative_posx = int(((posx + self.half_map_size_scaled) % (self.map_size * self.surface_scale)) / self.surface_scale)
        else:
            boat_grid[0] = int(((posx / (self.surface_scale * (self.map_size / 2)) - 1) / 2))
            self.relative_posx = int(map_sizesub - ((abs(posx) + self.half_map_size_scaled) % (self.map_size * self.surface_scale)) / self.surface_scale)
        if posy >= 0:
            boat_grid[1] = int((posy / (self.surface_scale * (self.map_size / 2)) + 1) / 2)
            self.relative_posy = int(((posy + self.half_map_size_scaled) % (self.map_size * self.surface_scale)) / self.surface_scale)
        else:
            boat_grid[1] = int(((posy / (self.surface_scale * (self.map_size / 2)) - 1) / 2))
            self.relative_posy = int(map_sizesub - ((abs(posy) + self.half_map_size_scaled) % (self.map_size * self.surface_scale)) / self.surface_scale)
        if boat_grid[0] % 2 != 0:
            flip[0]= True
        if boat_grid[1] % 2 != 0:
            flip[1] = True
        flip_tuple = tuple(flip.tolist())
        match flip_tuple:
            case (False, False):
                return np.array([windspeed * (self.noise_map[int(self.relative_posx)][int(self.relative_posy)]), windangle + self.shift_map[int(self.relative_posx)][int(self.relative_posy)], windspeed])
            case (True, False):
                return np.array([windspeed * (self.noise_map[int(map_sizesub - self.relative_posx)][int(self.relative_posy)]), windangle + self.shift_map[int(map_sizesub - self.relative_posx)][int(self.relative_posy)], windspeed])
            case (False, True):
                return np.array([windspeed * (self.noise_map[int(self.relative_posx)][int(map_sizesub - self.relative_posy)]), windangle + self.shift_map[int(self.relative_posx)][int(map_sizesub - self.relative_posy)], windspeed])
            case (True, True):
                return np.array([windspeed * (self.noise_map[int(map_sizesub - self.relative_posx)][int(map_sizesub - self.relative_posy)]), windangle + self.shift_map[int(map_sizesub - self.relative_posx)][int(map_sizesub - self.relative_posy)], windspeed])

wind = Wind()