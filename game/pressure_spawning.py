"""
Pressure-Based Spawning System
Spawn rate based on player behavior, not timers.
The game should hate silence - spawn threats when it feels "safe".
"""

import math


class PressureSpawningSystem:
    """
    Calculates spawning pressure based on multiple factors.
    Output is a pressure score (0-1) that drives threat spawning.
    
    CRITICAL RULE: If nothing has interacted with the player in 5 seconds,
    spawn a threat at screen edge moving inward.
    """
    
    def __init__(self):
        # Tracking variables
        self.player_stillness_duration = 0
        self.time_since_last_damage = 0
        self.time_since_last_advice = 0
        self.screen_emptiness_duration = 0
        self.time_since_last_interaction = 0  # Track ALL interactions
        
        # Thresholds
        self.stillness_threshold = 2.0  # seconds before stillness increases pressure
        self.safe_feeling_threshold = 5.0  # seconds of "safety" before spawning
        self.forced_spawn_threshold = 5.0  # RULE: Force spawn after 5 seconds
        self.stillness_speed_threshold_sq = 400  # 20^2 - avoid sqrt for performance
        
        # Current pressure score
        self.pressure_score = 0.3  # Start with moderate pressure
        
        # Forced spawn state
        self.needs_forced_spawn = False
        
    def update(self, dt, player, threat_manager, ai_companion, trust_level):
        """
        Calculate spawning pressure based on game state.
        
        Returns:
            float: Pressure score (0-1)
        """
        # Track time since ANY interaction (damage, advice, enemy presence)
        self.time_since_last_interaction += dt
        
        # Track player stillness using squared magnitude (avoid sqrt)
        player_speed_sq = player.velocity_x**2 + player.velocity_y**2
        if player_speed_sq < self.stillness_speed_threshold_sq:  # Standing still
            self.player_stillness_duration += dt
        else:
            self.player_stillness_duration = max(0, self.player_stillness_duration - dt * 0.5)
        
        # Track time since last damage
        self.time_since_last_damage += dt
        
        # Track time since last AI advice
        if ai_companion.current_advice:
            self.time_since_last_advice = 0
            self.time_since_last_interaction = 0  # AI advice counts as interaction
        else:
            self.time_since_last_advice += dt
        
        # Track screen emptiness (no nearby threats)
        threat_count = threat_manager.get_total_threat_count()
        if threat_count == 0:
            self.screen_emptiness_duration += dt
        else:
            self.screen_emptiness_duration = 0
            # Any threat presence counts as interaction
            self.time_since_last_interaction = 0
        
        # CRITICAL RULE: Force spawn if no interaction for 5 seconds
        if self.time_since_last_interaction >= self.forced_spawn_threshold:
            self.needs_forced_spawn = True
        
        # Calculate pressure components
        stillness_pressure = self._calculate_stillness_pressure()
        trust_pressure = self._calculate_trust_pressure(trust_level)
        safety_pressure = self._calculate_safety_pressure()
        emptiness_pressure = self._calculate_emptiness_pressure()
        
        # Combine pressures (weighted average)
        self.pressure_score = (
            stillness_pressure * 0.3 +
            trust_pressure * 0.25 +
            safety_pressure * 0.25 +
            emptiness_pressure * 0.2
        )
        
        # Clamp to 0-1
        self.pressure_score = max(0.0, min(1.0, self.pressure_score))
        
        return self.pressure_score
    
    def _calculate_stillness_pressure(self):
        """Player standing still attracts attention"""
        if self.player_stillness_duration > self.stillness_threshold:
            # Pressure increases the longer they stand still
            excess_time = self.player_stillness_duration - self.stillness_threshold
            return min(1.0, 0.3 + excess_time * 0.15)
        return 0.2  # Base pressure
    
    def _calculate_trust_pressure(self, trust_level):
        """Low trust = more hostile spawns"""
        # Invert trust: low trust = high pressure
        return 1.0 - trust_level
    
    def _calculate_safety_pressure(self):
        """Time since last threat = spawn something"""
        if self.time_since_last_damage > self.safe_feeling_threshold:
            # Feeling safe? Not for long.
            excess_time = self.time_since_last_damage - self.safe_feeling_threshold
            return min(1.0, 0.4 + excess_time * 0.1)
        return 0.3
    
    def _calculate_emptiness_pressure(self):
        """Screen feels empty = fill it with dread"""
        if self.screen_emptiness_duration > 3.0:
            # Screen has been empty too long
            return min(1.0, 0.5 + self.screen_emptiness_duration * 0.1)
        return 0.2
    
    def on_player_damaged(self):
        """Reset safety timer when player takes damage"""
        self.time_since_last_damage = 0
        self.time_since_last_interaction = 0  # Damage is interaction
        self.needs_forced_spawn = False  # Clear forced spawn flag
        
    def on_interaction(self):
        """Reset interaction timer - called for any player interaction"""
        self.time_since_last_interaction = 0
        self.needs_forced_spawn = False  # Clear forced spawn flag
    
    def should_force_spawn(self):
        """Check if forced spawn is needed (5 second rule)"""
        return self.needs_forced_spawn
    
    def reset_forced_spawn(self):
        """Clear forced spawn flag after spawning"""
        self.needs_forced_spawn = False
        self.time_since_last_interaction = 0
    
    def on_player_mistake(self):
        """Player made a mistake (missed advice, bad decision)"""
        # Increase pressure briefly
        self.pressure_score = min(1.0, self.pressure_score + 0.2)
    
    def get_pressure_description(self):
        """Get human-readable pressure level"""
        if self.pressure_score < 0.3:
            return "low"
        elif self.pressure_score < 0.6:
            return "moderate"
        elif self.pressure_score < 0.8:
            return "high"
        else:
            return "extreme"
