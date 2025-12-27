"""
Threat Layer System
Replaces simple enemy spawning with three simultaneous danger layers.
Each layer creates different types of pressure without requiring more enemies.
"""

import random
import math


class Hunter:
    """
    Layer 1 - Active Threat
    Aggressive enemies that are always moving and force repositioning.
    """
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.speed = 80  # Faster than old enemies
        self.detection_radius = 200
        self.attack_radius = 25
        self.always_moving = True
        self.hunt_target_x = x
        self.hunt_target_y = y
        self.hunt_timer = 0
        
    def update(self, dt, player, trust_level):
        """Update hunter behavior - always aggressive"""
        if not self.active:
            return False
            
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Always moving toward player or hunting position
        self.hunt_timer += dt
        
        # Change hunt target periodically
        if self.hunt_timer > 3.0:
            self.hunt_target_x = player.x + random.uniform(-100, 100)
            self.hunt_target_y = player.y + random.uniform(-100, 100)
            self.hunt_timer = 0
        
        # Move toward hunt target
        hunt_dx = self.hunt_target_x - self.x
        hunt_dy = self.hunt_target_y - self.y
        hunt_dist = math.sqrt(hunt_dx*hunt_dx + hunt_dy*hunt_dy)
        
        if hunt_dist > 0:
            hunt_dx /= hunt_dist
            hunt_dy /= hunt_dist
            
        self.x += hunt_dx * self.speed * dt
        self.y += hunt_dy * self.speed * dt
        
        # Attack if close enough
        if distance < self.attack_radius:
            return True
            
        return False


class Watcher:
    """
    Layer 2 - Psychological Threat
    Don't attack but create tension through presence.
    Lock camera / slow movement when on-screen.
    """
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.speed = 20  # Slow drift
        self.observe_radius = 250  # When player is "seen"
        self.is_observing = False
        self.observation_intensity = 0.0  # 0-1, builds over time
        
    def update(self, dt, player, trust_level):
        """Update watcher behavior - creates psychological pressure"""
        if not self.active:
            return None
            
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Check if observing player
        if distance < self.observe_radius:
            self.is_observing = True
            # Build observation intensity over time
            self.observation_intensity = min(1.0, self.observation_intensity + dt * 0.3)
        else:
            self.is_observing = False
            # Decay intensity when not observing
            self.observation_intensity = max(0.0, self.observation_intensity - dt * 0.5)
        
        # Slow drift movement
        self.x += random.uniform(-self.speed, self.speed) * dt
        self.y += random.uniform(-self.speed, self.speed) * dt
        
        # Return observation effect (camera lock, movement slow)
        if self.is_observing:
            return {
                'camera_lock': self.observation_intensity * 0.7,
                'movement_slow': self.observation_intensity * 0.4,
                'tension': self.observation_intensity
            }
        
        return None


class CorruptionField:
    """
    Layer 3 - Environmental Threat
    Expanding zones that drain light or distort controls.
    Move independently of enemies.
    """
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.radius = 80
        self.max_radius = 200
        self.expansion_rate = 15  # pixels per second
        self.drift_speed = 30
        self.drift_direction_x = random.uniform(-1, 1)
        self.drift_direction_y = random.uniform(-1, 1)
        self.field_type = random.choice(['drain_light', 'distort_controls', 'slow_time'])
        
    def update(self, dt, player, trust_level):
        """Update corruption field - environmental hazard"""
        if not self.active:
            return None
            
        # Expand field
        self.radius = min(self.max_radius, self.radius + self.expansion_rate * dt)
        
        # Drift movement
        self.x += self.drift_direction_x * self.drift_speed * dt
        self.y += self.drift_direction_y * self.drift_speed * dt
        
        # Occasionally change direction
        if random.random() < dt * 0.2:
            self.drift_direction_x = random.uniform(-1, 1)
            self.drift_direction_y = random.uniform(-1, 1)
        
        # Check if player is inside field
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.radius:
            # Calculate intensity based on proximity to center
            intensity = 1.0 - (distance / self.radius)
            
            return {
                'type': self.field_type,
                'intensity': intensity,
                'center_x': self.x,
                'center_y': self.y
            }
        
        return None


