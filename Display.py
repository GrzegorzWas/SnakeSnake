import pygame

class Display():

    def __init__(self, size):
        self.width, self.height = size
        self.size = size
        self._display_surface = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

    def draw_point(self, pos, color, radius=3):
        pygame.draw.circle(self._display_surface, color, pos, radius)