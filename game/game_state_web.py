"""
Web-based Game State Manager
Adapted from game_state.py without Pygame dependencies
"""

import json
import os
import time
from game.player import Player
from game.world import World
from game.ai_companion import AICompanion
from game.enemy_manager import EnemyManager
from game.behavior_profiler import BehaviorState

class GameStateWeb:
    """Web-compatible game state manager"""
    
    def __init__(self):
        """Initialize game state"""
        self.player = Player(400, 300)
        self.world = World()
        self.enemy_manager = EnemyManager()
        
        # Load previous playthrough for AI companion
        self.ai_companion = AICompanion()
        self.ai_companion.load_previous_playthrough()
        
        # Behavior profiler (tracks how player behaves)
        self.behavior_state = BehaviorState()
        
        # Game state
        self.game_time = 0
        self.should_quit = False
        self.game_phase = "exploration"
        
        # Recording for next playthrough
        self.playthrough_actions = []
        self.start_time = time.time()
        
        # Trust/defiance tracking
        self.trust_level = 0.5
        self.advice_followed = 0
        self.advice_ignored = 0
        
        # Ending determination
        self.ending_triggered = False
        self.ending_type = None
        
        # Input state (for web)
        self.current_input = {
            'move_x': 0,
            'move_y': 0,
            'running': False
        }
        
    def apply_input(self, input_data):
        """Apply player input from web client"""
        self.current_input = {
            'move_x': input_data.get('move_x', 0),
            'move_y': input_data.get('move_y', 0),
            'running': input_data.get('running', False)
        }
        
    def update(self, dt):
        """Update game state"""
        self.game_time += dt
        
        # Apply movement from current input
        if self.current_input['move_x'] != 0 or self.current_input['move_y'] != 0:
            self.player.is_running = self.current_input['running']
            self.player.move(self.current_input['move_x'], self.current_input['move_y'])
            self.record_action("move", {
                "x": self.player.x,
                "y": self.player.y,
                "running": self.player.is_running
            })
        else:
            self.player.stop()
        
        # Update subsystems
        self.player.update(dt)
        self.world.update(dt, self.trust_level)
        self.enemy_manager.update(dt, self.player, self.trust_level)
        self.ai_companion.update(dt, self)
        
        # Update behavior profiler (feeds all adaptive systems)
        self.behavior_state.update(dt, self.player, self.enemy_manager, self.game_time)
        
        # Check for zone exploration
        zone_type = self.world.check_zone_exploration(self.player.x, self.player.y)
        if zone_type:
            self.player.zones_explored += 1
            self.record_action("zone_explored", {"type": zone_type})
            
            if zone_type == "safe":
                self.player.decrease_fear(20)
            elif zone_type == "dangerous":
                self.player.increase_fear(30)
        
        # Check for ending conditions
        self._check_ending_conditions()
        
        # Adjust difficulty based on trust
        self._adjust_difficulty()
        
    def get_state_dict(self):
        """Get current game state as dictionary for JSON serialization"""
        return {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'health': self.player.health,
                'max_health': self.player.max_health,
                'stamina': self.player.stamina,
                'max_stamina': self.player.max_stamina,
                'fear': self.player.fear,
                'zones_explored': self.player.zones_explored,
                'velocity_x': self.player.velocity_x,
                'velocity_y': self.player.velocity_y,
            },
            'world': {
                'fog_density': self.world.fog_density,
                'ambient_darkness': self.world.ambient_darkness,
                'visibility_radius': self.world.get_visibility_radius(self.player.fear),
                'zones': [
                    {
                        'x': z['x'],
                        'y': z['y'],
                        'radius': z['radius'],
                        'explored': z['explored'],
                        'type': z['type']
                    }
                    for z in self.world.zones
                ]
            },
            'enemies': [
                {
                    'x': e.x,
                    'y': e.y,
                    'type': e.type,
                    'alert': e.alert
                }
                for e in self.enemy_manager.enemies
            ],
            'ai': {
                'advice': self.ai_companion.get_current_advice(),
                'confidence': self.ai_companion.confidence,
                'doubt': self.ai_companion.doubt
            },
            'game': {
                'time': self.game_time,
                'trust_level': self.trust_level,
                'advice_followed': self.advice_followed,
                'advice_ignored': self.advice_ignored,
                'ending_triggered': self.ending_triggered,
                'ending_type': self.ending_type,
                'should_quit': self.should_quit
            }
        }
        
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
        
    def _adjust_difficulty(self):
        """Adjust game difficulty based on trust level"""
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
            
        if self.player.health <= 0:
            self.ending_triggered = True
            self.ending_type = "death"
            self.should_quit = True
            
        if self.trust_level >= 0.95 and self.game_time > 180:
            self.ending_triggered = True
            self.ending_type = "trust"
            self.should_quit = True
            
        if self.trust_level <= 0.05 and self.game_time > 180:
            self.ending_triggered = True
            self.ending_type = "defiance"
            self.should_quit = True
            
        if 0.4 <= self.trust_level <= 0.6 and self.game_time > 300:
            self.ending_triggered = True
            self.ending_type = "balance"
            self.should_quit = True
            
        if self.player.zones_explored >= 10 and abs(self.trust_level - 0.5) < 0.1:
            self.ending_triggered = True
            self.ending_type = "transcendence"
            self.should_quit = True
            
    def save_playthrough(self):
        """Save the current playthrough for the next game"""
        if not self.playthrough_actions:
            return
            
        os.makedirs("playthroughs", exist_ok=True)
        
        playthrough_data = {
            "timestamp": self.start_time,
            "duration": self.game_time,
            "ending": self.ending_type,
            "final_trust": self.trust_level,
            "advice_followed": self.advice_followed,
            "advice_ignored": self.advice_ignored,
            "actions": self.playthrough_actions,
            "behavior_profile": self.behavior_state.get_state_dict()
        }
        
        with open("playthroughs/latest.json", "w") as f:
            json.dump(playthrough_data, f, indent=2)
            
        filename = f"playthroughs/playthrough_{int(self.start_time)}.json"
        with open(filename, "w") as f:
            json.dump(playthrough_data, f, indent=2)
