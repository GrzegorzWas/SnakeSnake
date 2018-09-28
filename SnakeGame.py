import pygame
import argparse
import time
from Players import Player1, Player2
from UI import UI, UIPane
from GameManager import GameManager, GameState, GameMode
from Utility import Display
#from pygame.locals import *

class Setup:
    Arcade = 0
    Desktop = 1
    Fullscreen = 3
    Windowed = 4

class SnakeGame:
    """
    Main game class
    """
    def __init__(self, s_width, s_height, setup):       
        pygame.init()
        pygame.font.init()

        self.arcade = False
        fullscreen = False
        for opt in setup:
            if opt == Setup.Arcade:
                self.arcade = True
            elif opt == Setup.Fullscreen:
                fullscreen = True
            
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()

        self.display = Display((s_width, s_height), fullscreen)
        self.clock = pygame.time.Clock()
        self.FPS = 60

        self.ui = UI(self. display)
        if self.arcade:
            if len(self.joysticks) == 0:  
                print("=================== plug in the controller ===================")  
                exit(1)
            self.ui.enable_arcade_mode()
        
        self.selected_speed = "speed Medium"
        self.game_manager = GameManager(self.display, self.ui, GameMode.EatToGrow, GameState.Menu)

    def start_new_game(self, mode):
        """
        Start a new game
        """ 
        self.display.clear()  
        #self.ui.hide()
        if self.selected_speed == "speed Slow":
            self.game_manager.set_players_speed(1.9)
        elif self.selected_speed == "speed Medium":
            self.game_manager.set_players_speed(3)
        elif self.selected_speed == "speed Fast":
            self.game_manager.set_players_speed(5)
        self.game_manager = GameManager(self.display, self.ui, mode, GameState.Running, self.game_manager.player1, self.game_manager.player2)     

    def handle_events(self):
        """
        Invoke handlers for desired events during game
        """
        keys = pygame.key.get_pressed()
        if self.game_manager.game_state == GameState.Running:
            if self.arcade:
                self.game_manager.control_players_arcade(self.joysticks)            
            else:
                self.game_manager.control_players(keys)
        elif self.arcade:
            self.ui.arcade_control(self.joysticks[1])
        # elif self.game_manager.game_state == GameState.Finished or \
        # self.game_manager.game_state == GameState.Menu:
        #     self.ui.control(keys)


        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_manager.game_state = GameState.Quit  
                if self.game_manager.game_state == GameState.Finished or\
                self.game_manager.game_state == GameState.Menu :
                    if event.type == pygame.KEYDOWN and not self.arcade:
                        self.ui.control(event.key)
                        #self.start_new_game(GameMode.EatToSurvive)

    def handle_ui_response(self):
        option = self.ui.get_selected_option()
        
        #main menu
        if option == "Play":
            #self.game_manager.game_state = GameState.Menu
            pass
        elif option == "Quit":
            self.ui.hide()
            self.game_manager.game_state = GameState.Quit
        
        #settings menu
        elif option == "p1 Absolute":
            self.game_manager.player1.steering_mode="absolute"
        elif option == "p1 Relative":
            self.game_manager.player1.steering_mode="relative"
        elif option == "p2 Absolute":
            self.game_manager.player2.steering_mode="absolute"
        elif option == "p2 Relative":
            self.game_manager.player2.steering_mode="relative"
        elif option == "P1 Key Bindings":
            self.ui.load_controls(self.game_manager.player1.controls)
        elif option == "P2 Key Bindings":
            self.ui.load_controls(self.game_manager.player2.controls)

        #key bindings menu
        elif option == "Apply":
            if self.ui.currently_changed_player == "p1":
                self.game_manager.player1.controls = self.ui.loaded_player_controls
            elif self.ui.currently_changed_player == "p2":
                self.game_manager.player2.controls = self.ui.loaded_player_controls

        #speed menu
        elif option == "speed Slow" or option == "speed Medium" or option == "speed Fast":
            self.selected_speed = option

        #play menu
        elif option == "Standard":
            self.start_new_game(GameMode.EatToGrow)
        elif option == "Infinite":
            self.start_new_game(GameMode.InfiniteSnake)
        elif option == "Starve":
            self.start_new_game(GameMode.EatToSurvive)
        
        #endgame menu
        elif option == "Play Again":
            self.start_new_game(self.game_manager.game_mode)
        elif option == "Return to main menu":
            self.game_manager.game_state = GameState.Menu
        

    def render_scene(self):
        """
        Draw objects onto the screen. 
        All the rendering is done here
        """
        if self.game_manager.game_state == GameState.Running or\
        self.game_manager.game_state == GameState.Finished:
            self.display.erase_points()
            self.game_manager.draw_players()

        self.ui.draw()
        pygame.display.flip()
        # if self.game_manager.game_state == GameState.Finished:
        #     time.sleep(0.5)

    def cleanup(self):
        """
        Cleanup after the game has ended
        """
        pygame.quit()

    def main_loop(self):
        """
        Main loop of the game. 
        """
        while self.game_manager.game_state != GameState.Quit:

            self.handle_events()
            self.handle_ui_response()
            #in menu
            if self.game_manager.game_state == GameState.Menu:  
                self.display.clear()

            #in game
            elif self.game_manager.game_state == GameState.Running:
                self.game_manager.move_players()

            #after game
            elif self.game_manager.game_state == GameState.Finished:
                if self.game_manager.winner == None:
                    self.game_manager.player1.decay()
                    self.game_manager.player2.decay()                  
                else:
                    self.game_manager.loser.decay()
                    self.game_manager.loser.draw()

            #perform game manager actions
            self.game_manager.act()
            #do all the rendering stuff
            self.render_scene()
            #control FPS
            self.clock.tick(self.FPS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--size", default="1000x900")
    parser.add_argument("-a", "--arcade", action="store_true")
    parser.add_argument("-f", "--fullscreen", action="store_true")
    args = parser.parse_args()

    setup = []

    if args.arcade:
            setup.append(Setup.Arcade)
    else:
        setup.append(Setup.Desktop)

    if args.fullscreen:
        setup.append(Setup.Fullscreen)
    
    s_width, s_height = [int(x) for x in args.size.split("x")]

    game = SnakeGame(s_width, s_height, setup)
    game.main_loop()
        