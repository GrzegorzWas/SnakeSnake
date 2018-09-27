import pygame
import time
from itertools import cycle
from copy import copy

class UIState:
    Hidden = 0
    Visible = 1

class MenuOption:
    """Base class for interactive menu options"""
    def __init__(self, text, position, redirect):
        self.text = text
        self.position = position
        #the menu pane the user is taken to
        self.redirect = redirect

        self.selected = False
        self.font_color = (230, 230, 230)
        self.font_size = 30
        self.selected_color = (255, 220, 77)
        self.selected_border = (55, 111, 158)
        self.id = ""
        
    def draw(self, display):

        if self.selected:
            display.draw_text(  self.text, self.font_size, self.selected_color, position=self.position, font="Pixel", bordered=True, border_color=self.selected_border)
        else:
            display.draw_text(  self.text, self.font_size, (255, 255, 255), position=self.position, font="Pixel", bordered=True, border_color=(0,0,0), border_thickness=3)

    def __str__(self):
        return self.text

    def choose(self):
        pass

    def unchoose(self):
        pass

    def get_group(self):
        return "default"

class SettingsOption(MenuOption):
    def __init__(self, text, position, redirect, group, selected=False):
        super().__init__(text, position, redirect)
        if text == "Relative" or selected:
            self.highlighted = True
        else:
            self.highlighted = False
        self.highlighted_color = (89, 179, 0)
        self.group = group

    def choose(self):
        self.highlighted = True

    def unchoose(self):
        self.highlighted = False

    def draw(self, display):
        if self.highlighted:
            display.draw_text(  self.text, self.font_size, self.selected_color, position=self.position, font="Pixel", bg_color=self.highlighted_color)
        super().draw(display)

    def get_group(self):
        return self.group

    def __str__(self):
        return self.group + " " + self.text

class MenuDecorator:
    """Abstract base class for uninteractive menu items"""
    def __init__(self, position):
        self.position = position
        self.id = ""
        
    def draw(self, display):
        pass

class MenuLabel(MenuDecorator):
    def __init__(self, text, position, size=70, color=(255, 220, 77), border = (55, 111, 158), font="Bungee"):
        super().__init__(position)
        self.text = text

        self.font = font
        self.font_size = size
        self.color = color
        self.border = border
        self.id = ""
        
    def draw(self, display):
        display.draw_text(  self.text, self.font_size, self.color, position=self.position, font=self.font, bordered=True, border_color=self.border)

    def __str__(self):
        return self.text 

class MenuSeparator(MenuDecorator):
    def __init__(self, position, thickness, length, color=(100, 100, 100)):
        super().__init__(position)
        self.thickness = thickness
        self.length = length
        self.color = color
        self.id = ""
        
    def draw(self, display):
        display.draw_horizontal_line(self.position, self.thickness, self.length, self.color)


    def __str__(self):
        return "i dont know what you expect here"


class UIPane:
    MainMenu = 0
    PlayMenu = 1
    SettingsMenu = 2
    IngameMenu = 3
    EndgameMenu = 4
    KeyBindingsMenu = 5
    PressKeyPrompt = 6
    SelectSpeedMenu = 7
    Pages = [None, None, None, None, None, None, None, None]

    def __init__(self, buttons, decorators):
        if buttons != None :
            self.buttons = buttons
            self.decorators = decorators
            self.selected_index = 0
            if len(buttons) > 0:
                self.selected_button = buttons[self.selected_index]
                self.buttons[self.selected_index].selected = True
            self.button_groups = {}

            for b in self.buttons:
                if not b.get_group() in self.button_groups.keys():
                    self.button_groups[b.get_group()] = []

                self.button_groups[b.get_group()].append(b)

    def choose_option(self, option):
        if option.get_group() in self.button_groups.keys():
            for b in self.button_groups[option.get_group()]:
                b.unchoose()
            option.choose()

    def select_next_button(self):
        if self.selected_button != None:
            self.selected_index += 1
            self.selected_index = self.selected_index % len(self.buttons)
            self.selected_button.selected = False
        self.selected_button = self.buttons[self.selected_index]
        self.selected_button.selected = True

    def select_previous_button(self):
        if self.selected_button != None:
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index += len(self.buttons)
            self.selected_button.selected = False
        self.selected_button = self.buttons[self.selected_index]
        self.selected_button.selected = True

    def select_first_button(self):
        if self.buttons != None and len(self.buttons) > 0:
            self.selected_button.selected = False
            self.selected_index=0
            self.selected_button = self.buttons[0]
            self.selected_button.selected = True

    def draw(self, display):
        for b in self.buttons:
            b.draw(display)
        for l in self.decorators:
            l.draw(display)


