"""
World class
Handles the foggy, minimal world environment
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
            
    def update(self, dt, trust_level):
        """Update world state based on trust level"""
        # High trust = clearer world, less hostile
        # Low trust = foggier, more hostile
        
        target_fog = 0.9 - (trust_level * 0.4)  # 0.5-0.9 range
        target_darkness = 0.8 - (trust_level * 0.4)  # 0.4-0.8 range
        target_hostility = 0.8 - (trust_level * 0.6)  # 0.2-0.8 range
        
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
