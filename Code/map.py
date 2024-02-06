import pygame
import settings
import numpy as np
class Map(pygame.sprite.Sprite):

    def __init__(self, map):
        super().__init__()
        self.image = pygame.image.load("Assets/" + map + ".png").convert_alpha()
        self.centreimage = pygame.transform.scale(self.image.copy(), ((self.image.get_width() * 5 * settings.centre_scale), (self.image.get_height() * 5 * settings.centre_scale)))
        self.mapimage = pygame.transform.scale(self.image.copy(), ((self.image.get_width() * 5 * settings.map_scale), (self.image.get_height() * 5 * settings.map_scale)))
        self.pos = np.array([0, 0])
        # Function draw the map
    def draw(self, screen, screenSize, boatposx, boatposy, mapposx, mapposy):
        if settings.center_boat:
            tempimage = self.centreimage
            maprect = tempimage.get_rect()
            maprect.center = screenSize[0]/2 - boatposx*settings.scale, screenSize[1]/2 - boatposy*settings.scale
        else:
            tempimage = self.mapimage
            maprect = tempimage.get_rect()
            maprect.center = screenSize[0]/2 - mapposx, screenSize[1]/2 - mapposy
        screen.blit(tempimage, maprect)
