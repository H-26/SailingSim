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
        self.speed = np.array([0, 0, 0])
        self.angularAcceleration = 0
        self.acceleration = np.array([0, 0, 0])
        self.frictionCoefficient = 0.1

        #Load assets
        self.hull = pygame.image.load("Assets/Boat.png").convert_alpha()
        self.portSail = pygame.image.load("Assets/portSail.png").convert_alpha()
        self.starboardSail = pygame.image.load("Assets/starboardSail.png").convert_alpha()
        # Scale centre assets
        self.centrehull = pygame.transform.smoothscale(self.hull, ((self.hull.get_width() * settings.centreScale), (self.hull.get_height() * settings.centreScale)))
        self.centreportSail = pygame.transform.smoothscale(self.portSail, ((self.portSail.get_width() * settings.centreScale), (self.portSail.get_height() * settings.centreScale)))
        self.centrestarboardSail = pygame.transform.smoothscale(self.starboardSail, ((self.starboardSail.get_width() * settings.centreScale), (self.starboardSail.get_height() * settings.centreScale)))

        # Scale map assets
        self.maphull = pygame.transform.smoothscale(self.hull, ((self.hull.get_width() * settings.mapScale), (self.hull.get_height() * settings.mapScale)))
        self.mapportSail = pygame.transform.smoothscale(self.portSail, ((self.portSail.get_width() * settings.mapScale), (self.portSail.get_height() * settings.mapScale)))
        self.mapstarboardSail = pygame.transform.smoothscale(self.starboardSail, ((self.starboardSail.get_width() * settings.mapScale), (self.starboardSail.get_height() * settings.mapScale)))

        self.hullRect = self.hull.get_rect()
        self.hullMask = pygame.mask.from_surface(self.hull)
        self.tack = "port"

        self.sail = self.centreportSail
        self.sailAngle = 10
        self.wind = (wind.localWind(0, 0))
        self.sailAngleToWind = (180 - self.angle % 180) - self.sailAngle - self.wind[1]
        self.boatAngleToWind = (180 - self.angle % 180) - self.wind[1]
    # Draw sail on boat and boat on screen

    def draw(self, screen, screenSize, interpolated_posx, interpolated_posy, map_posx, map_posy):
        if settings.centerBoat:
            temphull = self.centrehull.copy()
        else:
            temphull = self.maphull.copy()
        self.hullRect = temphull.get_rect()
        tempsail = self.sail.copy()
        # Draw sail on boat
        tempsail = pygame.transform.rotate(tempsail, self.sailAngle)
        self.sailRect = tempsail.get_rect()
        self.sailRect.center = self.hullRect.centerx, 270 * settings.scale
        temphull.blit(tempsail, self.sailRect)
        # Draw boat on screen
        temphull = pygame.transform.rotate(temphull, self.angle)
        self.hullRect = temphull.get_rect()
        if settings.centerBoat:
            self.hullRect.center = screenSize[0]/2, screenSize[1]/2
        else:
            self.hullRect.center = screenSize[0]/2 + interpolated_posx*settings.scale - map_posx, screenSize[1]/2 + interpolated_posy*settings.scale - map_posy
        screen.blit(temphull, self.hullRect)
    # Turn boat
    def steer(self, keys):
        angularvelocitysteps = 100
        if keys != 0:
            self.angularAcceleration = np.clip(self.angularAcceleration + (keys / angularvelocitysteps), -0.3, 0.3)
        else:
            if self.angularAcceleration > 0:
                self.angularAcceleration = self.angularAcceleration - (self.angularAcceleration / 3)
            elif self.angularAcceleration < 0:
                self.angularAcceleration = self.angularAcceleration + (-self.angularAcceleration / 3)
        self.angle = (self.angle + np.clip((self.angularAcceleration * 0.6 * self.speed[2]), -3, 3)) % 360
    # Rotate sail on boat
    def trimSail(self, angle):
        if self.sailAngleToWind > 0 or angle > 0:
            if self.tack == "port":
                self.sailAngle = np.clip(((self.sailAngle - angle) % 360),10,100)
            elif self.tack == "starboard":
                self.sailAngle = np.clip(((self.sailAngle + angle) % 360), 260, 350)
        elif self.sailAngleToWind < 0 and angle < 0:
            anglecoefficient = 5
            if self.tack == "port":
                self.sailAngle = np.clip(((self.sailAngle - angle / anglecoefficient) % 360),10,100)
            elif self.tack == "starboard":
                self.sailAngle = np.clip(((self.sailAngle + angle / anglecoefficient) % 360), 260, 350)
    # Change tack
    def changeTack(self):
        boatangle = (self.angle + self.wind[1]) % 360
        if settings.centerBoat == True:
            portSail = self.centreportSail.copy()
            starboardSail = self.centrestarboardSail.copy()
        else:
            portSail = self.mapportSail.copy()
            starboardSail = self.mapstarboardSail.copy()
        if 0 < (boatangle) < 160 and self.tack == "port":
            self.sail = starboardSail
            self.tack = "starboard"
            self.sailAngle = 350 - (self.sailAngle - 10)
        elif 200 < (boatangle) < 360 and self.tack == "starboard":
            self.sail = portSail
            self.tack = "port"
            self.sailAngle = 100 - (self.sailAngle - 260)
        elif self.sailAngleToWind > 0 and self.tack == "port":
            self.sail = portSail
        elif self.sailAngleToWind < 0 and self.tack == "port":
            self.sail = starboardSail
        elif self.sailAngleToWind > 0 and self.tack == "starboard":
            self.sail = starboardSail
        elif self.sailAngleToWind < 0 and self.tack == "starboard":
            self.sail = portSail
    # Calculate speed of boat using acceleration
    def calcSpeed(self, screenSize):
        self.wind = wind.localWind(self.pos[0], self.pos[1])
        if self.tack == "starboard":
            self.boatAngleToWind = (self.angle + self.wind[1]) % 360
            self.sailAngleToWind = self.boatAngleToWind - (100 - (self.sailAngle - 260))
        elif self.tack == "port":
            self.boatAngleToWind = (360 - self.angle - self.wind[1]) % 360
            self.sailAngleToWind = self.boatAngleToWind - self.sailAngle
        #Calculate acceleration for x, y and total. Use acceleration function to calculate acceleration, multiply by windspeed and subtract friction
        acceleration_calculation = wind.accelerationFunction(self.sailAngleToWind) * self.wind[0] - (abs(self.angularAcceleration) * 0.01)
        # self.acceleration[0] = math.sin(math.radians(self.angle)) * acceleration_calculation - (self.frictionCoefficient * self.speed[0]) - math.sin(math.radians(self.wind[1])) * (0.1 * self.wind[0])
        # self.acceleration[1] = math.cos(math.radians(self.angle)) * acceleration_calculation - (self.frictionCoefficient * self.speed[1]) - math.cos(math.radians(self.wind[1])) * (0.1 * self.wind[0])
        # self.acceleration[2] = math.sqrt(self.acceleration[0] ** 2 + self.acceleration[1] ** 2)
        self.acceleration[2] = acceleration_calculation - (self.frictionCoefficient * self.speed[2])
        self.speed[2] = self.speed[2] + self.acceleration[2]
        self.speed[0] = math.sin(math.radians(self.angle)) * self.speed[2]
        self.speed[1] = math.cos(math.radians(self.angle)) * self.speed[2]
        # self.speed[0] = self.speed[0] + self.acceleration[2] - math.sin(math.radians(self.wind[1])) * (0.1 * self.wind[0])
        # self.speed[1] = self.speed[1] + self.acceleration[2] - math.cos(math.radians(self.wind[1])) * (0.1 * self.wind[0])
        # self.speed[2] = math.sqrt(self.speed[0] ** 2 + self.speed[1] ** 2)
    def update(self, keys, factor, screenSize):
        self.steer((keys[pygame.K_d] - keys[pygame.K_a]))
        self.changeTack()
        self.calcSpeed(screenSize)
        self.move()
    # Move boat according to speed
    def move(self):
        self.pos[0] -= self.speed[0]
        self.pos[1] -= self.speed[1]