"""
Player class
Handles player state, movement, and survival mechanics with nonlinear interpolation
"""

import math

def ease_out_cubic(t):
    """Cubic easing out for smooth deceleration"""
    return 1 - pow(1 - t, 3)

def ease_in_out_quad(t):
    """Quadratic easing in/out for natural movement"""
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

def panic_overshoot(t, panic_level):
    """Add slight overshoot when panicked"""
    if panic_level > 0.5:
        return t + math.sin(t * math.pi) * (panic_level - 0.5) * 0.2
    return t

class Player:
    """Player entity with survival mechanics and nonlinear movement"""
    
    def __init__(self, x, y):
        """Initialize player"""
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.target_velocity_x = 0
        self.target_velocity_y = 0
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
        
        # Movement state for nonlinear interpolation
        self.movement_lerp_t = 0
        self.last_direction_change_time = 0
        
    def update(self, dt, time_dilation=1.0):
        """Update player state with optional time dilation"""
        # Apply time dilation (selective time skew)
        effective_dt = dt * time_dilation
        
        # Nonlinear velocity interpolation based on stress
        panic_level = self.fear / 100.0
        
        # Interpolate towards target velocity with easing
        if abs(self.target_velocity_x - self.velocity_x) > 1 or abs(self.target_velocity_y - self.velocity_y) > 1:
            # Active movement change
            self.movement_lerp_t = min(1.0, self.movement_lerp_t + effective_dt * 8)
            
            # Apply panic overshoot when stressed
            t = panic_overshoot(ease_in_out_quad(self.movement_lerp_t), panic_level)
            
            self.velocity_x += (self.target_velocity_x - self.velocity_x) * t * 0.5
            self.velocity_y += (self.target_velocity_y - self.velocity_y) * t * 0.5
        else:
            # Reset lerp when stable
            self.movement_lerp_t = 0
        
        # Apply movement
        prev_x, prev_y = self.x, self.y
        self.x += self.velocity_x * effective_dt
        self.y += self.velocity_y * effective_dt
        
        # Track distance
        dx = self.x - prev_x
        dy = self.y - prev_y
        self.distance_traveled += math.sqrt(dx*dx + dy*dy)
        
        # Regenerate stamina when not running
        if not self.is_running:
            self.stamina = min(self.max_stamina, self.stamina + 10 * effective_dt)
        else:
            self.stamina = max(0, self.stamina - 15 * effective_dt)
            
        # Fear slowly decreases over time
        self.fear = max(0, self.fear - 5 * effective_dt)
        
        # Health slowly regenerates
        if self.health < self.max_health and self.fear < 30:
            self.health = min(self.max_health, self.health + 2 * effective_dt)
            
    def move(self, direction_x, direction_y):
        """Set movement direction with nonlinear acceleration"""
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
        
        # Set target velocity (will be interpolated to in update)
        self.target_velocity_x = direction_x * speed
        self.target_velocity_y = direction_y * speed
        
    def stop(self):
        """Stop moving"""
        self.target_velocity_x = 0
        self.target_velocity_y = 0
        
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
