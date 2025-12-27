"""
Objectives System
Micro-objectives that compete with survival.
Pure survival gets stale - give players competing goals.
"""

import random
import math


# Objective type constants
OBJECTIVE_TYPE_STABILIZE = 'stabilize'
OBJECTIVE_TYPE_SIGNAL = 'signal'
OBJECTIVE_TYPE_PROTECT = 'protect'
OBJECTIVE_TYPE_ABANDON = 'abandon'


class Objective:
    """Base class for game objectives"""
    
    def __init__(self, x, y, duration):
        self.x = x
        self.y = y
        self.duration = duration
        self.time_remaining = duration
        self.active = True
        self.completed = False
        self.failed = False
        self.interaction_radius = 80
    
    def update(self, dt, player):
        """Update objective state"""
        if not self.active:
            return
        
        self.time_remaining -= dt
        
        if self.time_remaining <= 0:
            self.failed = True
            self.active = False
    
    def check_completion(self, player):
        """Check if objective is completed"""
        pass
    
    def get_distance_to_player(self, player):
        """Get distance from objective to player"""
        dx = player.x - self.x
        dy = player.y - self.y
        return math.sqrt(dx*dx + dy*dy)


class StabilizeZone(Objective):
    """
    Objective: Stabilize a collapsing zone
    Player must stay within zone for a duration
    """
    
    def __init__(self, x, y):
        super().__init__(x, y, duration=30.0)
        self.stabilization_progress = 0.0
        self.required_progress = 100.0
        self.stabilization_rate = 10.0  # per second when inside
        self.decay_rate = 5.0  # per second when outside
        self.zone_radius = 100
        
    def update(self, dt, player):
        """Update stabilization progress"""
        super().update(dt, player)
        
        if not self.active:
            return
        
        distance = self.get_distance_to_player(player)
        
        if distance < self.zone_radius:
            # Player is inside - stabilize
            self.stabilization_progress += self.stabilization_rate * dt
        else:
            # Player is outside - decay
            self.stabilization_progress = max(0, self.stabilization_progress - self.decay_rate * dt)
        
        # Check completion
        if self.stabilization_progress >= self.required_progress:
            self.completed = True
            self.active = False
    
    def get_progress_ratio(self):
        """Get stabilization progress (0-1)"""
        return self.stabilization_progress / self.required_progress


class ReachSignal(Objective):
    """
    Objective: Reach a fading signal before it disappears
    Simple race against time
    """
    
    def __init__(self, x, y):
        super().__init__(x, y, duration=20.0)
        self.signal_strength = 1.0
        
    def update(self, dt, player):
        """Update signal strength and check reach"""
        super().update(dt, player)
        
        if not self.active:
            return
        
        # Signal fades over time
        self.signal_strength = self.time_remaining / self.duration
        
        # Check if player reached signal
        distance = self.get_distance_to_player(player)
        if distance < self.interaction_radius:
            self.completed = True
            self.active = False


class ProtectFollower(Objective):
    """
    Objective: Protect a fragile entity that follows player
    If it takes damage, objective fails
    """
    
    def __init__(self, x, y):
        super().__init__(x, y, duration=45.0)
        self.follower_health = 100
        self.follower_speed = 80
        self.follow_distance = 120
        
    def update(self, dt, player):
        """Update follower position and check health"""
        super().update(dt, player)
        
        if not self.active:
            return
        
        # Follower moves toward player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.follow_distance:
            # Move toward player
            if distance > 0:
                dx /= distance
                dy /= distance
            
            self.x += dx * self.follower_speed * dt
            self.y += dy * self.follower_speed * dt
        
        # Check if follower is dead
        if self.follower_health <= 0:
            self.failed = True
            self.active = False
        
        # Complete after duration if still alive
        if self.time_remaining <= 0 and self.follower_health > 0:
            self.completed = True
            self.active = False
            self.failed = False
    
    def take_damage(self, amount):
        """Follower takes damage"""
        self.follower_health = max(0, self.follower_health - amount)


class ChooseAbandon(Objective):
    """
    Objective: Choose which area to abandon (binary choice)
    Two zones appear, player must choose one to sacrifice
    """
    
    def __init__(self, x1, y1, x2, y2):
        # Use midpoint for objective location
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        super().__init__(mid_x, mid_y, duration=25.0)
        
        self.zone1_x = x1
        self.zone1_y = y1
        self.zone2_x = x2
        self.zone2_y = y2
        self.zone_radius = 80
        
        self.choice_made = False
        self.abandoned_zone = None  # 1 or 2
        
    def update(self, dt, player):
        """Update choice state"""
        super().update(dt, player)
        
        if not self.active or self.choice_made:
            return
        
        # Check if player is in either zone
        dx1 = player.x - self.zone1_x
        dy1 = player.y - self.zone1_y
        dist1 = math.sqrt(dx1*dx1 + dy1*dy1)
        
        dx2 = player.x - self.zone2_x
        dy2 = player.y - self.zone2_y
        dist2 = math.sqrt(dx2*dx2 + dy2*dy2)
        
        if dist1 < self.zone_radius:
            # Chose zone 1, abandon zone 2
            self.abandoned_zone = 2
            self.choice_made = True
            self.completed = True
            self.active = False
        elif dist2 < self.zone_radius:
            # Chose zone 2, abandon zone 1
            self.abandoned_zone = 1
            self.choice_made = True
            self.completed = True
            self.active = False


