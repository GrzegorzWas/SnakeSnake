import pygame
import math
from copy import copy
from Utility import Point, Display



class Snake():
    """
    Base class for snake players which provides
    functionalities for controlling the snake as well
    as handling its properties and printing it on screen
    """
    def __init__(self, position, display):
        self.controls = {}
        self.body_list = []
        self.display = display

        self.collided = False
        self.collided_color = None
        self.collision_position = None

        self.super_smooth = True

        #starting direction
        self.direction = Point(1.0, 1.0)
        #initial position
        x, y = position
        self.head_pos = Point(x, y)
        self.color = (255, 0, 0)
        self._length = 100.0
        self.speed = 5
        self.rotation_factor =  self.speed**4.2 /100
        self.decay_speed = 4
        
        #the way you want the snake to be controlled
        #can be either absolute or relative
        self.steering_mode= "absolute"
        
    @property
    def length(self):
        return self.body_list.__len__()

    def steer(self, keys_pressed):
        """
        change the direction vector according to keys pressed by user
        """
        new_direction = copy(self.direction)
        x_present = True
        y_present = True

        if self.steering_mode == "absolute":
            if keys_pressed[ self.controls["left"] ]:
                new_direction.x = -1
            elif keys_pressed[ self.controls["right"] ]:
                new_direction.x = 1
            else:
                x_present = False
                new_direction.x = 0
                    
            if keys_pressed[ self.controls["up"] ]:
                new_direction.y = -1
            elif keys_pressed[ self.controls["down"] ]:
                new_direction.y = 1
            else:
                y_present = False
                new_direction.y = 0

            if x_present or y_present:
                if self.direction.angle_to(new_direction) < 180:
                    self.direction.rotate(self.rotation_factor)
                elif self.direction.angle_to(new_direction) >= 180:
                    self.direction.rotate(-self.rotation_factor)

        elif self.steering_mode == "relative":
            if keys_pressed[ self.controls["left"] ]:
                self.direction.rotate(-self.rotation_factor)
            elif keys_pressed[ self.controls["right"] ]:
                self.direction.rotate(self.rotation_factor)


    def move(self):
        """
        handle snake's movement
        """
        #move snake's head in the direction specified by 'direction' vector
        self.body_list.append(self.head_pos)
        self.head_pos += self.direction * self.speed
        
        #make snake appear on the other side of
        # the screen when passing through walls 
        if self.head_pos.x <= 0:
            self.head_pos.x = self.display.play_area_width
        elif self.head_pos.x >= self.display.play_area_width:
            self.head_pos.x = 0

        if self.head_pos.y <= 0:
            self.head_pos.y = self.display.play_area_height    
        elif self.head_pos.y >= self.display.play_area_height:
            self.head_pos.y = 0

        #check for collision
        self.collided, self.collided_color, self.collision_position = self.display.detect_collision(self.head_pos.coords, 5, self.color)

        # if self.collided:
        #     pygame.mixer.music.load("sounds/wilhelm.mp3")
        #     pygame.mixer.music.play()
        #erase snakes tail if it starts to exceed its length
        while self._length != -1 and self.length > self._length:
            self.display.erase_enqueue(self.body_list.pop(0), 8)

    def decay(self):
        for _ in range(self.decay_speed + self.body_list.__len__() // 100):
            if self.body_list.__len__() > 0:
                self.display.erase_enqueue(self.body_list.pop(0), 8)


    def draw(self):
        """
        print the snake onto the screen
        """
        if self.body_list.__len__() > 0:
            self.display.draw_point(self.body_list[0].coords, self.color)      
            self.display.draw_point(self.body_list[-1].coords, self.color)

        if self.super_smooth and self.body_list.__len__() > 1:
            self.display.draw_point(self.body_list[1].coords, self.color)
            #for smoother snake
            dist = self.body_list[-1] - self.body_list[-2]
            if dist.length() < 20:
                between1 = self.body_list[-2] + (dist) /2
                #between2 = self.body_list[-2] + (self.body_list[-1] - self.body_list[-2]) * (2/3)
                self.display.draw_point(between1.coords, self.color)
            #self.display.draw_point(between2.coords, self.color)
            #self.display.erase_enqueue(between, 5)
            #self.display.draw_point(self.body_list[-1].coords, self.display.bg_color, 2)

    

