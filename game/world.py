"""
World class
Handles the foggy, minimal world environment with soft boundaries
"""

import random
import math

class World:
    """World environment with fog and dynamic changes"""
    
    def __init__(self):
        """Initialize world"""
        self.fog_density = 0.7  # 0 = clear, 1 = dense fog
        self.ambient_darkness = 0.6  # 0 = bright, 1 = dark
        
        # World state affected by trust
        self.hostility = 0.5  # How hostile the environment is
        
        # Soft boundaries (no hard walls)
        self.world_center_x = 400
        self.world_center_y = 300
        self.soft_boundary_radius = 600  # Distance where effects start
        self.max_boundary_radius = 800  # Absolute limit
        
        # Exploration zones
        self.zones = []
        self._generate_zones()
        
    def _generate_zones(self):
        """Generate exploration zones"""
        # Create abstract zones for exploration
        for i in range(15):
            angle = (i / 15) * 2 * math.pi
            distance = 300 + random.randint(-50, 50)
            x = 400 + math.cos(angle) * distance
            y = 300 + math.sin(angle) * distance
            
            zone = {
                "x": x,
                "y": y,
                "radius": 50,
                "explored": False,
                "type": random.choice(["safe", "dangerous", "mysterious"])
            }
            self.zones.append(zone)
    
    def get_boundary_effect(self, player_x, player_y):
        """
        Calculate boundary effects based on distance from center.
        Returns (control_lag, zoom_factor, sound_muffle)
        """
        dx = player_x - self.world_center_x
        dy = player_y - self.world_center_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.soft_boundary_radius:
            # No effect inside safe zone
            return 0.0, 1.0, 0.0
        elif distance < self.max_boundary_radius:
            # Gradual effects in soft boundary zone
            t = (distance - self.soft_boundary_radius) / (self.max_boundary_radius - self.soft_boundary_radius)
            control_lag = t * 0.7  # 0 to 0.7 lag multiplier
            zoom_factor = 1.0 - t * 0.15  # Slight zoom in (1.0 to 0.85)
            sound_muffle = t  # 0 to 1 muffle effect
            return control_lag, zoom_factor, sound_muffle
        else:
            # At or beyond max boundary - strong effects
            return 0.8, 0.8, 1.0
            
    def push_player_from_boundary(self, player_x, player_y, dt):
        """
        Gently push player back if they're too far from center.
        Returns (push_x, push_y) force to apply.
        """
        dx = player_x - self.world_center_x
        dy = player_y - self.world_center_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.soft_boundary_radius:
            # Calculate push force towards center
            t = (distance - self.soft_boundary_radius) / (self.max_boundary_radius - self.soft_boundary_radius)
            t = min(1.0, t)
            
            # Normalize direction towards center
            push_strength = t * 50 * dt  # Stronger push as they get further
            if distance > 0:
                push_x = -(dx / distance) * push_strength
                push_y = -(dy / distance) * push_strength
                return push_x, push_y
        
        return 0, 0
            
    def update(self, dt, trust_level, reality_system=None):
        """Update world state based on trust level and reality stability"""
        # High trust = clearer world, less hostile
        # Low trust = foggier, more hostile
        
        target_fog = 0.9 - (trust_level * 0.4)  # 0.5-0.9 range
        target_darkness = 0.8 - (trust_level * 0.4)  # 0.4-0.8 range
        target_hostility = 0.8 - (trust_level * 0.6)  # 0.2-0.8 range
        
        # Apply reality system fog modifier if available
        if reality_system:
            target_fog = reality_system.apply_fog_density_modifier(target_fog)
        
        # Smoothly transition
        self.fog_density += (target_fog - self.fog_density) * dt * 0.5
        self.ambient_darkness += (target_darkness - self.ambient_darkness) * dt * 0.5
        self.hostility += (target_hostility - self.hostility) * dt * 0.3
        
    def check_zone_exploration(self, player_x, player_y):
        """Check if player has explored a new zone"""
        for zone in self.zones:
            if not zone["explored"]:
                dx = player_x - zone["x"]
                dy = player_y - zone["y"]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < zone["radius"]:
                    zone["explored"] = True
                    return zone["type"]
        return None
        
    def get_visibility_radius(self, fear_level):
        """Get how far player can see based on fog and fear"""
        base_radius = 150
        fog_modifier = 1.0 - (self.fog_density * 0.7)
        fear_modifier = 1.0 - (fear_level / 100 * 0.3)
        
        return base_radius * fog_modifier * fear_modifier
