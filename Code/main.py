# Imports
import pygame, sys, threading
import numpy as np
from scipy.interpolate import CubicHermiteSpline
import math

# Setup
pygame.init()

#accelerationFunction graph
x = np.array([-180,0,100,180])
y = np.array([-0.4,-0.007,0.5,0.2])
accelerationFunction = CubicHermiteSpline(x=x, y=y, dydx=np.zeros_like(y))

#maxSpeed graph
x = np.array([-180,0,30,100,180])
y = np.array([0.5,0.7,0.8,1.1,0.4])
# y = np.array([1, 1, 1, 1, 1])
maxSpeed = CubicHermiteSpline(x=x, y=y, dydx=np.zeros_like(y))

#minSpeed
minSpeed = -0.8

# Window initiation
screenWidth = 900
screenHeight = 700
screen = pygame.display.set_mode((screenWidth, screenHeight))

pygame.display.set_caption("SailingSim")
icon = pygame.image.load("../Assets/Boat.png")  # To change Icon
pygame.display.set_icon(icon)

def localWind(posx, posy):
    return(5,0)


class Boat(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.scale = 0.1
        self.posx = 400
        self.posy = 300
        self.angle = 0
        self.speed = 0
        self.speedx = 0
        self.speedy = 0

        self.hull = pygame.transform.scale(pygame.image.load("../Assets/Boat.png").convert_alpha(), ((1210*self.scale), (916*self.scale)))
        self.hullRect = self.hull.get_rect()
        self.tack = "port"

        self.portSail = pygame.transform.scale(pygame.image.load("../Assets/portSail.png").convert_alpha(), ((1250*self.scale), (1250*self.scale)))
        self.starboardSail = pygame.transform.scale(pygame.image.load("../Assets/starboardSail.png").convert_alpha(), ((1250*self.scale), (1250*self.scale)))

        self.sail = pygame.transform.scale(pygame.image.load("../Assets/portSail.png").convert_alpha(), ((1250*self.scale), (1250*self.scale)))
        self.sailAngle = 10
        self.wind = localWind(self.hullRect.centerx, self.hullRect.centery)
        self.angletoWind = (180 - self.angle % 180) - self.sailAngle - self.wind[1]

    def draw(self):
        tempHull = self.hull.copy()
        self.hullRect = tempHull.get_rect()
        # Draw sail on boat
        tempSail = pygame.transform.rotate(self.sail, self.sailAngle)
        self.sailRect = tempSail.get_rect()
        self.sailRect.center = self.hullRect.centerx, (270*self.scale)
        tempHull.blit(tempSail, self.sailRect)
        # Draw boat on screen
        tempHull = pygame.transform.rotate(tempHull, self.angle)
        self.hullRect = tempHull.get_rect()
        self.hullRect.center = self.posx, self.posy
        screen.blit(tempHull, self.hullRect)

    def turn(self, angle):
        self.angle = (self.angle + (angle * self.speed) / 1.5) % 360

    def trimSail(self, angle):
        if self.tack == "port":
            self.sailAngle = np.clip(((self.sailAngle + angle) % 360),10,100)
        elif self.tack == "starboard":
            self.sailAngle = np.clip(((self.sailAngle + angle) % 360), 260, 350)

    def changeTack(self):
        if 0 <= self.angle < 180 and self.tack == "port":
            self.sail = self.starboardSail.copy()
            self.tack = "starboard"
            self.sailAngle = 350 - (self.sailAngle - 10)
        elif 180 < self.angle <= 360 and self.tack == "starboard":
            self.sail = self.portSail.copy()
            self.tack = "port"
            self.sailAngle = 100 - (self.sailAngle - 260)
        elif self.angletoWind > 0 and self.tack == "port":
            self.sail = self.portSail.copy()
        elif self.angletoWind < 0 and self.tack == "port":
            self.sail = self.starboardSail.copy()
        elif self.angletoWind > 0 and self.tack == "starboard":
            self.sail = self.starboardSail.copy()
        elif self.angletoWind < 0 and self.tack == "starboard":
            self.sail = self.portSail.copy()

    def calcSpeed(self):
        acceleration = self.acceleration()
        print("Angle to Wind:", self.angletoWind)
        print("Acceleration:", acceleration)
        self.speed = np.clip(self.speed + acceleration, minSpeed*self.wind[0], maxSpeed(self.angletoWind)*self.wind[0])
        print("Speed:", self.speed)
        self.speedx = math.sin(math.radians(self.angle))*self.speed
        print("Speed X:", self.speedx)
        self.speedy = math.cos(math.radians(self.angle))*self.speed
        print("Speed Y:", self.speedy)

    def acceleration(self):
        self.wind = localWind(self.hullRect.centerx, self.hullRect.centery)
        if self.tack == "starboard":
            self.angletoWind = self.angle - (100 - (self.sailAngle - 260)) - self.wind[1]
        else:
            self.angletoWind = (180 - self.angle % 180) - self.sailAngle - self.wind[1]
        return accelerationFunction(self.angletoWind)*self.wind[0]

    def update(self):
        self.move()
        self.turn((keys[pygame.K_d] - keys[pygame.K_a]))
        self.changeTack()
        self.calcSpeed()

    def move(self):
        velocity = self.acceleration()
        self.posx -= self.speedx
        self.posy -= self.speedy

keys = pygame.key.get_pressed()
def tick():
    if running:
        global keys
        player.update()
        threading.Timer(0.05, tick).start()

# Player
player = Boat()

running = True

tick()
# Game loop
while running:

    # Check for events
    for event in pygame.event.get():
        # Check if quit button pressed and quit
        if event.type == pygame.QUIT:
            running = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    player.trimSail(1)
                elif event.button == 4:
                    player.trimSail(-1)

    keys = pygame.key.get_pressed()
    screen.fill((41, 74, 143))
    player.draw()
    # Update screen
    pygame.display.update()

pygame.quit()
sys.exit()