"""
Player class
Handles player state, movement, and survival mechanics
"""

import math

class Player:
    """Player entity with survival mechanics"""
    
    def __init__(self, x, y):
        """Initialize player"""
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 150  # pixels per second
        
        # Survival stats
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.fear = 0  # 0-100, affects visibility and stamina
        
        # Exploration tracking
        self.zones_explored = 0
        self.distance_traveled = 0
        
        # State
        self.is_running = False
        
    def update(self, dt):
        """Update player state"""
        # Apply movement
        prev_x, prev_y = self.x, self.y
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Track distance
        dx = self.x - prev_x
        dy = self.y - prev_y
        self.distance_traveled += math.sqrt(dx*dx + dy*dy)
        
        # Regenerate stamina when not running
        if not self.is_running:
            self.stamina = min(self.max_stamina, self.stamina + 10 * dt)
        else:
            self.stamina = max(0, self.stamina - 15 * dt)
            
        # Fear slowly decreases over time
        self.fear = max(0, self.fear - 5 * dt)
        
        # Health slowly regenerates
        if self.health < self.max_health and self.fear < 30:
            self.health = min(self.max_health, self.health + 2 * dt)
            
    def move(self, direction_x, direction_y):
        """Set movement direction"""
        # Normalize direction
        magnitude = math.sqrt(direction_x**2 + direction_y**2)
        if magnitude > 0:
            direction_x /= magnitude
            direction_y /= magnitude
            
        # Apply speed modifiers
        speed = self.speed
        if self.is_running and self.stamina > 0:
            speed *= 1.5
        if self.fear > 50:
            speed *= 0.8
            
        self.velocity_x = direction_x * speed
        self.velocity_y = direction_y * speed
        
    def stop(self):
        """Stop moving"""
        self.velocity_x = 0
        self.velocity_y = 0
        
    def take_damage(self, amount):
        """Take damage"""
        self.health = max(0, self.health - amount)
        self.fear = min(100, self.fear + amount * 0.5)
        
    def increase_fear(self, amount):
        """Increase fear level"""
        self.fear = min(100, self.fear + amount)
        
    def decrease_fear(self, amount):
        """Decrease fear level"""
        self.fear = max(0, self.fear - amount)
