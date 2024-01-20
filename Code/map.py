import pygame
import settings
class Map(pygame.sprite.Sprite):

    def __init__(self, map):
        super().__init__()
        self.scale = settings.scale
        self.image = pygame.image.load("Assets/" + map + ".png").convert_alpha()

        # Function draw the map
    def draw(self, screen, screenSize, posx, posy):
        tempimage = self.image.copy()
        tempimage = pygame.transform.scale(tempimage, ((self.image.get_width() * 5 * settings.scale), (self.image.get_height()* 5 * settings.scale)))
        maprect = tempimage.get_rect()
        if settings.centerBoat:
            maprect.center = screenSize[0]/2 - posx*settings.scale, screenSize[1]/2 - posy*settings.scale
        else:
            maprect.center = (screenSize[0]/2), (screenSize[1]/2)
        screen.blit(tempimage, maprect)
