"""
Game State Manager
Handles the main game state, player stats, and game progression
"""

import json
import os
import time
from game.player import Player
from game.world import World
from game.ai_companion import AICompanion
from game.enemy_manager import EnemyManager
from game.behavior_profiler import BehaviorState
from game.reality_system import RealitySystem
from game.threat_layers import ThreatLayerManager
from game.pressure_spawning import PressureSpawningSystem
from game.player_abilities import PlayerAbilities
from game.phase_system import PhaseSystem
from game.objectives_system import ObjectivesSystem
from game.countdown_system import CountdownSystem

class GameState:
    """Main game state manager"""
    
    def __init__(self):
        """Initialize game state"""
        self.player = Player(400, 300)  # Start in center
        self.world = World()
        self.enemy_manager = EnemyManager()  # Keep for backward compatibility
        
        # NEW SYSTEMS
        # Threat layer system (replaces simple enemy spawning)
        self.threat_manager = ThreatLayerManager()
        
        # Pressure-based spawning system
        self.pressure_system = PressureSpawningSystem()
        
        # Player abilities (Focus, Burn, Break)
        self.abilities = PlayerAbilities()
        
        # Phase escalation system
        self.phase_system = PhaseSystem()
        
        # Objectives system
        self.objectives_system = ObjectivesSystem()
        
        # Countdown/uncertainty system
        self.countdown_system = CountdownSystem()
        
        # Load previous playthrough for AI companion
        self.ai_companion = AICompanion()
        self.ai_companion.load_previous_playthrough()
        
        # Behavior profiler (tracks how player behaves)
        self.behavior_state = BehaviorState()
        
        # Reality system (environmental degradation)
        self.reality_system = RealitySystem()
        
        # Game state
        self.game_time = 0
        self.should_quit = False
        self.game_phase = "exploration"  # exploration, crisis, ending
        
        # Recording for next playthrough
        self.playthrough_actions = []
        self.start_time = time.time()
        
        # Trust/defiance tracking
        self.trust_level = 0.5  # 0 = complete defiance, 1 = complete trust
        self.advice_followed = 0
        self.advice_ignored = 0
        
        # Ending determination
        self.ending_triggered = False
        self.ending_type = None
        
    def update(self, dt):
        """Update game state with all new systems"""
        self.game_time += dt
        
        # Calculate time dilation factors for different entities
        # Player time stretches when hesitating (indecisive = slower perception)
        player_hesitation = self.behavior_state.hesitation_score if hasattr(self.behavior_state, 'hesitation_score') else 0
        player_time_dilation = 1.0 - (player_hesitation * 0.2)  # Up to 20% slower when hesitating
        
        # Enemy time accelerates when off-screen (creates uncanny feeling)
        # AI speech causes subtle time lag (reality slipping)
        ai_speaking = self.ai_companion.current_advice is not None
        enemy_time_dilation = 1.15 if ai_speaking else 1.0
        
        # Apply phase time distortion
        phase_time_factor = self.phase_system.get_time_distortion_factor()
        enemy_time_dilation *= phase_time_factor
        
        # Update player abilities
        self.abilities.update(dt)
        
        # Apply player ability effects
        self._apply_ability_effects(dt)
        
        # Update player with time dilation
        self.player.update(dt, player_time_dilation)
        
        # Apply phase rules to player
        phase_effects = self.phase_system.apply_phase_rules_to_player(self.player, dt)
        self._apply_phase_effects_to_player(phase_effects)
        
        # Update reality system (affects world rendering and behavior)
        self.reality_system.update(dt, self)
        
        # World update with reality stability
        self.world.update(dt, self.trust_level, self.reality_system)
        
        # Update pressure-based spawning system
        pressure_score = self.pressure_system.update(
            dt, 
            self.player, 
            self.threat_manager,
            self.ai_companion, 
            self.trust_level
        )
        
        # Update threat layers (replaces old enemy system)
        self.threat_manager.update(
            dt * enemy_time_dilation,
            self.player,
            self.trust_level,
            pressure_score
        )
        
        # Keep old enemy manager for backward compatibility
        self.enemy_manager.update(
            dt * enemy_time_dilation,
            self.player, 
            self.trust_level, 
            self.behavior_state,
            ai_speaking
        )
        
        # Apply watcher effects (psychological pressure)
        self._apply_watcher_effects()
        
        # Apply corruption field effects
        self._apply_corruption_field_effects()
        
        # Update phase system
        self.phase_system.update(dt, self.game_time)
        self.phase_system.apply_phase_rules_to_enemy_manager(self.enemy_manager, self.threat_manager)
        self.phase_system.apply_phase_rules_to_ai(self.ai_companion)
        
        # Update objectives system
        self.objectives_system.update(dt, self.player, self.threat_manager, self.game_time)
        
        # Update countdown system
        self.countdown_system.update(dt, self)
        
        self.ai_companion.update(dt, self)
        
        # Update behavior profiler (feeds all adaptive systems)
        self.behavior_state.update(dt, self.player, self.enemy_manager, self.game_time)
        
        # Check for ending conditions
        self._check_ending_conditions()
        
        # Adjust difficulty based on trust and abilities
        self._adjust_difficulty()
        
    def record_action(self, action_type, data):
        """Record an action for the next playthrough"""
        action = {
            "time": self.game_time,
            "type": action_type,
            "data": data,
            "trust_level": self.trust_level
        }
        self.playthrough_actions.append(action)
        
    def follow_advice(self):
        """Player followed AI advice"""
        self.advice_followed += 1
        self.trust_level = min(1.0, self.trust_level + 0.05)
        self.record_action("advice_followed", {"trust_level": self.trust_level})
        
        # Notify behavior profiler
        self.behavior_state.on_advice_followed(self.game_time)
        
    def ignore_advice(self):
        """Player ignored AI advice"""
        self.advice_ignored += 1
        self.trust_level = max(0.0, self.trust_level - 0.05)
        self.record_action("advice_ignored", {"trust_level": self.trust_level})
        
        # Notify behavior profiler
        self.behavior_state.on_advice_ignored(self.game_time)
        
        # Notify pressure system (mistake increases pressure)
        self.pressure_system.on_player_mistake()
    
    def use_ability_focus(self):
        """Use Focus ability"""
        result = self.abilities.use_focus(self.player)
        if result:
            self.record_action("ability_focus", {"time": self.game_time})
        return result
    
    def use_ability_burn(self):
        """Use Burn ability"""
        result = self.abilities.use_burn(self.player, self.threat_manager, self.enemy_manager)
        if result:
            self.record_action("ability_burn", {
                "time": self.game_time,
                "cleared": result['cleared_count']
            })
            # Update difficulty
            self._adjust_difficulty()
        return result
    
    def use_ability_break(self):
        """Use Break ability"""
        result = self.abilities.use_break(self.ai_companion, self.reality_system)
        if result:
            self.record_action("ability_break", {
                "time": self.game_time,
                "effect": result['type']
            })
        return result
    
    def _apply_ability_effects(self, dt):
        """Apply active ability effects"""
        # Focus effect: reveal threats
        if self.abilities.is_focus_active():
            # This is handled in rendering/display
            pass
        
        # Break glitch effects
        glitch = self.abilities.get_break_glitch_effects()
        if glitch:
            if glitch['type'] == 'help':
                # Speed boost
                self.player.speed *= glitch.get('speed_boost', 1.0)
            elif glitch['type'] == 'hurt':
                # Control reverse would be handled in input
                pass
    
    def _apply_watcher_effects(self):
        """Apply psychological effects from watchers"""
        watcher_effects = self.threat_manager.get_watcher_effects()
        if watcher_effects:
            # Camera lock (reduces visibility)
            camera_lock = watcher_effects['camera_lock']
            
            # Movement slow
            movement_slow = watcher_effects['movement_slow']
            if movement_slow > 0:
                self.player.speed *= (1.0 - movement_slow * 0.3)
            
            # Tension increases fear
            tension = watcher_effects['tension']
            self.player.increase_fear(tension * 2.0)
    
    def _apply_corruption_field_effects(self):
        """Apply environmental effects from corruption fields"""
        field_effects = self.threat_manager.get_field_effects()
        if field_effects:
            for effect in field_effects:
                intensity = effect['intensity']
                field_type = effect['type']
                
                if field_type == 'drain_light':
                    # Drain visibility/light
                    self.player.increase_fear(intensity * 5.0)
                elif field_type == 'distort_controls':
                    # Control distortion (handled in input)
                    pass
                elif field_type == 'slow_time':
                    # Slow player movement
                    self.player.speed *= (1.0 - intensity * 0.2)
    
    def _apply_phase_effects_to_player(self, phase_effects):
        """Apply phase rule effects to player"""
        if not phase_effects:
            return
        
        # Light drain
        if 'light_drain' in phase_effects:
            # Increase fear as "light" drains
            self.player.increase_fear(phase_effects['light_drain'])
        
        # Edge damage
        if phase_effects.get('edge_damage_active'):
            # Check if player is near world edges
            dx = abs(self.player.x - self.world.world_center_x)
            dy = abs(self.player.y - self.world.world_center_y)
            distance = max(dx, dy)
            
            edge_threshold = phase_effects.get('edge_threshold', 100)
            if distance < edge_threshold:
                damage_rate = phase_effects.get('edge_damage_rate', 5.0)
                self.player.take_damage(damage_rate * 0.016)  # Per frame at 60fps
        
        # Corruption damage (from fields)
        if 'corruption_damage_rate' in phase_effects:
            field_effects = self.threat_manager.get_field_effects()
            if field_effects:
                damage_rate = phase_effects['corruption_damage_rate']
                for effect in field_effects:
                    intensity = effect['intensity']
                    self.player.take_damage(damage_rate * intensity * 0.016)
        
    def _adjust_difficulty(self):
        """Adjust game difficulty based on trust level and abilities"""
        # High trust = easier (AI helps more)
        # Low trust = harder (AI misleads or withdraws help)
        base_modifier = 1.0
        if self.trust_level > 0.7:
            base_modifier = 0.8
        elif self.trust_level < 0.3:
            base_modifier = 1.3
        
        # Apply burn ability difficulty increase
        burn_multiplier = self.abilities.get_burn_difficulty_multiplier()
        
        self.enemy_manager.difficulty_modifier = base_modifier * burn_multiplier
            
    def _check_ending_conditions(self):
        """Check if any ending conditions are met"""
        if self.ending_triggered:
            return
            
        # Death ending
        if self.player.health <= 0:
            self.ending_triggered = True
            self.ending_type = "death"
            self.should_quit = True
            
        # Trust ending (complete trust in AI)
        if self.trust_level >= 0.95 and self.game_time > 180:
            self.ending_triggered = True
            self.ending_type = "trust"
            self.should_quit = True
            
        # Defiance ending (complete rejection of AI)
        if self.trust_level <= 0.05 and self.game_time > 180:
            self.ending_triggered = True
            self.ending_type = "defiance"
            self.should_quit = True
            
        # Survival ending (balanced approach)
        if 0.4 <= self.trust_level <= 0.6 and self.game_time > 300:
            self.ending_triggered = True
            self.ending_type = "balance"
            self.should_quit = True
            
        # Transcendence ending (understanding the system)
        if self.player.zones_explored >= 10 and abs(self.trust_level - 0.5) < 0.1:
            self.ending_triggered = True
            self.ending_type = "transcendence"
            self.should_quit = True
            
    def save_playthrough(self):
        """Save the current playthrough for the next game"""
        if not self.playthrough_actions:
            return
            
        # Create playthroughs directory
        os.makedirs("playthroughs", exist_ok=True)
        
        playthrough_data = {
            "timestamp": self.start_time,
            "duration": self.game_time,
            "ending": self.ending_type,
            "final_trust": self.trust_level,
            "advice_followed": self.advice_followed,
            "advice_ignored": self.advice_ignored,
            "actions": self.playthrough_actions,
            "behavior_profile": self.behavior_state.get_state_dict(),
            "ai_intent_history": self.ai_companion.intent_history,
            "abilities_used": self.abilities.get_state_dict(),
            "final_phase": self.phase_system.get_state_dict(),
            "objectives_completed": self.objectives_system.get_objectives_count(),
            "countdown_stats": self.countdown_system.get_lie_statistics(),
            "pressure_final": self.pressure_system.pressure_score
        }
        
        # Save as latest playthrough (will be loaded next time)
        with open("playthroughs/latest.json", "w") as f:
            json.dump(playthrough_data, f, indent=2)
            
        # Also save with timestamp
        filename = f"playthroughs/playthrough_{int(self.start_time)}.json"
        with open(filename, "w") as f:
            json.dump(playthrough_data, f, indent=2)
