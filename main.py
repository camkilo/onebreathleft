#!/usr/bin/env python3
"""
One Breath Left - A Psychological Survival Game
The player is guided by an AI companion that is actually a recording from their last playthrough.
"""

import pygame
import sys
import os
from game.game_state import GameState
from game.renderer import Renderer
from game.input_handler import InputHandler

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

def main():
    """Main game loop"""
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("One Breath Left")
    
    # Create game clock
    clock = pygame.time.Clock()
    
    # Initialize game systems
    game_state = GameState()
    renderer = Renderer(screen, WINDOW_WIDTH, WINDOW_HEIGHT)
    input_handler = InputHandler()
    
    # Main game loop
    running = True
    while running:
        # Get delta time
        dt = clock.tick(FPS) / 1000.0  # Convert to seconds
        
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            input_handler.handle_event(event)
        
        # Update game state
        input_handler.update(game_state, dt)
        game_state.update(dt)
        
        # Check if game should end
        if game_state.should_quit:
            running = False
        
        # Render
        renderer.render(game_state)
        pygame.display.flip()
    
    # Save playthrough on exit
    game_state.save_playthrough()
    
    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
