import pygame
import math
import wind
import map
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
        self.angularVelocity = 0

        # self.hull = pygame.transform.scale(pygame.image.load("../Assets/Boat.png").convert_alpha(), ((1210*settings.scale), (916*settings.scale)))
        self.hull = pygame.image.load("Assets/Boat.png").convert_alpha()
        self.hullRect = self.hull.get_rect()
        self.hullMask = pygame.mask.from_surface(self.hull)
        self.tack = "port"

        # self.portSail = pygame.transform.scale(pygame.image.load("../Assets/portSail.png").convert_alpha(), ((1250*settings.scale), (1250*settings.scale)))
        # self.starboardSail = pygame.transform.scale(pygame.image.load("../Assets/starboardSail.png").convert_alpha(), ((1250*settings.scale), (1250*settings.scale)))
        self.portSail = pygame.image.load("Assets/portSail.png").convert_alpha()
        self.starboardSail = pygame.image.load("Assets/starboardSail.png").convert_alpha()

        # self.sail = pygame.transform.scale(pygame.image.load("../Assets/portSail.png").convert_alpha(), ((1250*settings.scale), (1250*settings.scale)))
        self.sail = pygame.image.load("Assets/portSail.png").convert_alpha()
        self.sailAngle = 10
        self.wind = wind.localWind(self.hullRect.centerx, self.hullRect.centery)
        self.sailAngleToWind = (180 - self.angle % 180) - self.sailAngle - self.wind[1]
        self.boatAngleToWind = (180 - self.angle % 180) - self.wind[1]
    # Draw sail on boat and boat on screen
    def draw(self, screen, screenSize):
        temphull = self.hull.copy()
        self.hullRect = temphull.get_rect()
        # Draw sail on boat
        tempsail = pygame.transform.rotate(self.sail, self.sailAngle)
        self.sailRect = tempsail.get_rect()
        self.sailRect.center = self.hullRect.centerx, 270
        temphull.blit(tempsail, self.sailRect)
        # Draw boat on screen
        temphull = pygame.transform.rotate(temphull, self.angle)
        temphull = pygame.transform.scale(temphull, ((temphull.get_width()*settings.scale), (temphull.get_height()*settings.scale)))
        self.hullRect = temphull.get_rect()
        self.hullRect.center = screenSize[0]/2 + self.posx*settings.scale, screenSize[1]/2 + self.posy*settings.scale
        screen.blit(temphull, self.hullRect)
    # Turn boat
    def turn(self, angle):
        angularvelocitysteps = 7
        if angle != 0:
            self.angularVelocity = np.clip(self.angularVelocity + (angle / angularvelocitysteps), -0.1 * self.speed, 0.1 * self.speed)
        else:
            if self.angularVelocity > 0:
                self.angularVelocity = np.clip((self.angularVelocity - ((self.angularVelocity * self.speed) / 25)), 0, 5)
            elif self.angularVelocity < 0:
                self.angularVelocity = np.clip((self.angularVelocity + ((-self.angularVelocity * self.speed) / 25)), -5, 0)
        self.angle = (self.angle + np.clip((self.angularVelocity * self.speed), -3, 3)) % 360
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
        acceleration = self.acceleration()
        self.speed = np.clip(self.speed + acceleration - (abs(self.angularVelocity) * 0.01), wind.minSpeed(self.boatAngleToWind) * self.wind[0], wind.maxSpeed(self.boatAngleToWind) * self.wind[0]) * 3 * settings.scale
        self.speedx = math.sin(math.radians(self.angle)) * self.speed + ((math.sin(math.radians(self.wind[1])) * (0.1 * self.wind[0])) * settings.scale)
        self.speedy = math.cos(math.radians(self.angle)) * self.speed - ((math.cos(math.radians(self.wind[1])) * (0.1 * self.wind[0])) * settings.scale)
    # Calculate acceleration of boat
    def acceleration(self):
        self.wind = wind.localWind(self.hullRect.centerx, self.hullRect.centery)
        if self.tack == "starboard":
            self.boatAngleToWind = (self.angle + self.wind[1]) % 360
            self.sailAngleToWind = self.boatAngleToWind - (100 - (self.sailAngle - 260))
        elif self.tack == "port":
            self.boatAngleToWind = (360 - self.angle - self.wind[1]) % 360
            self.sailAngleToWind = self.boatAngleToWind - self.sailAngle
        return wind.accelerationFunction(self.sailAngleToWind)*self.wind[0]
    # Update boat
    def update(self, keys):
        self.move()
        self.turn((keys[pygame.K_d] - keys[pygame.K_a]))
        self.changeTack()
        self.calcSpeed()
    # Move boat according to speed
    def move(self):
        velocity = self.acceleration()
        self.posx -= self.speedx
        self.posy -= self.speedy