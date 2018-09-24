import pygame
import math


def colors_equal(color1, color2):
    for i in range(0,3):
        if color1[i] != color2[i]:
            return False
    return True




class Point():
    """
    Data structure for point storing and basic 2D vector arythmetics
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def rotate(self, angle):
        if angle < 0:
            angle = 360 + angle
        angle = angle * math.pi/180
        old_x = self.x
        old_y = self.y
        self.x = old_x * math.cos(angle) - old_y * math.sin(angle)
        self.y = old_x * math.sin(angle) + old_y * math.cos(angle)

    def angle_to(self, p):
        angle = math.atan2(p.y, p.x) - math.atan2(self.y, self.x)
        if angle < 0: 
            angle += 2 * math.pi
        return angle * 180/math.pi

    def distance_to(self, p):
        return ( (self.x - p.x)**2 + (self.y - p.y)**2 ) **0.5 

    def length(self):
         return ( self.x**2 + self.y**2 )**0.5

    def dot_product(self, p):
        return self.x * p.x + self.y * p.y

    @property
    def coords(self):
        return (int(round(self.x, 0)), int(round(self.y, 0)) )

    def __add__(self, p):
        """
        '+' operator override
        """
        return Point(self.x + p.x, self.y + p.y)

    def __mul__(self, scalar):
        """
        '*' operator override
        """
        return Point(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        """
        '/' operator override
        """
        return Point(self.x / scalar, self.y / scalar)

    # def __iadd__(self, p):
    #     self.x += p.x
    #     self.y += p.y
    #     return self

    def __sub__(self, p):
        """
        '-' operator override
        """
        return Point(self.x - p.x, self.y - p.y)



class Display():
    """
    Wrapper class for pygame rendering and display handling
    """  
    def __init__(self, size, play_area_size=(None, None)):
        self.width, self.height = size
        self.size = size
        self.play_area_size = play_area_size
        self._display_surface = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.erase_list = []
        self.bg_color = (0,0,0)
        self._display_surface.fill(self.bg_color)

    @property
    def play_area_width(self):
        if self.play_area_size[0] != None:
            return self.play_area_size[0]
        else:
            return self.width

    @property
    def play_area_height(self):
        if self.play_area_size[1] != None:
            return self.play_area_size[1]
        else:
            return self.height

    def erase_enqueue(self, point, radius):
        """
        Enqueue the points to be erased during the rendering process
        Args:
            point (Point): point on the display surface that should be erased
        """
        self.erase_list.append((point, radius))

    def clear(self):
        self._display_surface.fill(self.bg_color)

    def draw_point(self, pos, color, radius=5):
        """
        Draw point on display surface
        Args:
            pos ((int, int)): tuple of x and y point coords
            color ((int, int, int)): tuple of rgb color values
            radius (int): radius of the drawn point. 5 is default 
        """
        pygame.draw.circle(self._display_surface, color, pos, radius)

    def draw_horizontal_line(self, position, thickness, length, color):
        """
        Draw line on display surface
        Args:
            position ((int, int)): tuple of x and y line coords. center is default 
            thickness (int): thickness in pixels
            length (int): length in pixels
            color ((int, int, int)): tuple of rgb color values
        """
        start_pos = None
        end_pos = None
        if position == None:
            start_position = (self.width // 2 -  length/2), (self.height // 2)
            end_position = (self.width // 2 +  length/2), (self.height // 2)
        else:
            x, y = position
            if x == None:
                x = (self.width // 2 -  length/2)
            if y == None:
                y = (self.height // 2)
            start_pos = x, y
            end_pos = x + length, y

        pygame.draw.line(self._display_surface, color, start_pos, end_pos, thickness)

    def draw_rect(self, size, color, position=None):
        """
        Draw rectangle on display surface
        Args:
            size ((int, int)): tuple of width and height for rect drawn
            color ((int, int, int)): tuple of rgb color values
            position ((int, int)): tuple of x and y rect coords. center is default 
        """
        r_width, r_height = size
        if position == None:
            position = (self.width // 2 -  r_width/2), (self.height // 2 -  r_height/2)

        rect = pygame.Rect(position, size)
        pygame.draw.rect(self._display_surface, color, rect)

    def draw_text(self, text, font_size, color, bg_color=None, position=None, font=None, bold=0, bordered=False, border_color=(255,255,255), border_thickness=2):
        """
        Draw text on display surface
        Args:
            text (string): text to be drawn on screen
            font_size (int): size of the font
            color ((int, int, int)): tuple of rgb color values
            position ((int, int)): tuple of x and y rect coords. Center is default 
            font (Font): font of the drawn text. SysFont is default
        """
        if font == None:
            #font = pygame.font.SysFont("", font_size, bold)
            font = pygame.font.Font("fonts/Bungee.ttf", font_size)
        else:
            font = pygame.font.Font("fonts/"+font+".ttf", font_size)
            
        font.set_bold(bold)

        rendered_text = font.render(text, False, color, bg_color)
        border = font.render(text, False, border_color, bg_color)

        
        r_width = rendered_text.get_width()
        r_height = rendered_text.get_height()
        x , y = None, None
        if position == None:
            position = (self.width // 2 -  r_width/2), (self.height // 2 -  r_height/2)
        else:
            x, y = position
            if x == None:
                x = (self.width // 2 -  r_width/2)
            if y == None:
                y = (self.height // 2 -  r_height/2)
            
            position = x, y

        if bordered:
            self._display_surface.blit(border, (position[0] - border_thickness, position[1] - border_thickness))
            self._display_surface.blit(border, (position[0] + border_thickness, position[1] + border_thickness))
            self._display_surface.blit(border, (position[0] + border_thickness, position[1] - border_thickness))
            self._display_surface.blit(border, (position[0] - border_thickness, position[1] + border_thickness))
        self._display_surface.blit(rendered_text, position)
        
        
    def erase_points(self):
        while len(self.erase_list) > 0:
            point, radius = self.erase_list.pop()
            self.draw_point(point.coords, self.bg_color, radius)   

    def detect_collision(self, coords, r, color):
        """
        Looks for pixel with color different than given and background
        
        """
        body_color_count = 0
        y, x = coords
        pixels_in_body = False
        for i in range(y-r, y+r) :
            j = x
            while (r-2)**2 <= (j-x)**2 + (i-y)**2 <= (r+1)**2 :
                try:
                    p_color = self._display_surface.get_at((i, j))  
                    if colors_equal(p_color, color):
                        body_color_count += 1
                    elif (j-x)**2 + (i-y)**2 < (r+1)**2 and not colors_equal(p_color, self.bg_color) and not colors_equal(p_color, color):
                        return (True, p_color, Point(i, j))
                except IndexError:
                    pass
                j -= 1

            j= x + 1
            while (r-2)**2 <= (j-x)**2 + (i-y)**2 <= (r+1)**2:
                try:
                    p_color = self._display_surface.get_at((i, j))
                    if colors_equal(p_color, color):
                        body_color_count += 1   
                    if (j-x)**2 + (i-y)**2 < (r+1)**2 and not colors_equal(p_color, self.bg_color) and not colors_equal(p_color, color): 
                        return (True, p_color, Point(i, j))
                except IndexError:
                    pass
                j += 1
            
        if body_color_count > (r) * 4.7:
            return (True, color, None)
        else:
            return (False, color, None) 
