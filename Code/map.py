import pygame
import settings
class Map(pygame.sprite.Sprite):

    def __init__(self, map):
        super().__init__()
        self.image = pygame.image.load("Assets/" + map + ".png").convert_alpha()
        self.centreimage = pygame.transform.scale(self.image.copy(), ((self.image.get_width() * 5 * settings.centreScale), (self.image.get_height()* 5 * settings.centreScale)))
        self.mapimage = pygame.transform.scale(self.image.copy(), ((self.image.get_width() * 5 * settings.mapScale), (self.image.get_height()* 5 * settings.mapScale)))
        # Function draw the map
    def draw(self, screen, screenSize, posx, posy, prevCenterboat):
        if settings.centerBoat:
            tempimage = self.centreimage
            maprect = tempimage.get_rect()
            maprect.center = screenSize[0]/2 - posx*settings.scale, screenSize[1]/2 - posy*settings.scale
        else:
            tempimage = self.mapimage
            maprect = tempimage.get_rect()
            maprect.center = (screenSize[0]/2), (screenSize[1]/2)
        screen.blit(tempimage, maprect)
