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

class GameState:
    """Main game state manager"""
    
    def __init__(self):
        """Initialize game state"""
        self.player = Player(400, 300)  # Start in center
        self.world = World()
        self.enemy_manager = EnemyManager()
        
        # Load previous playthrough for AI companion
        self.ai_companion = AICompanion()
        self.ai_companion.load_previous_playthrough()
        
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
        """Update game state"""
        self.game_time += dt
        
        # Update subsystems
        self.player.update(dt)
        self.world.update(dt, self.trust_level)
        self.enemy_manager.update(dt, self.player, self.trust_level)
        self.ai_companion.update(dt, self)
        
        # Check for ending conditions
        self._check_ending_conditions()
        
        # Adjust difficulty based on trust
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
        
    def ignore_advice(self):
        """Player ignored AI advice"""
        self.advice_ignored += 1
        self.trust_level = max(0.0, self.trust_level - 0.05)
        self.record_action("advice_ignored", {"trust_level": self.trust_level})
        
    def _adjust_difficulty(self):
        """Adjust game difficulty based on trust level"""
        # High trust = easier (AI helps more)
        # Low trust = harder (AI misleads or withdraws help)
        if self.trust_level > 0.7:
            self.enemy_manager.difficulty_modifier = 0.8
        elif self.trust_level < 0.3:
            self.enemy_manager.difficulty_modifier = 1.3
        else:
            self.enemy_manager.difficulty_modifier = 1.0
            
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
            "actions": self.playthrough_actions
        }
        
        # Save as latest playthrough (will be loaded next time)
        with open("playthroughs/latest.json", "w") as f:
            json.dump(playthrough_data, f, indent=2)
            
        # Also save with timestamp
        filename = f"playthroughs/playthrough_{int(self.start_time)}.json"
        with open(filename, "w") as f:
            json.dump(playthrough_data, f, indent=2)
