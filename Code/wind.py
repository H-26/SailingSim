import numpy as np
from scipy.interpolate import CubicHermiteSpline
import noise

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

def localWind(posx, posy):
    return(5,0)
    windspeed = 5
    # print(noise.pnoise2(posx, float(posy), octaves=1, persistance=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0.0))
    # return windspeed * int(noise.pnoise2(posx + ((math.sin(math.radians(windspeed)) * windspeed) * (pygame.time.get_ticks() / 50)), posy - ((math.sin(math.radians(windspeed)) * (0.1 * windspeed)) * (pygame.time.get_ticks() / 50)), octaves=1, persistance=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0.0))
    # return (windspeed * (noise.pnoise2(posx, posy - ((math.sin(math.radians(windspeed)) * (0.1 * windspeed)) * (pygame.time.get_ticks() / 50)), octaves=1, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0)), 0)