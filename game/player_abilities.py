"""
Player Abilities System
Three risk-reward actions that give player agency:
- Focus: Stop, reveal threats, shrink light
- Burn: Clear enemies, increase difficulty
- Break: Ignore AI, cause reality glitch
"""

import random


class PlayerAbilities:
    """
    Manages player's special abilities.
    Each ability has a cost and cooldown.
    """
    
    def __init__(self):
        # Focus ability
        self.focus_cooldown = 0
        self.focus_max_cooldown = 15.0  # seconds
        self.focus_duration = 3.0
        self.focus_active = False
        self.focus_timer = 0
        self.focus_light_penalty = 0  # Accumulated light radius reduction
        
        # Burn ability
        self.burn_cooldown = 0
        self.burn_max_cooldown = 30.0
        self.burn_energy = 0  # Stored energy (0-100)
        self.burn_energy_rate = 5.0  # Energy gain per second
        self.burn_uses = 0  # Track uses for difficulty scaling
        
        # Break ability
        self.break_cooldown = 0
        self.break_max_cooldown = 20.0
        self.break_glitch_active = False
        self.break_glitch_duration = 0
        self.break_glitch_type = None  # 'help' or 'hurt'
        
    def update(self, dt):
        """Update ability cooldowns and states"""
        # Update cooldowns
        if self.focus_cooldown > 0:
            self.focus_cooldown = max(0, self.focus_cooldown - dt)
        
        if self.burn_cooldown > 0:
            self.burn_cooldown = max(0, self.burn_cooldown - dt)
        
        if self.break_cooldown > 0:
            self.break_cooldown = max(0, self.break_cooldown - dt)
        
        # Update focus state
        if self.focus_active:
            self.focus_timer -= dt
            if self.focus_timer <= 0:
                self.focus_active = False
        
        # Accumulate burn energy
        self.burn_energy = min(100, self.burn_energy + self.burn_energy_rate * dt)
        
        # Update break glitch state
        if self.break_glitch_active:
            self.break_glitch_duration -= dt
            if self.break_glitch_duration <= 0:
                self.break_glitch_active = False
                self.break_glitch_type = None
    
    def can_use_focus(self):
        """Check if focus can be used"""
        return self.focus_cooldown <= 0 and not self.focus_active
    
    def can_use_burn(self):
        """Check if burn can be used"""
        return self.burn_cooldown <= 0 and self.burn_energy >= 50
    
    def can_use_break(self):
        """Check if break can be used"""
        return self.break_cooldown <= 0
    
    def use_focus(self, player):
        """
        Activate Focus ability.
        Player stops moving, reveals hidden threats, shrinks light afterward.
        
        Returns:
            dict: Focus effects
        """
        if not self.can_use_focus():
            return None
        
        # Stop player movement
        player.stop()
        player.is_running = False
        
        # Activate focus
        self.focus_active = True
        self.focus_timer = self.focus_duration
        self.focus_cooldown = self.focus_max_cooldown
        
        # Accumulate light penalty (permanent reduction)
        self.focus_light_penalty += 10
        
        return {
            'reveal_threats': True,
            'stop_movement': True,
            'duration': self.focus_duration
        }
    
    def use_burn(self, player, threat_manager, enemy_manager):
        """
        Activate Burn ability.
        Release stored energy, clear nearby enemies, increase future difficulty.
        
        Returns:
            dict: Burn effects
        """
        if not self.can_use_burn():
            return None
        
        # Consume energy
        energy_used = self.burn_energy
        self.burn_energy = 0
        self.burn_cooldown = self.burn_max_cooldown
        self.burn_uses += 1
        
        # Clear nearby threats based on energy
        clear_radius = 150 + (energy_used / 100) * 100  # 150-250 radius
        
        cleared_count = 0
        
        # Clear hunters
        for hunter in list(threat_manager.hunters):
            dx = player.x - hunter.x
            dy = player.y - hunter.y
            distance = (dx*dx + dy*dy) ** 0.5
            if distance < clear_radius:
                hunter.active = False
                cleared_count += 1
        
        # Clear watchers
        for watcher in list(threat_manager.watchers):
            dx = player.x - watcher.x
            dy = player.y - watcher.y
            distance = (dx*dx + dy*dy) ** 0.5
            if distance < clear_radius:
                watcher.active = False
                cleared_count += 1
        
        # Clear old enemies (backward compatibility)
        for enemy in list(enemy_manager.enemies):
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            distance = (dx*dx + dy*dy) ** 0.5
            if distance < clear_radius:
                enemy.active = False
                cleared_count += 1
        
        # Reduce fear significantly
        player.decrease_fear(40)
        
        # Cost: Increase difficulty multiplier
        difficulty_increase = 1.0 + (self.burn_uses * 0.1)
        
        return {
            'cleared_count': cleared_count,
            'clear_radius': clear_radius,
            'difficulty_increase': difficulty_increase,
            'energy_used': energy_used
        }
    
    def use_break(self, ai_companion, reality_system):
        """
        Activate Break ability.
        Deliberately ignore AI warning, cause reality glitch (can help or hurt).
        
        Returns:
            dict: Break effects
        """
        if not self.can_use_break():
            return None
        
        self.break_cooldown = self.break_max_cooldown
        
        # Trigger reality glitch
        self.break_glitch_active = True
        self.break_glitch_duration = random.uniform(2.0, 5.0)
        
        # 50/50 chance of help or hurt
        self.break_glitch_type = random.choice(['help', 'hurt'])
        
        # Affect AI behavior
        if ai_companion:
            # AI reacts to defiance
            ai_companion.doubt = min(1.0, ai_companion.doubt + 0.15)
            ai_companion.confidence = max(0.2, ai_companion.confidence - 0.1)
        
        # Affect reality stability
        if reality_system:
            reality_system.lie_count += 1  # Treat as reality violation
        
        # Determine glitch effects
        if self.break_glitch_type == 'help':
            effects = {
                'type': 'help',
                'speed_boost': 1.5,
                'invisibility': 0.7,  # Harder to detect
                'duration': self.break_glitch_duration
            }
        else:
            effects = {
                'type': 'hurt',
                'control_reverse': 0.5,  # Controls partially reversed
                'vision_distort': 0.8,
                'duration': self.break_glitch_duration
            }
        
        return effects
    
    def get_light_penalty(self):
        """Get accumulated light radius penalty from Focus uses"""
        return self.focus_light_penalty
    
    def get_burn_difficulty_multiplier(self):
        """Get difficulty multiplier from Burn uses"""
        return 1.0 + (self.burn_uses * 0.1)
    
    def is_focus_active(self):
        """Check if Focus is currently active"""
        return self.focus_active
    
    def get_break_glitch_effects(self):
        """Get current Break glitch effects"""
        if not self.break_glitch_active:
            return None
        
        if self.break_glitch_type == 'help':
            return {
                'type': 'help',
                'speed_boost': 1.5,
                'invisibility': 0.7
            }
        else:
            return {
                'type': 'hurt',
                'control_reverse': 0.5,
                'vision_distort': 0.8
            }
    
    def get_state_dict(self):
        """Get ability state for serialization"""
        return {
            'focus_cooldown': self.focus_cooldown,
            'focus_active': self.focus_active,
            'focus_light_penalty': self.focus_light_penalty,
            'burn_cooldown': self.burn_cooldown,
            'burn_energy': self.burn_energy,
            'burn_uses': self.burn_uses,
            'break_cooldown': self.break_cooldown,
            'break_glitch_active': self.break_glitch_active,
            'break_glitch_type': self.break_glitch_type
        }
