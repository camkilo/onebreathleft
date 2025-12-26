"""
Enemy Manager
Handles abstract enemies that adapt to player behavior
"""

import random
import math

class Enemy:
    """Abstract enemy entity"""
    
    def __init__(self, x, y, enemy_type):
        """Initialize enemy"""
        self.x = x
        self.y = y
        self.type = enemy_type  # shadow, whisper, presence
        self.active = True
        self.speed = 50
        
        # Behavior
        self.aggression = 0.5
        self.detection_radius = 150
        self.attack_radius = 30
        
        # State
        self.target_x = x
        self.target_y = y
        self.alert = False
        
    def update(self, dt, player, trust_level):
        """Update enemy behavior"""
        if not self.active:
            return
            
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Detection based on trust level (low trust = easier detection)
        detection_mod = 1.5 - trust_level
        effective_radius = self.detection_radius * detection_mod
        
        # Check if player is detected
        if distance < effective_radius:
            self.alert = True
            # Move towards player
            if distance > self.attack_radius:
                # Normalize direction
                if distance > 0:
                    dx /= distance
                    dy /= distance
                    
                self.x += dx * self.speed * dt * self.aggression
                self.y += dy * self.speed * dt * self.aggression
        else:
            self.alert = False
            # Wander
            self.x += random.uniform(-20, 20) * dt
            self.y += random.uniform(-20, 20) * dt
            
        # Attack if close enough
        if distance < self.attack_radius and self.alert:
            return True  # Signal that enemy attacked
            
        return False

class EnemyManager:
    """Manages all enemies in the game"""
    
    def __init__(self):
        """Initialize enemy manager"""
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 20  # seconds
        self.difficulty_modifier = 1.0
        self.max_enemies = 5
        
    def update(self, dt, player, trust_level):
        """Update all enemies"""
        self.spawn_timer += dt
        
        # Spawn new enemies periodically
        if self.spawn_timer >= self.spawn_interval and len(self.enemies) < self.max_enemies:
            self._spawn_enemy(player, trust_level)
            self.spawn_timer = 0
            
        # Update existing enemies
        enemies_to_remove = []
        for enemy in self.enemies:
            attacked = enemy.update(dt, player, trust_level)
            if attacked:
                # Enemy hit player
                damage = 10 * self.difficulty_modifier
                player.take_damage(damage)
                player.increase_fear(15)
                
            # Remove inactive enemies
            if not enemy.active:
                enemies_to_remove.append(enemy)
                
        # Remove inactive enemies
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)
            
    def _spawn_enemy(self, player, trust_level):
        """Spawn a new enemy"""
        # Spawn away from player
        angle = random.uniform(0, 2 * math.pi)
        distance = 300 + random.uniform(0, 200)
        
        x = player.x + math.cos(angle) * distance
        y = player.y + math.sin(angle) * distance
        
        # Enemy type based on trust level
        if trust_level > 0.6:
            enemy_type = "shadow"  # Less threatening
        elif trust_level < 0.4:
            enemy_type = "presence"  # More threatening
        else:
            enemy_type = random.choice(["shadow", "whisper", "presence"])
            
        enemy = Enemy(x, y, enemy_type)
        
        # Adjust enemy difficulty
        enemy.aggression *= self.difficulty_modifier
        enemy.speed *= self.difficulty_modifier
        
        self.enemies.append(enemy)
        
    def clear_enemies(self):
        """Remove all enemies"""
        self.enemies.clear()
