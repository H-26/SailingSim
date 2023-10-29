# Imports
import pygame, sys, threading
import numpy as np
from scipy.interpolate import CubicHermiteSpline
import math
import noise

# Setup
pygame.init()

# accelerationFunction graph
x = np.array([-180, 0, 20, 35, 70, 180])
y = np.array([-0.4, -0.01, -0.01, 0.3, 0.5, -0.05])
accelerationFunction = CubicHermiteSpline(x=x, y=y, dydx=np.zeros_like(y))

# maxSpeed graph
x = np.array([-180, 0, 30, 100, 180, 200])
y = np.array([0.5, 0.7, 0.7, 1, 0.75, 0.9])
# y = np.array([1, 1, 1, 1, 1])
maxSpeed = CubicHermiteSpline(x=x, y=y, dydx=np.zeros_like(y))

# minSpeed
x = np.array([-180, 90, 200])
y = np.array([-0.9, 0, 0])
minSpeed = CubicHermiteSpline(x=x, y=y, dydx=np.zeros_like(y))

# Window initiation
screenWidth = 900
screenHeight = 700
screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)

pygame.display.set_caption("SailingSim")
icon = pygame.image.load("../Assets/Boat.png")  # To change Icon
pygame.display.set_icon(icon)

def localWind(posx, posy):
    return(5,0)
    # windspeed = 5
    # print(noise.pnoise2(float(posx), float(posy), octaves=1, persistance=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0.0))
    # return windspeed * int(noise.pnoise2(posx + ((math.sin(math.radians(windspeed)) * windspeed) * (pygame.time.get_ticks() / 50)), posy - ((math.sin(math.radians(windspeed)) * (0.1 * windspeed)) * (pygame.time.get_ticks() / 50)), octaves=1, persistance=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0.0))

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
        self.angularVelocity = 0

        self.hull = pygame.transform.scale(pygame.image.load("../Assets/Boat.png").convert_alpha(), ((1210*self.scale), (916*self.scale)))
        self.hullRect = self.hull.get_rect()
        self.tack = "port"

        self.portSail = pygame.transform.scale(pygame.image.load("../Assets/portSail.png").convert_alpha(), ((1250*self.scale), (1250*self.scale)))
        self.starboardSail = pygame.transform.scale(pygame.image.load("../Assets/starboardSail.png").convert_alpha(), ((1250*self.scale), (1250*self.scale)))

        self.sail = pygame.transform.scale(pygame.image.load("../Assets/portSail.png").convert_alpha(), ((1250*self.scale), (1250*self.scale)))
        self.sailAngle = 10
        self.wind = localWind(self.hullRect.centerx, self.hullRect.centery)
        self.sailAngleToWind = (180 - self.angle % 180) - self.sailAngle - self.wind[1]
        self.boatAngleToWind = (180 - self.angle % 180) - self.wind[1]

    def draw(self):
        temphull = self.hull.copy()
        self.hullRect = temphull.get_rect()
        # Draw sail on boat
        tempsail = pygame.transform.rotate(self.sail, self.sailAngle)
        self.sailRect = tempsail.get_rect()
        self.sailRect.center = self.hullRect.centerx, (270*self.scale)
        temphull.blit(tempsail, self.sailRect)
        # Draw boat on screen
        temphull = pygame.transform.rotate(temphull, self.angle)
        self.hullRect = temphull.get_rect()
        self.hullRect.center = self.posx, self.posy
        screen.blit(temphull, self.hullRect)

    def turn(self, angle):
        angularvelocitysteps = 5
        if angle != 0:
            self.angularVelocity = np.clip(self.angularVelocity + (angle / angularvelocitysteps), -5, 5)
        else:
            if self.angularVelocity > 0:
                self.angularVelocity = np.clip((self.angularVelocity - ((self.angularVelocity * self.speed) / angularvelocitysteps)), 0, 5)
            elif self.angularVelocity < 0:
                self.angularVelocity = np.clip((self.angularVelocity + ((-self.angularVelocity * self.speed) / angularvelocitysteps)), -5, 0)
        self.angle = (self.angle + np.clip((self.angularVelocity * self.speed), -3, 3)) % 360

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

    def calcSpeed(self):
        acceleration = self.acceleration()
        self.speed = np.clip(self.speed + acceleration, minSpeed(self.boatAngleToWind) * self.wind[0], maxSpeed(self.boatAngleToWind) * self.wind[0])
        self.speedx = math.sin(math.radians(self.angle))*self.speed + (math.sin(math.radians(self.wind[1])) * (0.1 * self.wind[0]))
        self.speedy = math.cos(math.radians(self.angle))*self.speed - (math.cos(math.radians(self.wind[1])) * (0.1 * self.wind[0]))

    def acceleration(self):
        self.wind = localWind(self.hullRect.centerx, self.hullRect.centery)
        if self.tack == "starboard":
            self.boatAngleToWind = (self.angle + self.wind[1]) % 360
            self.sailAngleToWind = self.boatAngleToWind - (100 - (self.sailAngle - 260))
        elif self.tack == "port":
            self.boatAngleToWind = (360 - self.angle - self.wind[1]) % 360
            self.sailAngleToWind = self.boatAngleToWind - self.sailAngle
        return accelerationFunction(self.sailAngleToWind)*self.wind[0]

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

def debugtick():
    if running:
        print("================================")
        # print("Boat Angle to Wind:", player.boatAngleToWind)
        # print("Boat Angle:", player.angle)
        # print("Wind Angle:", player.wind[1])
        # print("Pos X:", player.posx)
        # print("Pos Y:", player.posy)
        print("Tack:", player.tack)
        print("Sail Angle to Wind:", player.sailAngleToWind)
        print("Starboard Boat angle", (player.angle + player.wind[1]) % 360)
        # print("Acceleration:", player.acceleration())
        # print("Speed:", player.speed)
        # print("Angular Velocity", player.angularVelocity)
        threading.Timer(1,debugtick).start()

def tick():
    if running:
        global keys
        player.update()
        threading.Timer(0.05, tick).start()

# Player
player = Boat()

running = True

tick()
debugtick()
# Game loop
while running:

    # width, height = pygame.display.get_surface().get_size()
    # for posx in range(width):
    #     for posy in range(height):
    #         screen.set_at(posx, posy, (localWind(x,y), 0, 0))


    # Check for events
    for event in pygame.event.get():
        # Check if quit button pressed and quit
        if event.type == pygame.QUIT:
            running = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    player.trimSail(-1)
                elif event.button == 4:
                    player.trimSail(1)

    keys = pygame.key.get_pressed()
    screen.fill((41, 74, 143))
    player.draw()
    # Update screen
    pygame.display.update()

pygame.quit()
sys.exit()