class ObjectivesSystem:
    """
    Manages active objectives and spawning new ones.
    """
    
    def __init__(self):
        self.active_objectives = []
        self.completed_objectives = []
        self.failed_objectives = []
        
        self.spawn_timer = 0
        self.spawn_interval = 40.0  # Spawn objective every ~40 seconds
        
        self.objectives_enabled = True
        
    def update(self, dt, player, threat_manager, game_time):
        """Update all objectives"""
        if not self.objectives_enabled:
            return
        
        # Update spawn timer
        self.spawn_timer += dt
        
        # Spawn new objective periodically
        if self.spawn_timer >= self.spawn_interval and len(self.active_objectives) == 0:
            # Only start objectives after 30 seconds
            if game_time > 30:
                self._spawn_random_objective(player)
                self.spawn_timer = 0
        
        # Update active objectives
        objectives_to_remove = []
        for objective in self.active_objectives:
            objective.update(dt, player)
            
            # Check for follower damage from threats
            if isinstance(objective, ProtectFollower):
                self._check_follower_threats(objective, threat_manager)
            
            if not objective.active:
                if objective.completed:
                    self.completed_objectives.append(objective)
                elif objective.failed:
                    self.failed_objectives.append(objective)
                objectives_to_remove.append(objective)
        
        for obj in objectives_to_remove:
            self.active_objectives.remove(obj)
    
    def _spawn_random_objective(self, player):
        """Spawn a random objective near player"""
        # Spawn away from player
        angle = random.uniform(0, 2 * math.pi)
        distance = 250 + random.uniform(0, 200)
        
        x = player.x + math.cos(angle) * distance
        y = player.y + math.sin(angle) * distance
        
        # Choose objective type
        objective_type = random.choice([
            OBJECTIVE_TYPE_STABILIZE,
            OBJECTIVE_TYPE_SIGNAL,
            OBJECTIVE_TYPE_PROTECT,
            OBJECTIVE_TYPE_ABANDON
        ])
        
        if objective_type == OBJECTIVE_TYPE_STABILIZE:
            obj = StabilizeZone(x, y)
        elif objective_type == OBJECTIVE_TYPE_SIGNAL:
            obj = ReachSignal(x, y)
        elif objective_type == OBJECTIVE_TYPE_PROTECT:
            obj = ProtectFollower(x, y)
        elif objective_type == OBJECTIVE_TYPE_ABANDON:
            # Need two positions
            angle2 = angle + math.pi / 2
            x2 = player.x + math.cos(angle2) * distance
            y2 = player.y + math.sin(angle2) * distance
            obj = ChooseAbandon(x, y, x2, y2)
        
        self.active_objectives.append(obj)
    
    def _check_follower_threats(self, follower_obj, threat_manager):
        """Check if any threats damage the follower"""
        # Check hunters
        for hunter in threat_manager.hunters:
            dx = follower_obj.x - hunter.x
            dy = follower_obj.y - hunter.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < hunter.attack_radius:
                follower_obj.take_damage(5)
        
        # Corruption fields also damage follower
        for field in threat_manager.corruption_fields:
            dx = follower_obj.x - field.x
            dy = follower_obj.y - field.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < field.radius:
                follower_obj.take_damage(2)
    
    def get_active_objectives_info(self):
        """Get info about active objectives for display"""
        info = []
        for obj in self.active_objectives:
            obj_info = {
                'type': obj.__class__.__name__,
                'x': obj.x,
                'y': obj.y,
                'time_remaining': obj.time_remaining,
                'duration': obj.duration
            }
            
            if isinstance(obj, StabilizeZone):
                obj_info['progress'] = obj.get_progress_ratio()
            elif isinstance(obj, ReachSignal):
                obj_info['signal_strength'] = obj.signal_strength
            elif isinstance(obj, ProtectFollower):
                obj_info['follower_health'] = obj.follower_health
                obj_info['follower_x'] = obj.x
                obj_info['follower_y'] = obj.y
            elif isinstance(obj, ChooseAbandon):
                obj_info['zone1_x'] = obj.zone1_x
                obj_info['zone1_y'] = obj.zone1_y
                obj_info['zone2_x'] = obj.zone2_x
                obj_info['zone2_y'] = obj.zone2_y
                obj_info['choice_made'] = obj.choice_made
            
            info.append(obj_info)
        
        return info
    
    def get_objectives_count(self):
        """Get count of completed/failed objectives"""
        return {
            'active': len(self.active_objectives),
            'completed': len(self.completed_objectives),
            'failed': len(self.failed_objectives)
        }
