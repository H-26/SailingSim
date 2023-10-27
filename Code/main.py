# Imports
import pygame, sys, threading
import numpy as np
from scipy.interpolate import CubicHermiteSpline
import math

# Setup
pygame.init()

#Interpulation graph
x = np.array([-360,0,90,180,270,360])
y = np.array([-1,-0.1,1,0.4,1,-0.1])
speedfunction = CubicHermiteSpline(x=x, y=y, dydx=np.zeros_like(y))

# Window initiation
screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))

pygame.display.set_caption("SailingSim")
icon = pygame.image.load("../Assets/Boat.png")  # To change Icon
pygame.display.set_icon(icon)

def localWind(posx, posy):
    return(2,0)


class Boat(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.scale = 0.05
        self.posx = 400
        self.posy = 300
        self.angle = 0
        self.angular_velocity = 0
        self.hull = pygame.transform.scale(pygame.image.load("../Assets/Boat.png").convert_alpha(), ((1210*self.scale), (916*self.scale)))
        self.hullRect = self.hull.get_rect()
        self.tack = "port"

        self.portSail = pygame.transform.scale(pygame.image.load("../Assets/portSail.png").convert_alpha(), ((1250*self.scale), (1250*self.scale)))
        self.starboardSail = pygame.transform.scale(pygame.image.load("../Assets/starboardSail.png").convert_alpha(), ((1250*self.scale), (1250*self.scale)))

        self.sail = pygame.transform.scale(pygame.image.load("../Assets/portSail.png").convert_alpha(), ((1250*self.scale), (1250*self.scale)))
        self.sailAngle = 0

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

    def rotate(self, angle):
        self.angle = (self.angle + angle) % 360

    def rotateSail(self, angle):
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

    def angularVelocity(self, keyspressed):
        deceleration = 0.5
        if keyspressed != 0:
            angular_velocity
            if self.angular_velocity > 0:
                self.angular_velocity = max(0,self.angular_velocity - deceleration)
            elif self.angular_velocity < 0:
                self.angular_velocity = min(0, self.angular_velocity + deceleration)

    # def direction(self):


    def getVelocity(self):
        wind = localWind(self.hullRect.centerx, self.hullRect.centery)
        if self.tack == "starboard":
            angletoWind = self.angle - (100 - (self.sailAngle - 260)) - wind[1]
        else:
            angletoWind = (180 - self.angle % 180) - self.sailAngle - wind[1]
        # print("Boat Angle:", self.angle, (180 - self.angle % 180))
        # print("Sail Angle:", self.sailAngle)
        # print("Tack:", self.tack)
        print("Angle to wind:", angletoWind)
        return speedfunction(angletoWind)*wind[0]

    def update(self):
        self.move()
        self.rotate((keys[pygame.K_d] - keys[pygame.K_a]) * 1)
        self.changeTack()

    def move(self):
        velocity = self.getVelocity()
        self.posx -= math.sin(math.radians(self.angle))*velocity
        self.posy -= math.cos(math.radians(self.angle))*velocity

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
                    player.rotateSail(1)
                elif event.button == 4:
                    player.rotateSail(-1)

    keys = pygame.key.get_pressed()
    screen.fill((41, 74, 143))
    player.draw()
    # Update screen
    pygame.display.update()

pygame.quit()
sys.exit()