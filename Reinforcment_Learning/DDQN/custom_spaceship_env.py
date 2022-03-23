# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 23:09:13 2021

@author: bergergu
"""
import numpy as np
import gym
from gym import spaces
import cv2 
import random
from elements import Spaceship, Fuel, Alien, Missile, Magazine, Explosion
import time 

font = cv2.FONT_HERSHEY_COMPLEX_SMALL 


class CustomSpaceshipEnv(gym.Env):
    
    def __init__(self):
        super(CustomSpaceshipEnv, self).__init__()  
        
        # Define a 2-D observation space
        self.observation_shape = (300, 400, 3)
        self.observation_space = spaces.Box(low = np.zeros(self.observation_shape), 
                                            high = np.ones(self.observation_shape),
                                            dtype = np.float16)
    
        self.max_reward = 0
        self.ep_return = 0
        # Define an action space ranging from 0 to 5
        self.action_space = spaces.Discrete(6,)
        self.hits = 0
        # Create a canvas to render the environment images upon 
        self.canvas = np.ones(self.observation_shape) * 1
        self.life_time = []
        self.life_time.append(0)
        self.average_time = 0
        # Define elements present inside the environment
        self.elements = []
        self.average_life_time = 0
        # Maximum fuel Spaceship can take at once
        self.max_fuel = 1000
        self.episode_num = 0
        # Permissible area of helicper to be 
        self.y_min = int (self.observation_shape[0] * 0.1)
        self.x_min = 0
        self.y_max = int (self.observation_shape[0] * 0.9)
        self.x_max = self.observation_shape[1]
        self.max_magazine = 100
        self.shoot = False
        self.explode = False
        self.tic = 0
        self.toc = 0
        
    def draw_elements_on_canvas(self):
        # Init the canvas 
        self.canvas = np.ones(self.observation_shape) * 1
    
        # Draw the heliopter on canvas
        for elem in self.elements:
            elem_shape = elem.icon.shape
            x,y = elem.x, elem.y
            self.canvas[y : y + elem_shape[1], x:x + elem_shape[0]] = elem.icon
    
        text = 'Max Score: {} Score: {} Fuel: {} Fire: {}'.format(self.max_reward,
               self.ep_return,self.fuel_left, self.magazine_left)
    
        # Put the info on canvas 
        self.canvas = cv2.putText(self.canvas, text, (10,10), font,  
                   0.6, (0,0,0), 1, cv2.LINE_AA)
        
        text = 'Average LT[s]: {}  Hit: {}  Episode: {}'.format(int(self.average_time),
                                                                self.hits, self.episode_num)
    
        # Put the info on canvas 
        self.canvas = cv2.putText(self.canvas, text, (10,25), font,  
                   0.6, (0,0,0), 1, cv2.LINE_AA)

    def reset(self):
        self.tic = time.perf_counter()
        # Reset the fuel consumed
        self.fuel_left = self.max_fuel
        # reset the magazine
        self.magazine_left = self.max_magazine
        # Reset the reward
        #self.max_reward = np.max([self.max_reward,self.ep_return])
        self.ep_return  = 0
        self.hits = 0
        # Number of birds
        self.alien_count = 0
        # Number of Fuel
        self.fuel_count = 0
        # Number of Missiles
        self.missile_count = 0
        # Number of Magazine 
        self.magazine_count = 0
        # Number of blasts
        self.explosion_count = 0
        # to check colissiotn with alion ship
        self.explode = False
        # Game over
        self.gameover_count = 0
        # Determine a place to intialise the Spaceship in
        x = random.randrange(int(self.observation_shape[0] * 0.05), int(self.observation_shape[0] * 0.10))
        y = random.randrange(int(self.observation_shape[1] * 0.15), int(self.observation_shape[1] * 0.20))
        
        # Intialise the Spaceship
        self.spaceship = Spaceship("Spaceship", self.x_max, self.x_min, self.y_max, self.y_min)
        self.spaceship.set_position(x,y)
    
        # Intialise the elements 
        self.elements = [self.spaceship]
    
        # Reset the Canvas 
        self.canvas = np.ones(self.observation_shape) * 1
    
        # Draw elements on the canvas
        #self.draw_elements_on_canvas()
    
        # return the observation
        return self.canvas 
    
    def render(self, mode = "human"):
        assert mode in ["human", "rgb_array"], "Invalid mode, must be either \"human\" or \"rgb_array\""
        if mode == "human":
            #Draw elements on the canvas
            self.draw_elements_on_canvas()
            cv2.imshow("Game", self.canvas)
            cv2.waitKey(10)
        
        elif mode == "rgb_array":
            return self.canvas
    
    def close(self):
        cv2.destroyAllWindows()
        
    def has_collided(self, elem1, elem2):
        x_col = False
        y_col = False
    
        elem1_x, elem1_y = elem1.get_position()
        elem2_x, elem2_y = elem2.get_position()
    
        if 2 * abs(elem1_x - elem2_x) <= (elem1.icon_w + elem2.icon_w):
            x_col = True
    
        if 2 * abs(elem1_y - elem2_y) <= (elem1.icon_h + elem2.icon_h):
            y_col = True
    
        if x_col and y_col:
            return True
    
        return False
                    
    def step(self, action):
        # Flag that marks the termination of an episode
        done = False
        
        # Assert that it is a valid action 
        assert self.action_space.contains(action), "Invalid Action"
    
        # Decrease the fuel counter 
        self.fuel_left -= 1 
        
        # Reward for executing a step.
        reward = 1      
    
        # apply the action to the spaceship
        if action == 0:
            self.spaceship.move(0,5)
        elif action == 1:
            self.spaceship.move(0,-5)
        elif action == 2:
            self.spaceship.move(5,0)
        elif action == 3:
            self.spaceship.move(-5,0)
        elif action == 4:
            self.spaceship.move(0,0)
        elif action == 5:
            self.shoot = True
        
        for elem in self.elements:
            if isinstance(elem, Explosion):
                self.elements.remove(elem)
                
        #  # Game Over 
        # spawned_game_over = GameOver("game_over_{}".format(self.gameover_count), self.x_max, self.x_min, self.y_max, self.y_min)
        # # Compute the x,y co-ordinates of the position from where the game is end
        # game_over_x = 400
        # game_over_y = 400
        # spawned_game_over.set_position(game_over_x,game_over_y)
        # # Append the spawned gameover to the elements currently present in Env. 
        # self.elements.append(spawned_game_over)                            
            
        # Spawn a missile
        if self.shoot and self.magazine_left > 0 :#and random.random() < 0.01:          
            spawned_missile = Missile("missile_{}".format(self.missile_count), self.x_max, 
                                      self.x_min, self.y_max, self.y_min)
            self.missile_count += 1
            self.magazine_left -= 1
            self.shoot = False
            
            # Compute the x,y co-ordinates of the position from where the missile has to be spawned
            missile_x = self.spaceship.get_position()[0] + 35
            missile_y = self.spaceship.get_position()[1] + 15
            spawned_missile.set_position(missile_x,missile_y)
  
            # Append the spawned missile to the elements currently present in Env. 
            self.elements.append(spawned_missile)    
            
        # Spawn an alien at the right edge with prob 0.01
        if random.random() < 0.01:
            
            # Spawn a Alien
            spawned_alien = Alien("alien_{}".format(self.alien_count), self.x_max, self.x_min, self.y_max, self.y_min)
            self.alien_count += 1
    
            # Compute the x,y co-ordinates of the position from where the Alien has to be spawned
            # Horizontally, the position is on the right edge and vertically, the height is randomly 
            # sampled from the set of permissible values
            alien_x = self.x_max 
            alien_y = random.randrange(self.y_min, self.y_max)
            spawned_alien.set_position(alien_x , alien_y)
            
            # Append the spawned alien to the elements currently present in Env. 
            self.elements.append(spawned_alien)    
    
        # Spawn a fuel at the bottom edge with prob 0.01
        if random.random() < 0.01:
            # Spawn a fuel tank
            spawned_fuel = Fuel("fuel_{}".format(self.fuel_count), self.x_max, self.x_min, self.y_max, self.y_min)
            self.fuel_count += 1
            
            # Compute the x,y co-ordinates of the position from where the fuel tank has to be spawned
            # Horizontally, the position is randomly chosen from the list of permissible values and 
            # vertically, the position is on the bottom edge
            fuel_x = random.randrange(self.x_min, self.x_max)
            fuel_y = self.y_max
            spawned_fuel.set_position(fuel_x, fuel_y)
            
            # Append the spawned fuel tank to the elemetns currently present in the Env.
            self.elements.append(spawned_fuel)   
        
        if random.random() < 0.01:
            # Spawn a magazine 
            spawned_magazine = Magazine("magazine_{}".format(self.magazine_count), self.x_max, self.x_min, self.y_max, self.y_min)
            self.magazine_count += 1
            
            # Compute the x,y co-ordinates of the position from where the magazine has to be spawned
            # Horizontally, the position is randomly chosen from the list of permissible values and 
            # vertically, the position is on the bottom edge
            magazine_x = random.randrange(self.x_min, self.x_max)
            magazine_y = self.y_max
            spawned_magazine.set_position(magazine_x, magazine_y)
            
            # Append the spawned fuel tank to the elemetns currently present in the Env.
            self.elements.append(spawned_magazine)  
        
        # For elements in the Ev
        for elem in self.elements:
            if isinstance(elem, Alien):
                # If the Alien has collided.
                if self.has_collided(self.spaceship, elem):
                    spawned_explosion = Explosion("explosion_{}".format(self.explosion_count), 
                                                  self.x_max, self.x_min, self.y_max, self.y_min)
                    self.explosion_count += 1
                    # Compute the x,y co-ordinates of the position from where the blast has to be spawned
                    blast_x = self.spaceship.get_position()[0]
                    blast_y = self.spaceship.get_position()[1]
                    spawned_explosion.set_position(blast_x, blast_y)         
                    # Append the spawned explosion to the elemetns currently present in the Env.
                    self.elements.append(spawned_explosion)                      
                    # Conclude the episode and remove the spaceship from the Env.
                    done = True
                    reward = -50
                    self.explode = True
                    self.elements.remove(self.spaceship)
                    # if alien wasnt removed yet up
                    if(elem in self.elements):
                        self.elements.remove(elem)
                # If the Alien has reached the left edge, remove it from the Env
                elif elem.get_position()[0] <= self.x_min:
                    self.elements.remove(elem)
                else:
                # Move the Alien left by 5 pts.
                    elem.move(-5,0)
    
            if isinstance(elem, Fuel):
                # If the fuel tank has collided with the spaceship.
                if self.has_collided(self.spaceship, elem):
                    # Remove the fuel tank from the env.
                    self.elements.remove(elem)
                    # Fill the fuel tank of the spaceship to full.
                    self.fuel_left += self.max_fuel
                    reward = 10
                elif elem.get_position()[1] <= self.y_min:
                    # If the fuel tank has reached the top, remove it from the Env
                    self.elements.remove(elem)
                else:
                    # If nothing happened move the Tank up by 5 pts.
                    elem.move(0, -5)
                    
            
            if isinstance(elem, Magazine):
                # If the magazine has collided with the spaceship.
                if self.has_collided(self.spaceship, elem):
                    # Remove the magazine from the env.
                    self.elements.remove(elem)
                    # Fill the magazine of the spaceship.
                    self.magazine_left += self.max_magazine
                    reward = 5
                # If the magazine has reached the top, remove it from the Env
                elif elem.get_position()[1] <= self.y_min:
                    self.elements.remove(elem)
                else:
                    # If nothing happened move the magazine up by 5 pts.
                    elem.move(0, -5)
                    
            
            if isinstance(elem, Missile):
                missile = True
                # check If the missile has collided.
                for elem_alien in self.elements:
                    if isinstance(elem_alien, Alien):
                        if self.has_collided(elem, elem_alien):
                            #remove the spaceship from the Env.
                            spawned_explosion = Explosion("explosion_{}".format(self.explosion_count), 
                                                          self.x_max, self.x_min, self.y_max, self.y_min)
                            self.explosion_count += 1
                            # Compute the x,y co-ordinates of the position from where the blast has to be spawned
                            blast_x = elem_alien.get_position()[0]
                            blast_y = elem_alien.get_position()[1]
                            spawned_explosion.set_position(blast_x, blast_y)
                            # Append the spawned explosion to the elemetns currently present in the Env.
                            self.elements.append(spawned_explosion) 
                            reward = 25
                            self.elements.remove(elem_alien)
                            self.elements.remove(elem)
                            missile = False
                            self.hits += 1
                    # If the Missile has reached the right corner, remove it from the Env
                if missile and (elem.get_position()[0] >= self.x_max - 32):
                    self.elements.remove(elem)
                elif missile:
                # Move the missile right by 5 pts.
                    elem.move(5,0)
                

        
        # Draw elements on the canvas
        self.draw_elements_on_canvas()
        
        # If out of fuel, end the episode.
        if self.fuel_left == 0:
            reward = -10
            done = True
            
        if done:
            self.toc = time.perf_counter()
            self.life_time.append(self.toc - self.tic)
            #print("life_time: ",self.life_time)
        self.average_time = np.mean([self.life_time])
        
        # Increment the episodic return
        self.ep_return += reward
        self.max_reward = np.max([self.max_reward,self.ep_return])
        
        return self.canvas, reward, done, []
        
        
        
        