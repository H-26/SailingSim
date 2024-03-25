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
    def draw(self, screen, screen_size, boat_posx, boat_posy):
        if settings.center_boat:
            temp_image = self.centreimage
            map_rect = temp_image.get_rect()
            map_rect.center = screen_size[0] / 2 - boat_posx * settings.scale, screen_size[1] / 2 - boat_posy * settings.scale
        else:
            temp_image = self.mapimage
            map_rect = temp_image.get_rect()
            map_rect.center = screen_size[0] / 2 - self.pos[0], screen_size[1] / 2 - self.pos[1]
        screen.blit(temp_image, map_rect)
