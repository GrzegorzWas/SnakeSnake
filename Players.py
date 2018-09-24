import pygame
import random
from Snake import Snake

class Player1(Snake):
    def __init__(self, display):
        super().__init__((display.width * 0.75, display.height * 0.5), display)
        self.direction.rotate(random.randrange(0, 360))
        self.color = (55, 111, 158)
        self.controls = {
            "left": pygame.K_LEFT, 
            "right":pygame.K_RIGHT, 
            "up": pygame.K_UP, 
            "down": pygame.K_DOWN
            }
        self.steering_mode="relative"
    def __str__(self):
        return "Blue Player"

class Player2(Snake):
    def __init__(self, display):
        super().__init__((display.width * 0.25, display.height * 0.5), display)
        self.direction.rotate(random.randrange(0, 360))
        self.color = (255, 220, 77)
        self.controls = {
            "left": pygame.K_a, 
            "right":pygame.K_d, 
            "up": pygame.K_w, 
            "down": pygame.K_s
            }
        self.steering_mode="absolute"

    def __str__(self):
        return "Yellow Player"