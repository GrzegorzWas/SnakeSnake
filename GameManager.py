import random
import pygame

from UI import UI, UIState, UIPane
from Players import Player1, Player2
from Utility import Point, colors_equal


class GameState:
    Menu = 0
    Running = 1
    Finished = 2
    Quit = 3


class GameMode:
    InfiniteSnake = 0
    EatToGrow = 1
    EatToSurvive = 2
    

class GameManager:
    """
    Class rsponsible for all the game logic
    """
    def __init__(self, display, ui, game_mode, game_state=GameState.Menu, p1=None, p2=None):
        self.display = display
        self.player1 = Player1(self.display)
        self.player2 = Player2(self.display)
        
        #copy settings from players used in previous game
        if p1 != None:
            self.player1.steering_mode = p1.steering_mode     
            self.player1.controls = p1.controls
            self.player1.speed = p1.speed
        if p2 != None:
            self. player2.controls = p2.controls
            self.player2.steering_mode = p2.steering_mode 
            self.player2.speed = p2.speed

        #setup ui
        self.ui = ui
        self.ui.reset_p1_score()
        self.ui.reset_p2_score()
        self.game_mode = game_mode

        #setup game management stuff
        self.pickup_color = (255, 255, 255)
        self.pickup_radius = 7
        self.pickups = []
        self.winner = None
        self.loser = None
        self.game_state = game_state

        #setup the game based on selected game mode
        if self.game_mode == GameMode.InfiniteSnake:
            self.player1._length = -1
            self.player2._length = -1

        elif self.game_mode == GameMode.EatToSurvive:
            self.pickup_radius = 9
            self.player1._length = 75
            self.player2._length = 75
            for i in range(10):
                self.spawn_pickup()

        elif self.game_mode == GameMode.EatToGrow:
            for i in range(4):
                self.spawn_pickup()
    
    def act(self):
        """
        Performs bundle of managing actions for a game depending on its state
        """
        if self.game_state == GameState.Menu:
            self._menu_state_actions()

        elif self.game_state == GameState.Running:
            self._running_state_actions() 

        elif self.game_state == GameState.Finished:
            self._finished_state_actions()   

    def _menu_state_actions(self):
        pass

    def _running_state_actions(self):
        #handle all collision stuff

        if  self.player1.collided and \
        colors_equal(self.player1.collided_color, self.pickup_color):
            #player1 collided with a pickup
            self.handle_pickup_collision(self.player1)

        if  self.player2.collided and \
        colors_equal(self.player2.collided_color, self.pickup_color):
            #player2 collided with a pickup
           self.handle_pickup_collision(self.player2)

        if self.player1.collided and self.player2.collided:
            self.finish_game()
        elif self.player1.collided and self.player1.collided_color != (100,100,100):
            self.finish_game( winner=self.player2, loser=self.player1 )
        elif self.player2.collided and self.player2.collided_color != (100,100,100):
            self.finish_game( winner=self.player1, loser=self.player2 )

        if self.game_mode == GameMode.EatToSurvive:
            if self.player1.length > 0:
                self.player1._length -= 0.15
            if self.player2.length > 0:
                self.player2._length -= 0.15
            
            if self.player1.length <= 0 and self.player2.length <= 0:
                self.finish_game()
            elif self.player1.length <= 0:
                self.finish_game( winner=self.player2, loser=self.player1 )
            elif self.player2.length <= 0:
                self.finish_game( winner=self.player1, loser=self.player2 )

    def _finished_state_actions(self):
        pass
        #self.ui.show_endgame_menu()
        # if self.winner == None and \
        #     self.player1.length <= 0 and \
        #     self.player2.length <= 0:
        #     self.game_state = GameState.Quit
        # elif self.winner != None and self.loser.length <= 0:
        #     self.game_state = GameState.Quit
          
    def find_pickup(self, collision_position):
        """
        Look through the list of pickups to fint the one player collided with 
        """
        closest_pickup = self.pickups[0]
        current_dist = closest_pickup.distance_to(collision_position)
        for p in self.pickups:
            if p.distance_to(collision_position) <= current_dist:
                closest_pickup = p
                current_dist = p.distance_to(collision_position)
        return closest_pickup

    def handle_pickup_collision(self, player):
        """
        find collided pickup and increase player's score
        """
        p = self.find_pickup(player.collision_position)
        self.display.erase_enqueue(p, self.pickup_radius)
        self.pickups.remove(p)
        if self.game_mode == GameMode.EatToSurvive:
            player._length += 25
            player.speed += 0.1
        elif self.game_mode == GameMode.EatToGrow:
            player._length += 25
            player.speed += 0.1
        player.collided = False 
        if isinstance(player, Player1):
            self.ui.increment_p1_score()
        elif isinstance(player, Player2):
            self.ui.increment_p2_score()
        self.spawn_pickup()

    def spawn_pickup(self):
        """
        Spawn picku on random location
        """
        x = random.randrange(self.pickup_radius , self.display.play_area_width - self.pickup_radius)
        y = random.randrange(self.pickup_radius, self.display.play_area_height - self.pickup_radius)

        while self.display.detect_collision((x, y), self.pickup_radius*5, self.pickup_color)[0]:
            x = random.randrange(self.pickup_radius , self.display.play_area_width - self.pickup_radius)
            y = random.randrange(self.pickup_radius, self.display.play_area_height - self.pickup_radius)
        
        self.pickups.append(Point(x, y))
        self.display.draw_point((x, y), self.pickup_color, self.pickup_radius)

    def control_players(self, pressed_keys):
        self.player1.steer(pressed_keys)
        self.player2.steer(pressed_keys)

    def control_players_arcade(self, joysticks):
        self.player2.joy_steer(joysticks[0].get_axis(0), joysticks[0].get_axis(1))
        self.player1.joy_steer(joysticks[1].get_axis(0), joysticks[1].get_axis(1))

    def draw_players(self):
        self.player1.draw()
        self.player2.draw()

    def move_players(self):
        self.player1.move()
        self.player2.move()

    def finish_game(self, winner = None, loser = None):
        """
        display endgame screen and show who won
        """
        self.winner = winner
        self.ui.winner = winner
        self.loser = loser
        self.ui.loser = loser
        self.game_state = GameState.Finished
        self.ui.state = UIState.Visible
        self.ui.show_endgame_menu()

    def set_players_speed(self, speed):
        self.player1.speed = speed
        self.player2.speed = speed
        



        
