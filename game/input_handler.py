"""
Input Handler
Processes player input and controls with soft boundary effects
"""

import pygame
import math

class InputHandler:
    """Handles keyboard and mouse input with boundary awareness"""
    
    def __init__(self):
        """Initialize input handler"""
        self.keys_pressed = set()
        self.accept_pressed = False  # For accepting/rejecting advice
        self.reject_pressed = False
        
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            
            # Advice response keys
            if event.key == pygame.K_y:
                self.accept_pressed = True
            elif event.key == pygame.K_n:
                self.reject_pressed = True
                
        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed.remove(event.key)
                
    def update(self, game_state, dt):
        """Update game state based on input with soft boundary effects"""
        player = game_state.player
        world = game_state.world
        
        # Movement
        direction_x = 0
        direction_y = 0
        
        if pygame.K_w in self.keys_pressed or pygame.K_UP in self.keys_pressed:
            direction_y -= 1
        if pygame.K_s in self.keys_pressed or pygame.K_DOWN in self.keys_pressed:
            direction_y += 1
        if pygame.K_a in self.keys_pressed or pygame.K_LEFT in self.keys_pressed:
            direction_x -= 1
        if pygame.K_d in self.keys_pressed or pygame.K_RIGHT in self.keys_pressed:
            direction_x += 1
            
        # Running
        player.is_running = pygame.K_LSHIFT in self.keys_pressed or pygame.K_RSHIFT in self.keys_pressed
        
        # Get boundary effects
        control_lag, zoom_factor, sound_muffle = world.get_boundary_effect(player.x, player.y)
        
        # Apply movement with control lag at boundaries
        if direction_x != 0 or direction_y != 0:
            # Reduce responsiveness near boundaries
            lag_factor = 1.0 - control_lag
            player.move(direction_x * lag_factor, direction_y * lag_factor)
            
            game_state.record_action("move", {
                "x": player.x,
                "y": player.y,
                "running": player.is_running
            })
        else:
            player.stop()
        
        # Apply gentle push back from boundaries
        push_x, push_y = world.push_player_from_boundary(player.x, player.y, dt)
        player.x += push_x
        player.y += push_y
            
        # Check for zone exploration
        zone_type = game_state.world.check_zone_exploration(player.x, player.y)
        if zone_type:
            player.zones_explored += 1
            game_state.record_action("zone_explored", {"type": zone_type})
            
            # Affect player based on zone type
            if zone_type == "safe":
                player.decrease_fear(20)
            elif zone_type == "dangerous":
                player.increase_fear(30)
                
        # Handle advice responses
        if self.accept_pressed:
            game_state.follow_advice()
            self.accept_pressed = False
            
        if self.reject_pressed:
            game_state.ignore_advice()
            self.reject_pressed = False
