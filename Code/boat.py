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
        self.posx = 0
        self.posy = 0
        self.angle = 0
        self.speed = 0
        self.speedx = 0
        self.speedy = 0
        self.angularAcceleration = 0
        self.acceleration = 0.0

        #Load assets
        self.hull = pygame.image.load("Assets/Boat.png").convert_alpha()
        self.portSail = pygame.image.load("Assets/portSail.png").convert_alpha()
        self.starboardSail = pygame.image.load("Assets/starboardSail.png").convert_alpha()
        #Lower Resolution Assets
        self.hull = pygame.transform.scale(self.hull, (self.hull.get_width()//2, self.hull.get_height()//2))
        self.portSail = pygame.transform.scale(self.portSail, (self.portSail.get_width()//2, self.portSail.get_height()//2))
        self.starboardSail = pygame.transform.scale(self.starboardSail, (self.starboardSail.get_width()//2, self.starboardSail.get_height()//2))

        self.hullRect = self.hull.get_rect()
        self.hullMask = pygame.mask.from_surface(self.hull)
        self.tack = "port"

        self.sail = self.portSail
        self.sailAngle = 10
        self.wind = wind.localWind(self.hullRect.centerx, self.hullRect.centery)
        self.sailAngleToWind = (180 - self.angle % 180) - self.sailAngle - self.wind[1]
        self.boatAngleToWind = (180 - self.angle % 180) - self.wind[1]
    # Draw sail on boat and boat on screen

    def draw(self, screen, screenSize, interpolated_posx, interpolated_posy):
        temphull = self.hull.copy()
        temphull = pygame.transform.scale(temphull, (self.hull.get_width() * 2, self.hull.get_height() * 2))
        self.hullRect = temphull.get_rect()
        # Draw sail on boat
        tempsail = pygame.transform.scale(self.sail, (self.sail.get_width() * 2, self.sail.get_height() * 2))
        tempsail = pygame.transform.rotate(tempsail, self.sailAngle)
        self.sailRect = tempsail.get_rect()
        self.sailRect.center = self.hullRect.centerx, 270
        temphull.blit(tempsail, self.sailRect)
        # Draw boat on screen
        temphull = pygame.transform.rotate(temphull, self.angle)
        temphull = pygame.transform.scale(temphull, ((temphull.get_width()*settings.scale), (temphull.get_height()*settings.scale)))
        self.hullRect = temphull.get_rect()
        if settings.centerBoat:
            self.hullRect.center = screenSize[0]/2, screenSize[1]/2
        else:
            self.hullRect.center = screenSize[0]/2 + interpolated_posx*settings.scale, screenSize[1]/2 + interpolated_posy*settings.scale
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
        self.angle = (self.angle + np.clip((self.angularAcceleration * self.speed), -3, 3)) % 360
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
        if 0 < (boatangle) < 160 and self.tack == "port":
            self.sail = self.starboardSail.copy()
            self.tack = "starboard"
            self.sailAngle = 350 - (self.sailAngle - 10)
        elif 200 < (boatangle) < 360 and self.tack == "starboard":
            self.sail = self.portSail.copy()
            self.tack = "port"
            self.sailAngle = 100 - (self.sailAngle - 260)
        elif self.sailAngleToWind > 0 and self.tack == "port":
            self.sail = self.portSail.copy()
        elif self.sailAngleToWind < 0 and self.tack == "port":
            self.sail = self.starboardSail.copy()
        elif self.sailAngleToWind > 0 and self.tack == "starboard":
            self.sail = self.starboardSail.copy()
        elif self.sailAngleToWind < 0 and self.tack == "starboard":
            self.sail = self.portSail.copy()
    # Calculate speed of boat using acceleration
    def calcSpeed(self):
        self.wind = wind.localWind(self.hullRect.centerx, self.hullRect.centery)
        if self.tack == "starboard":
            self.boatAngleToWind = (self.angle + self.wind[1]) % 360
            self.sailAngleToWind = self.boatAngleToWind - (100 - (self.sailAngle - 260))
        elif self.tack == "port":
            self.boatAngleToWind = (360 - self.angle - self.wind[1]) % 360
            self.sailAngleToWind = self.boatAngleToWind - self.sailAngle
        self.acceleration = wind.accelerationFunction(self.sailAngleToWind) * self.wind[0] - (0.1 * self.speed)
        self.speed = self.speed + self.acceleration - (abs(self.angularAcceleration) * 0.01)
        self.speedx = math.sin(math.radians(self.angle)) * self.speed + (math.sin(math.radians(self.wind[1])) * (0.1 * self.wind[0]))
        self.speedy = math.cos(math.radians(self.angle)) * self.speed - (math.cos(math.radians(self.wind[1])) * (0.1 * self.wind[0]))
    def update(self, keys, factor):
        self.steer((keys[pygame.K_d] - keys[pygame.K_a]))
        self.changeTack()
        self.calcSpeed()
        self.move()
    # Move boat according to speed
    def move(self):
        self.posx -= self.speedx
        self.posy -= self.speedy