class UI:
    def __init__(self, display):
        self.menu_controls = {
            "left": pygame.K_LEFT, 
            "right":pygame.K_RIGHT, 
            "up": pygame.K_UP, 
            "down": pygame.K_DOWN,
            "select":pygame.K_RETURN
            }
        self.display = display
        self.state = UIState.Visible
        self.winner = None
        self.loser = None
        self.loaded_player_controls = {}
        self.currently_changed_control = ""
        self.currently_changed_player = ""
        self.selected_speed = ""
        self.p1_score = 0
        self.p2_score = 0
        self.arcade_mode = False
        self.arcade_select_button = 0
        #arcade command last press time
        self.acc_up = None
        self.acc_down = None
        self.acc_select = None
        self.acc_interval = 1

        #main menu
        UIPane.Pages[UIPane.MainMenu] = UIPane(
            buttons = [
                MenuOption("Play",      (None, self.display.height/2 - 80), UIPane.PlayMenu),
                MenuOption("Settings",  (None, self.display.height/2), UIPane.SettingsMenu),
                MenuOption("Quit",      (None, self.display.height/2 + 80), None),
            ],
            decorators = [
                MenuLabel("Snake",      (self.display.width/2 - 250, self.display.height/2 - 250)),
                MenuLabel("Snake",      (self.display.width/2 + 25, self.display.height/2 - 250), color=(55, 111, 158), border = (255, 220, 77))
            ]
        )  
        #play menu
        UIPane.Pages[UIPane.PlayMenu] = UIPane(
            buttons = [
                MenuOption("Standard",  (None, self.display.height/2 - 80), UIPane.IngameMenu),
                MenuOption("Infinite",  (None, self.display.height/2), UIPane.IngameMenu),
                MenuOption("Starve",    (None, self.display.height/2 + 80), UIPane.IngameMenu),
                MenuOption("Return to main menu", (None, self.display.height/2 + 160), UIPane.MainMenu)
            ],
            decorators = [
            ])       
        #settings menu 
        UIPane.Pages[UIPane.SettingsMenu]= UIPane(
            buttons = [
                SettingsOption("Absolute", (None, self.display.height/10 + 160), UIPane.SettingsMenu, "p1"),
                SettingsOption("Relative", (None, self.display.height/10 + 220), UIPane.SettingsMenu, "p1"),
                MenuOption("P1 Key Bindings", (None, self.display.height/10 + 300), UIPane.KeyBindingsMenu),
                SettingsOption("Absolute", (None, self.display.height/10 + 460), UIPane.SettingsMenu, "p2"),
                SettingsOption("Relative", (None, self.display.height/10 + 520), UIPane.SettingsMenu, "p2"),
                MenuOption("P2 Key Bindings", (None, self.display.height/10 + 600), UIPane.KeyBindingsMenu),
                MenuOption("Set speed", (None, self.display.height/10 + 700), UIPane.SelectSpeedMenu),
                MenuOption("Return to menu", (None, self.display.height*9/10), UIPane.MainMenu)
            ],
            decorators = [
                MenuLabel("Controls",       (None, self.display.height/15), 50),
                #MenuSeparator(              (None, self.display.height/10 + 80), 2, 400),
                MenuLabel("Blue player",    (None, self.display.height/10 + 100), 30, color=(55, 111, 158), border = (255, 220, 77)),
                MenuSeparator(              (None, self.display.height/10 + 370), 2, 600),
                MenuLabel("Yellow player",  (None, self.display.height/10 + 400), 30),
                MenuSeparator(              (None, self.display.height/10 + 670), 2, 550)
            ])
        #key bindings menu
        UIPane.Pages[UIPane.KeyBindingsMenu] = UIPane(
            buttons = [
                MenuOption("u",  (self.display.width/2 + 50, self.display.height/5), UIPane.PressKeyPrompt),
                MenuOption("d",  (self.display.width/2 + 50, self.display.height/5 + 100), UIPane.PressKeyPrompt),
                MenuOption("l",  (self.display.width/2 + 50, self.display.height/5 + 200), UIPane.PressKeyPrompt),
                MenuOption("r",  (self.display.width/2 + 50, self.display.height/5 + 300), UIPane.PressKeyPrompt),
                MenuOption("Apply",     (None, self.display.height/5 + 500), UIPane.SettingsMenu),
                MenuOption("Go Back",   (None, self.display.height/5 + 560), UIPane.SettingsMenu)
            ],
            decorators = [
                MenuLabel("Up",     (self.display.width/2 - 170, self.display.height/5), 40),
                MenuLabel("Down",   (self.display.width/2 - 170, self.display.height/5 + 100), 40),
                MenuLabel("Left",   (self.display.width/2 - 170, self.display.height/5 + 200) , 40),
                MenuLabel("Right",  (self.display.width/2 - 170, self.display.height/5 + 300), 40)
            ])   
        #press key prompt
        UIPane.Pages[UIPane.PressKeyPrompt] = UIPane(
            buttons = [],
            decorators = [
                MenuLabel("Press a key", (None, None), 40, color=(255,255,255), border=(0,0,0) ,font="Pixel"),
            ])   
        #select speed menu
        UIPane.Pages[UIPane.SelectSpeedMenu]= UIPane(
            buttons = [
                SettingsOption("Slow", (None, self.display.height/10 + 160), None, "speed"),
                SettingsOption("Medium", (None, self.display.height/10 + 220), None, "speed"),
                SettingsOption("Fast", (None, self.display.height/10 + 280), None, "speed"),
                MenuOption("Go Back", (None, self.display.height/10 + 380), UIPane.SettingsMenu)
            ],
            decorators = [
                MenuLabel("Select speed", (None, self.display.height/10), 50),
            ])
        #ingame menu
        UIPane.Pages[UIPane.IngameMenu] = UIPane(
            buttons = [
            ],
            decorators = [
                MenuSeparator((None, self.display.height), (self.display.height - self.display.play_area_height)*2, self.display.width, color=(150,150,150)),
                MenuSeparator((None, self.display.height*9/10 + 10), 20, self.display.width),
                MenuLabel("Score",  (None, self.display.height*9/10 + 30), 30, font="Pixel", color=(255,255,255), border=(100,100,100)),
                MenuLabel("0",      (self.display.width/10, self.display.height*9/10 + 30), 30, font="Pixel"),
                MenuLabel("0",      (self.display.width*9/10, self.display.height*9/10 + 30), 30, font="Pixel", color=(55, 111, 158), border = (255, 220, 77))
            ])
        #endgame menu
        UIPane.Pages[UIPane.EndgameMenu] = UIPane(
            buttons = [
                MenuOption("Play Again", (None, self.display.height /2 + 80), UIPane.IngameMenu),
                MenuOption("Return to main menu", (None, self.display.height /2 + 160), UIPane.MainMenu)
            ],
            decorators = [      
            ]
        )     
        self.current_page = UIPane.Pages[UIPane.MainMenu]
        self.selected_option = self.current_page.buttons[0]
        UIPane.Pages[UIPane.SelectSpeedMenu].buttons[1].highlighted = True
        

    def show_endgame_prompt(self):
        if self.winner == None:
            self.display.draw_text("Both players shmuck", 40, (255,255,255), (0,0,0))
        else:
            self.display.draw_text(str(self.winner) + " Won", 40, self.winner.color, bordered=True, border_color = self.loser.color, border_thickness=3)
            #self.display.draw_text("Apparently " + str(self.loser) + " sucks", 39, self.loser.color, bold=1)

    def draw(self):
        if self.state == UIState.Visible and self.selected_option != "Quit":  
            if self.current_page == UIPane.Pages[UIPane.EndgameMenu]:   
                self.show_endgame_prompt()
            self.current_page.draw(self.display)

    def arcade_control(self, joystick):
        if self.arcade_mode:
            y = controller.get_axis(1)
            selected = jpystick.get_button(self.arcade_select_button) == pygame.JOYBUTTONDOWN

            if self.current_page == UIPane.Pages[UIPane.PressKeyPrompt]:
                self.loaded_player_controls[self.currently_changed_control] = key_pressed
                self.reload_controls()
                self.current_page = UIPane.Pages[UIPane.KeyBindingsMenu]
            else:
                if y == 1 and time.time() - self.acc_up >= self.acc_interval:
                    self.current_page.select_previous_button()
                    self.acc_up = time.time()
                elif y == -1 and time.time() - self.acc_down >= self.acc_interval:
                    self.current_page.select_next_button()
                    self.acc_down = time.time()
                elif selected and time.time() - self.acc_select >= self.acc_interval:
                    self.acc_select = time.time()
                    if self.current_page == UIPane.Pages[UIPane.KeyBindingsMenu]:
                        if self.current_page.selected_index == 0:
                            self.currently_changed_control = "up"
                        elif self.current_page.selected_index == 1:
                            self.currently_changed_control = "down"
                        elif self.current_page.selected_index == 2:
                            self.currently_changed_control = "left"
                        elif self.current_page.selected_index == 3:
                            self.currently_changed_control = "right"
                    self.current_page.choose_option(self.current_page.selected_button)
                    self.selected_option = str(self.current_page.selected_button)
                    if self.selected_option == "P1 Key Bindings":
                        self. currently_changed_player = "p1"
                    elif self.selected_option == "P2 Key Bindings":
                        self. currently_changed_player = "p2" 
                    if self.current_page.selected_button.redirect != None:
                        
                        redirect = self.current_page.selected_button.redirect
                        self.current_page.select_first_button()
                        self.current_page = UIPane.Pages[redirect]  
        
    def control(self, key_pressed):
        if not self.arcade_mode:
            if self.current_page == UIPane.Pages[UIPane.PressKeyPrompt]:
                self.loaded_player_controls[self.currently_changed_control] = key_pressed
                self.reload_controls()
                self.current_page = UIPane.Pages[UIPane.KeyBindingsMenu]
            else:
                if key_pressed == self.menu_controls["up"]:
                    self.current_page.select_previous_button()
                elif key_pressed == self.menu_controls["down"]:
                    self.current_page.select_next_button()
                elif key_pressed == self.menu_controls["select"]:
                    if self.current_page == UIPane.Pages[UIPane.KeyBindingsMenu]:
                        if self.current_page.selected_index == 0:
                            self.currently_changed_control = "up"
                        elif self.current_page.selected_index == 1:
                            self.currently_changed_control = "down"
                        elif self.current_page.selected_index == 2:
                            self.currently_changed_control = "left"
                        elif self.current_page.selected_index == 3:
                            self.currently_changed_control = "right"
                    self.current_page.choose_option(self.current_page.selected_button)
                    self.selected_option = str(self.current_page.selected_button)
                    if self.selected_option == "P1 Key Bindings":
                        self. currently_changed_player = "p1"
                    elif self.selected_option == "P2 Key Bindings":
                        self. currently_changed_player = "p2" 
                    if self.current_page.selected_button.redirect != None:
                        
                        redirect = self.current_page.selected_button.redirect
                        self.current_page.select_first_button()
                        self.current_page = UIPane.Pages[redirect]         

    def hide(self):
        self.state = UIState.Hidden

    def show_endgame_menu(self):
        self.current_page = UIPane.Pages[UIPane.EndgameMenu]

    def get_selected_option(self):
        option = self.selected_option
        self.selected_option = None
        return option

    def load_controls(self, controls):
        self.loaded_player_controls = copy(controls)
        u = pygame.key.name(controls["up"])
        d = pygame.key.name(controls["down"])
        l = pygame.key.name(controls["left"])
        r = pygame.key.name(controls["right"])

        UIPane.Pages[UIPane.KeyBindingsMenu].buttons[0].text = u
        UIPane.Pages[UIPane.KeyBindingsMenu].buttons[1].text = d
        UIPane.Pages[UIPane.KeyBindingsMenu].buttons[2].text = l
        UIPane.Pages[UIPane.KeyBindingsMenu].buttons[3].text = r

    def reload_controls(self):
        controls = self.loaded_player_controls
        u = pygame.key.name(controls["up"])
        d = pygame.key.name(controls["down"])
        l = pygame.key.name(controls["left"])
        r = pygame.key.name(controls["right"])

        UIPane.Pages[UIPane.KeyBindingsMenu].buttons[0].text = u
        UIPane.Pages[UIPane.KeyBindingsMenu].buttons[1].text = d
        UIPane.Pages[UIPane.KeyBindingsMenu].buttons[2].text = l
        UIPane.Pages[UIPane.KeyBindingsMenu].buttons[3].text = r

    def increment_p1_score(self):
        self.p1_score += 1
        UIPane.Pages[UIPane.IngameMenu].decorators[4].text = str(self.p1_score)

    def increment_p2_score(self):
        self.p2_score += 1
        UIPane.Pages[UIPane.IngameMenu].decorators[3].text = str(self.p2_score)

    def reset_p1_score(self):
        self.p1_score = 0
        UIPane.Pages[UIPane.IngameMenu].decorators[4].text = str(self.p1_score)

    def reset_p2_score(self):
        self.p2_score = 0
        UIPane.Pages[UIPane.IngameMenu].decorators[3].text = str(self.p1_score)

    def disable_quit_button(self):
        del UIPane.Pages[UIPane.MainMenu].buttons[-1]

    def enable_arcade_mode(self):
        self.disable_quit_button()
        #self.arcade_mode = True
        UIPane.Pages[UIPane.SettingsMenu]= UIPane(
            buttons = [
                SettingsOption("Absolute", (None, self.display.height/10 + 160), UIPane.SettingsMenu, "p1"),
                SettingsOption("Relative", (None, self.display.height/10 + 220), UIPane.SettingsMenu, "p1"),
                SettingsOption("Absolute", (None, self.display.height/10 + 460), UIPane.SettingsMenu, "p2"),
                SettingsOption("Relative", (None, self.display.height/10 + 520), UIPane.SettingsMenu, "p2"),
                MenuOption("Set speed", (None, self.display.height/10 + 700), UIPane.SelectSpeedMenu),
                MenuOption("Return to menu", (None, self.display.height*9/10), UIPane.MainMenu)
            ],
            decorators = [
                MenuLabel("Controls",       (None, self.display.height/15), 50),
                #MenuSeparator(              (None, self.display.height/10 + 80), 2, 400),
                MenuLabel("Blue player",    (None, self.display.height/10 + 100), 30, color=(55, 111, 158), border = (255, 220, 77)),
                MenuSeparator(              (None, self.display.height/10 + 370), 2, 600),
                MenuLabel("Yellow player",  (None, self.display.height/10 + 400), 30),
                MenuSeparator(              (None, self.display.height/10 + 670), 2, 550)
            ])



    


