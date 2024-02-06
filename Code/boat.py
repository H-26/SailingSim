#Imports

import pygame
import math
import wind
import numpy as np
import settings

# Boat class
class Boat(pygame.sprite.Sprite):
    # Constructor
    def __init__(self):
        super().__init__()
        self.pos = np.array([0, 0])
        self.angle = 0
        self.speed = np.array([0.0, 0.0, 0.0])
        self.angular_acceleration = 0
        self.acceleration = np.array([0.0, 0.0, 0.0])
        self.friction_coefficient = 0.08

        #Load assets
        self.hull = pygame.image.load("Assets/Boat.png").convert_alpha()
        self.port_sail = pygame.image.load("Assets/portSail.png").convert_alpha()
        self.port_sail = pygame.image.load("Assets/portSail.png").convert_alpha()
        self.starboard_sail = pygame.image.load("Assets/starboardSail.png").convert_alpha()
        # Scale centre assets
        self.centre_hull = pygame.transform.smoothscale(self.hull, ((self.hull.get_width() * settings.centre_scale), (self.hull.get_height() * settings.centre_scale)))
        self.centre_port_sail = pygame.transform.smoothscale(self.port_sail, ((self.port_sail.get_width() * settings.centre_scale), (self.port_sail.get_height() * settings.centre_scale)))
        self.centre_starboard_sail = pygame.transform.smoothscale(self.starboard_sail, ((self.starboard_sail.get_width() * settings.centre_scale), (self.starboard_sail.get_height() * settings.centre_scale)))
        # Scale map assets
        self.map_hull = pygame.transform.smoothscale(self.hull, ((self.hull.get_width() * settings.map_scale), (self.hull.get_height() * settings.map_scale)))
        self.map_port_sail = pygame.transform.smoothscale(self.port_sail, ((self.port_sail.get_width() * settings.map_scale), (self.port_sail.get_height() * settings.map_scale)))
        self.map_starboard_sail = pygame.transform.smoothscale(self.starboard_sail, ((self.starboard_sail.get_width() * settings.map_scale), (self.starboard_sail.get_height() * settings.map_scale)))

        self.hull_rect = self.hull.get_rect()
        # Future idea to make a mask for collision detection
        # self.hullMask = pygame.mask.from_surface(self.hull)

        #Wind related variables
        self.tack = "port"
        self.sail = self.centre_port_sail
        self.sail_angle = 10
        self.wind = (wind.localWind(0, 0))
        self.sail_angle_to_wind = (180 - self.angle % 180) - self.sail_angle - self.wind[1]
        self.boat_angle_to_wind = (180 - self.angle % 180) - self.wind[1]

    # Draw sail on boat and boat on screen
    def draw(self, screen, screen_size, interpolated_posx, interpolated_posy, map_posx, map_posy):
        if settings.center_boat:
            temp_hull = self.centre_hull.copy()
        else:
            temp_hull = self.map_hull.copy()
        self.hull_rect = temp_hull.get_rect()
        temp_sail = self.sail.copy()
        # Draw sail on boat
        temp_sail = pygame.transform.rotate(temp_sail, self.sail_angle)
        self.sailRect = temp_sail.get_rect()
        self.sailRect.center = self.hull_rect.centerx, 270 * settings.scale
        temp_hull.blit(temp_sail, self.sailRect)
        # Draw boat on screen
        temp_hull = pygame.transform.rotate(temp_hull, self.angle)
        self.hull_rect = temp_hull.get_rect()
        if settings.center_boat:
            self.hull_rect.center = screen_size[0] / 2, screen_size[1] / 2
        else:
            self.hull_rect.center = screen_size[0] / 2 + interpolated_posx * settings.scale - map_posx, screen_size[1] / 2 + interpolated_posy * settings.scale - map_posy
        screen.blit(temp_hull, self.hull_rect)
    # Turn boat
    def steer(self, keys):
        angularvelocitysteps = 100
        if keys != 0:
            self.angular_acceleration = np.clip(self.angular_acceleration + (keys / angularvelocitysteps), -0.3, 0.3)
        else:
            if self.angular_acceleration > 0:
                self.angular_acceleration = self.angular_acceleration - (self.angular_acceleration / 3)
            elif self.angular_acceleration < 0:
                self.angular_acceleration = self.angular_acceleration + (-self.angular_acceleration / 3)
        self.angle = (self.angle + np.clip((self.angular_acceleration * 0.6 * self.speed[2]), -3, 3)) % 360
    # Rotate sail on boat
    def trimSail(self, angle):
        if self.sail_angle_to_wind > 0 or angle > 0:
            if self.tack == "port":
                self.sail_angle = np.clip(((self.sail_angle - angle) % 360),10,100)
            elif self.tack == "starboard":
                self.sail_angle = np.clip(((self.sail_angle + angle) % 360), 260, 350)
        elif self.sail_angle_to_wind < 0 and angle < 0:
            anglecoefficient = 5
            if self.tack == "port":
                self.sail_angle = np.clip(((self.sail_angle - angle / anglecoefficient) % 360),10,100)
            elif self.tack == "starboard":
                self.sail_angle = np.clip(((self.sail_angle + angle / anglecoefficient) % 360), 260, 350)
    # Change tack
    def changeTack(self):
        boatangle = (self.angle + self.wind[1]) % 360
        if settings.center_boat == True:
            port_sail = self.centre_port_sail.copy()
            starboard_sail = self.centre_starboard_sail.copy()
        else:
            port_sail = self.map_port_sail.copy()
            starboard_sail = self.map_starboard_sail.copy()
        if 0 < (boatangle) < 160 and self.tack == "port":
            self.sail = starboard_sail
            self.tack = "starboard"
            self.sail_angle = 350 - (self.sail_angle - 10)
        elif 200 < (boatangle) < 360 and self.tack == "starboard":
            self.sail = port_sail
            self.tack = "port"
            self.sail_angle = 100 - (self.sail_angle - 260)
        elif self.sail_angle_to_wind > 0 and self.tack == "port":
            self.sail = port_sail
        elif self.sail_angle_to_wind < 0 and self.tack == "port":
            self.sail = starboard_sail
        elif self.sail_angle_to_wind > 0 and self.tack == "starboard":
            self.sail = starboard_sail
        elif self.sail_angle_to_wind < 0 and self.tack == "starboard":
            self.sail = port_sail
    # Calculate speed of boat using acceleration
    def calcSpeed(self):
        self.wind = wind.localWind(self.pos[0], self.pos[1])
        if self.tack == "starboard":
            self.boat_angle_to_wind = (self.angle + self.wind[1]) % 360
            self.sail_angle_to_wind = self.boat_angle_to_wind - (100 - (self.sail_angle - 260))
        elif self.tack == "port":
            self.boat_angle_to_wind = (360 - self.angle - self.wind[1]) % 360
            self.sail_angle_to_wind = self.boat_angle_to_wind - self.sail_angle
        #Calculate acceleration for x, y and total. Use acceleration function to calculate acceleration, multiply by windspeed and subtract friction
        acceleration_calculation = wind.acceleration_function(self.sail_angle_to_wind) * self.wind[0] - (abs(self.angular_acceleration) * 0.01)
        # Removed previous acceleration calculation for x and y so boat always moves in direction of travel
        # self.acceleration[0] = math.sin(math.radians(self.angle)) * acceleration_calculation - (self.friction_coefficient * self.speed[0]) - math.sin(math.radians(self.wind[1])) * (0.1 * self.wind[0])
        # self.acceleration[2] = math.sqrt(self.acceleration[0] ** 2 + self.acceleration[1] ** 2)
        self.acceleration[2] = acceleration_calculation - (self.friction_coefficient * self.speed[2]) - math.cos(math.radians(self.boat_angle_to_wind)) * (0.01 * self.wind[0])
        self.speed[2] += self.acceleration[2]
        self.speed[0] = math.sin(math.radians(self.angle)) * self.speed[2]
        self.speed[1] = math.cos(math.radians(self.angle)) * self.speed[2]

    # Update boat
    def update(self, keys, factor, screen_size):
        self.steer((keys[pygame.K_d] - keys[pygame.K_a]))
        self.changeTack()
        self.calcSpeed()
        self.move()
    # Move boat according to speed
    def move(self):
        self.pos[0] -= self.speed[0]
        self.pos[1] -= self.speed[1]