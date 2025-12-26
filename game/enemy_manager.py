"""
Enemy Manager
Handles abstract enemies that adapt to player behavior.
Enemies now react to hesitation, movement speed, and AI speech.
"""

import random
import math

class Enemy:
    """Abstract enemy entity with perception-based behavior"""
    
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
        
        # Perception tracking
        self.player_last_pos = (x, y)
        self.player_still_timer = 0.0  # How long player has been still
        self.attracted_to_stillness = False
        self.attracted_to_speech = False
        self.speech_attraction_timer = 0.0
        
    def update(self, dt, player, trust_level, behavior_state=None, ai_speaking=False):
        """
        Update enemy behavior with perception.
        
        Args:
            dt: Delta time
            player: Player object
            trust_level: Current trust level
            behavior_state: BehaviorState for hesitation tracking
            ai_speaking: Whether AI is currently giving advice
        """
        if not self.active:
            return False
            
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Detect player movement/stillness
        player_pos = (player.x, player.y)
        movement = math.sqrt(
            (player_pos[0] - self.player_last_pos[0])**2 +
            (player_pos[1] - self.player_last_pos[1])**2
        )
        
        # Track if player is standing still
        if movement < 5 * dt:  # Very little movement
            self.player_still_timer += dt
        else:
            self.player_still_timer = 0.0
            
        self.player_last_pos = player_pos
        
        # React to player stillness (standing still attracts attention)
        if self.player_still_timer > 2.0:
            self.attracted_to_stillness = True
            # Increase detection radius when player is still
            stillness_bonus = min(1.5, 1.0 + self.player_still_timer * 0.1)
        else:
            self.attracted_to_stillness = False
            stillness_bonus = 1.0
        
        # React to AI speech (listening feels risky)
        if ai_speaking:
            self.attracted_to_speech = True
            self.speech_attraction_timer = 3.0  # Stay attracted for 3 seconds
        
        if self.speech_attraction_timer > 0:
            self.speech_attraction_timer -= dt
            speech_bonus = 1.3  # Significantly easier to detect while listening
        else:
            self.attracted_to_speech = False
            speech_bonus = 1.0
        
        # React to player hesitation
        hesitation_bonus = 1.0
        if behavior_state:
            # High hesitation = easier to detect (indecision attracts attention)
            hesitation_bonus = 1.0 + behavior_state.hesitation_score * 0.3
        
        # Detection based on trust level (low trust = easier detection)
        detection_mod = 1.5 - trust_level
        
        # Combine all perception factors
        effective_radius = (
            self.detection_radius * 
            detection_mod * 
            stillness_bonus * 
            speech_bonus * 
            hesitation_bonus
        )
        
        # Check if player is detected
        if distance < effective_radius:
            self.alert = True
            # Move towards player
            if distance > self.attack_radius:
                # Normalize direction
                if distance > 0:
                    dx /= distance
                    dy /= distance
                
                # Speed boost when attracted to stillness or speech
                speed_mod = 1.0
                if self.attracted_to_stillness:
                    speed_mod = 1.2
                if self.attracted_to_speech:
                    speed_mod = 1.3
                    
                self.x += dx * self.speed * dt * self.aggression * speed_mod
                self.y += dy * self.speed * dt * self.aggression * speed_mod
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
        
    def update(self, dt, player, trust_level, behavior_state=None, ai_speaking=False):
        """
        Update all enemies with perception-based behavior.
        
        Args:
            dt: Delta time
            player: Player object
            trust_level: Current trust level
            behavior_state: BehaviorState for hesitation tracking
            ai_speaking: Whether AI is currently giving advice
        """
        self.spawn_timer += dt
        
        # Spawn new enemies periodically
        if self.spawn_timer >= self.spawn_interval and len(self.enemies) < self.max_enemies:
            self._spawn_enemy(player, trust_level)
            self.spawn_timer = 0
            
        # Update existing enemies
        enemies_to_remove = []
        for enemy in self.enemies:
            attacked = enemy.update(dt, player, trust_level, behavior_state, ai_speaking)
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
