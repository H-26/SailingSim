import pygame
class Map(pygame.sprite.Sprite):

    def __init__(self, scale, map):
        super().__init__()
        self.scale = scale
        self.image = pygame.transform.scale(pygame.image.load("../Assets/" + map + ".png").convert_alpha(), ((1210*self.scale), (916*self.scale)))