class ThreatLayerManager:
    """
    Manages all three threat layers simultaneously.
    Ensures constant pressure without overwhelming the player.
    """
    
    def __init__(self):
        self.hunters = []
        self.watchers = []
        self.corruption_fields = []
        
        # Spawn timers for each layer
        self.hunter_spawn_timer = 0
        self.watcher_spawn_timer = 0
        self.field_spawn_timer = 0
        
        # Layer-specific limits
        self.max_hunters = 2  # Few but aggressive
        self.max_watchers = 3  # More numerous but passive
        self.max_fields = 2  # Environmental zones
        
        # Active effects
        self.active_watcher_effects = []
        self.active_field_effects = []
        
    def update(self, dt, player, trust_level, pressure_score):
        """
        Update all threat layers.
        
        Args:
            dt: Delta time
            player: Player object
            trust_level: Current trust level
            pressure_score: Spawning pressure (0-1)
        """
        self.active_watcher_effects = []
        self.active_field_effects = []
        
        # Update hunters
        hunters_to_remove = []
        for hunter in self.hunters:
            attacked = hunter.update(dt, player, trust_level)
            if attacked:
                damage = 12
                player.take_damage(damage)
                player.increase_fear(10)
            if not hunter.active:
                hunters_to_remove.append(hunter)
        
        for hunter in hunters_to_remove:
            self.hunters.remove(hunter)
        
        # Update watchers (psychological pressure)
        watchers_to_remove = []
        for watcher in self.watchers:
            effect = watcher.update(dt, player, trust_level)
            if effect:
                self.active_watcher_effects.append(effect)
            if not watcher.active:
                watchers_to_remove.append(watcher)
        
        for watcher in watchers_to_remove:
            self.watchers.remove(watcher)
        
        # Update corruption fields (environmental hazards)
        fields_to_remove = []
        for field in self.corruption_fields:
            effect = field.update(dt, player, trust_level)
            if effect:
                self.active_field_effects.append(effect)
            if not field.active:
                fields_to_remove.append(field)
        
        for field in fields_to_remove:
            self.corruption_fields.remove(field)
        
        # Spawn based on pressure and layer limits
        self._spawn_threats(dt, player, pressure_score)
        
    def _spawn_threats(self, dt, player, pressure_score):
        """Spawn threats based on pressure score"""
        # Hunters spawn more when pressure is high
        self.hunter_spawn_timer += dt * (0.5 + pressure_score * 0.5)
        if self.hunter_spawn_timer >= 25 and len(self.hunters) < self.max_hunters:
            self._spawn_hunter(player)
            self.hunter_spawn_timer = 0
        
        # Watchers spawn more frequently but are passive
        self.watcher_spawn_timer += dt * (0.3 + pressure_score * 0.7)
        if self.watcher_spawn_timer >= 15 and len(self.watchers) < self.max_watchers:
            self._spawn_watcher(player)
            self.watcher_spawn_timer = 0
        
        # Corruption fields expand the danger without adding entities
        self.field_spawn_timer += dt * (0.4 + pressure_score * 0.6)
        if self.field_spawn_timer >= 30 and len(self.corruption_fields) < self.max_fields:
            self._spawn_corruption_field(player)
            self.field_spawn_timer = 0
    
    def _spawn_hunter(self, player):
        """Spawn a new hunter"""
        angle = random.uniform(0, 2 * math.pi)
        distance = 350 + random.uniform(0, 150)
        
        x = player.x + math.cos(angle) * distance
        y = player.y + math.sin(angle) * distance
        
        hunter = Hunter(x, y)
        self.hunters.append(hunter)
    
    def _spawn_watcher(self, player):
        """Spawn a new watcher"""
        angle = random.uniform(0, 2 * math.pi)
        distance = 300 + random.uniform(0, 200)
        
        x = player.x + math.cos(angle) * distance
        y = player.y + math.sin(angle) * distance
        
        watcher = Watcher(x, y)
        self.watchers.append(watcher)
    
    def _spawn_corruption_field(self, player):
        """Spawn a new corruption field"""
        angle = random.uniform(0, 2 * math.pi)
        distance = 250 + random.uniform(0, 200)
        
        x = player.x + math.cos(angle) * distance
        y = player.y + math.sin(angle) * distance
        
        field = CorruptionField(x, y)
        self.corruption_fields.append(field)
    
    def get_total_threat_count(self):
        """Get total number of active threats"""
        return len(self.hunters) + len(self.watchers) + len(self.corruption_fields)
    
    def get_watcher_effects(self):
        """Get accumulated watcher effects"""
        if not self.active_watcher_effects:
            return None
        
        # Combine all watcher effects
        total_camera_lock = 0
        total_movement_slow = 0
        total_tension = 0
        
        for effect in self.active_watcher_effects:
            total_camera_lock += effect['camera_lock']
            total_movement_slow += effect['movement_slow']
            total_tension += effect['tension']
        
        # Cap at 1.0
        return {
            'camera_lock': min(1.0, total_camera_lock),
            'movement_slow': min(1.0, total_movement_slow),
            'tension': min(1.0, total_tension)
        }
    
    def get_field_effects(self):
        """Get active corruption field effects"""
        return self.active_field_effects if self.active_field_effects else None
    
    def clear_all_threats(self):
        """Remove all threats"""
        self.hunters.clear()
        self.watchers.clear()
        self.corruption_fields.clear()
