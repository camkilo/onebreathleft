"""
Phase Escalation System
Every 90-120 seconds, add a new rule (not content).
Rules stack to naturally increase complexity.
"""

import random


class GamePhase:
    """Represents a single game phase with its rules"""
    
    def __init__(self, phase_number, name, description, rules):
        self.phase_number = phase_number
        self.name = name
        self.description = description
        self.rules = rules  # Dict of rule effects


class PhaseSystem:
    """
    Manages escalating game phases.
    Each phase adds new rules that stack on previous phases.
    """
    
    def __init__(self):
        self.current_phase = 0
        self.time_in_phase = 0
        self.phase_duration = 90  # Base duration, randomized
        self.active_rules = set()
        
        # Define all phases
        self.phases = [
            GamePhase(
                0, "Calm Before",
                "The world is stable... for now.",
                {}
            ),
            GamePhase(
                1, "First Crack",
                "Enemies no longer die - they disperse and reform.",
                {
                    'enemies_disperse': True,
                    'enemy_respawn_time': 10.0
                }
            ),
            GamePhase(
                2, "Fading Light",
                "Light no longer refills automatically.",
                {
                    'light_auto_refill': False,
                    'light_drain_rate': 2.0
                }
            ),
            GamePhase(
                3, "Doubtful Voice",
                "The AI speaks less... or too much.",
                {
                    'ai_erratic': True,
                    'ai_speech_random': True
                }
            ),
            GamePhase(
                4, "Hostile Edges",
                "Screen edges become dangerous zones.",
                {
                    'edge_damage': True,
                    'edge_damage_rate': 5.0,
                    'edge_threshold': 100
                }
            ),
            GamePhase(
                5, "Time Fracture",
                "Time flows unevenly. Some threats move faster.",
                {
                    'time_distortion': True,
                    'enemy_time_variance': 0.5
                }
            ),
            GamePhase(
                6, "Silent Watchers",
                "Watchers multiply. They're everywhere now.",
                {
                    'watcher_spawn_boost': 2.0,
                    'max_watchers': 6
                }
            ),
            GamePhase(
                7, "Reality Breach",
                "The corruption spreads faster than you can run.",
                {
                    'corruption_expansion_boost': 2.0,
                    'corruption_damage_rate': 3.0
                }
            ),
            GamePhase(
                8, "Final Descent",
                "All rules active. Survival is unlikely.",
                {
                    'all_threats_boosted': True,
                    'spawn_rate_multiplier': 1.5
                }
            )
        ]
    
    def update(self, dt, game_time):
        """Update phase system"""
        self.time_in_phase += dt
        
        # Check if it's time to advance phase
        # Randomize duration: 90-120 seconds
        phase_threshold = self.phase_duration + random.uniform(-15, 15)
        
        if self.time_in_phase >= phase_threshold:
            self._advance_phase()
            self.time_in_phase = 0
    
    def _advance_phase(self):
        """Advance to next phase"""
        if self.current_phase < len(self.phases) - 1:
            self.current_phase += 1
            
            # Add new rules from this phase
            new_phase = self.phases[self.current_phase]
            for rule in new_phase.rules:
                self.active_rules.add(rule)
    
    def get_current_phase(self):
        """Get current phase object"""
        return self.phases[self.current_phase]
    
    def has_rule(self, rule_name):
        """Check if a rule is active"""
        return rule_name in self.active_rules
    
    def get_rule_value(self, rule_name, default=None):
        """Get value for a specific rule"""
        phase = self.phases[self.current_phase]
        return phase.rules.get(rule_name, default)
    
    def get_active_rule_effects(self):
        """Get all active rule effects from all phases"""
        effects = {}
        
        # Accumulate rules from all phases up to current
        for i in range(self.current_phase + 1):
            phase = self.phases[i]
            effects.update(phase.rules)
        
        return effects
    
    def apply_phase_rules_to_enemy_manager(self, enemy_manager, threat_manager):
        """Apply phase rules to enemy/threat systems"""
        # Phase 1: Enemies disperse instead of dying
        if self.has_rule('enemies_disperse'):
            # This is handled in the threat manager update logic
            pass
        
        # Phase 6: Boost watcher spawns
        if self.has_rule('watcher_spawn_boost'):
            boost = self.get_rule_value('watcher_spawn_boost', 1.0)
            max_watchers = self.get_rule_value('max_watchers', 3)
            threat_manager.max_watchers = max_watchers
        
        # Phase 7: Boost corruption expansion
        if self.has_rule('corruption_expansion_boost'):
            boost = self.get_rule_value('corruption_expansion_boost', 1.0)
            for field in threat_manager.corruption_fields:
                field.expansion_rate *= boost
        
        # Phase 8: Boost all threat spawns
        if self.has_rule('spawn_rate_multiplier'):
            multiplier = self.get_rule_value('spawn_rate_multiplier', 1.0)
            # This affects spawn timers in threat manager
    
    def apply_phase_rules_to_player(self, player, dt):
        """Apply phase rules that affect player"""
        effects = {}
        
        # Phase 2: Light drain
        if self.has_rule('light_auto_refill'):
            if not self.get_rule_value('light_auto_refill'):
                drain_rate = self.get_rule_value('light_drain_rate', 2.0)
                effects['light_drain'] = drain_rate * dt
        
        # Phase 4: Edge damage
        if self.has_rule('edge_damage'):
            # Check if player is near edges (handled in game_state)
            effects['edge_damage_active'] = True
            effects['edge_damage_rate'] = self.get_rule_value('edge_damage_rate', 5.0)
            effects['edge_threshold'] = self.get_rule_value('edge_threshold', 100)
        
        # Phase 7: Corruption damage
        if self.has_rule('corruption_damage_rate'):
            effects['corruption_damage_rate'] = self.get_rule_value('corruption_damage_rate', 3.0)
        
        return effects
    
    def apply_phase_rules_to_ai(self, ai_companion):
        """Apply phase rules to AI behavior"""
        # Phase 3: AI becomes erratic
        if self.has_rule('ai_erratic'):
            # AI speech becomes more random
            if self.get_rule_value('ai_speech_random'):
                # Modify AI cooldown randomly
                ai_companion.advice_cooldown = random.uniform(5, 20)
                
                # Increase chance of lies/doubt
                ai_companion.doubt = min(0.9, ai_companion.doubt + 0.2)
    
    def get_time_distortion_factor(self):
        """Get time distortion multiplier for threats"""
        if self.has_rule('time_distortion'):
            variance = self.get_rule_value('enemy_time_variance', 0.5)
            # Return a random time multiplier
            return random.uniform(1.0 - variance, 1.0 + variance)
        return 1.0
    
    def get_phase_announcement(self):
        """Get announcement text for current phase"""
        phase = self.get_current_phase()
        return f"Phase {phase.phase_number}: {phase.name} - {phase.description}"
    
    def get_state_dict(self):
        """Get phase state for serialization"""
        return {
            'current_phase': self.current_phase,
            'time_in_phase': self.time_in_phase,
            'active_rules': list(self.active_rules),
            'phase_name': self.phases[self.current_phase].name
        }
