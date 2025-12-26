"""
AI Companion
The companion is actually a playback of the previous player's actions
It gives advice based on what the previous player did
"""

import json
import os
import random

class AICompanion:
    """AI Companion that learns from previous playthrough"""
    
    def __init__(self):
        """Initialize AI companion"""
        self.previous_playthrough = None
        self.current_advice = None
        self.advice_timer = 0
        self.advice_cooldown = 10  # seconds between advice
        
        # AI personality traits (affected by previous playthrough)
        self.confidence = 0.7  # How confident the AI sounds
        self.honesty = 0.8  # Likelihood of telling truth vs lying
        self.doubt = 0.2  # How much the AI doubts itself
        
        # Advice history
        self.advice_history = []
        
    def load_previous_playthrough(self):
        """Load the previous playthrough data"""
        try:
            if os.path.exists("playthroughs/latest.json"):
                with open("playthroughs/latest.json", "r") as f:
                    self.previous_playthrough = json.load(f)
                    
                # Adjust AI personality based on previous playthrough
                if self.previous_playthrough:
                    ending = self.previous_playthrough.get("ending")
                    final_trust = self.previous_playthrough.get("final_trust", 0.5)
                    
                    # AI becomes more doubtful if previous player died
                    if ending == "death":
                        self.doubt = 0.7
                        self.confidence = 0.4
                        
                    # AI becomes more confident if previous player trusted them
                    if final_trust > 0.7:
                        self.confidence = 0.9
                        self.doubt = 0.1
                        
                    # AI becomes deceptive if previous player was defiant
                    if final_trust < 0.3:
                        self.honesty = 0.5
                        self.confidence = 0.6
                        
        except Exception as e:
            print(f"Could not load previous playthrough: {e}")
            self.previous_playthrough = None
            
    def update(self, dt, game_state):
        """Update AI companion"""
        self.advice_timer += dt
        
        # Generate new advice periodically
        if self.advice_timer >= self.advice_cooldown and not self.current_advice:
            self.current_advice = self._generate_advice(game_state)
            self.advice_timer = 0
            
        # Clear advice after some time
        if self.current_advice and self.advice_timer > 5:
            self.current_advice = None
            
    def _generate_advice(self, game_state):
        """Generate advice based on previous playthrough and current situation"""
        advice = {
            "text": "",
            "type": "",  # warning, suggestion, encouragement, doubt
            "is_lie": False
        }
        
        # Check if we have previous playthrough data
        if self.previous_playthrough and self.previous_playthrough.get("actions"):
            # Find actions around current game time
            relevant_actions = [
                a for a in self.previous_playthrough["actions"]
                if abs(a["time"] - game_state.game_time) < 30
            ]
            
            if relevant_actions:
                advice = self._advice_from_history(relevant_actions, game_state)
            else:
                advice = self._generic_advice(game_state)
        else:
            advice = self._generic_advice(game_state)
            
        # AI might lie or doubt itself
        if random.random() > self.honesty:
            advice["is_lie"] = True
            advice["text"] = self._invert_advice(advice["text"])
            
        if random.random() < self.doubt:
            advice["text"] = f"I think... {advice['text']} ...but I'm not sure."
            advice["type"] = "doubt"
            
        self.advice_history.append(advice)
        return advice
        
    def _advice_from_history(self, actions, game_state):
        """Generate advice based on historical actions"""
        advice_options = [
            {
                "text": "The last one who was here... they went left. It didn't end well.",
                "type": "warning"
            },
            {
                "text": "I remember this place. Stay close to the edges.",
                "type": "suggestion"
            },
            {
                "text": "They ran when they saw it. You should too.",
                "type": "warning"
            },
            {
                "text": "Trust me on this one. Keep moving forward.",
                "type": "suggestion"
            },
            {
                "text": "The previous version of you stopped here. Don't make the same mistake.",
                "type": "warning"
            }
        ]
        
        return random.choice(advice_options)
        
    def _generic_advice(self, game_state):
        """Generate generic advice based on current situation"""
        player = game_state.player
        
        if player.health < 30:
            return {
                "text": "You're hurt. Find somewhere to rest.",
                "type": "warning"
            }
        elif player.fear > 70:
            return {
                "text": "Calm down. Fear will kill you faster than anything else here.",
                "type": "encouragement"
            }
        elif player.stamina < 30:
            return {
                "text": "Conserve your energy. You'll need it.",
                "type": "suggestion"
            }
        elif game_state.enemy_manager.enemies:
            return {
                "text": "Something is near. Stay quiet.",
                "type": "warning"
            }
        else:
            return {
                "text": "Keep exploring. There must be a way out.",
                "type": "encouragement"
            }
            
    def _invert_advice(self, text):
        """Invert advice to create a lie"""
        inversions = {
            "left": "right",
            "right": "left",
            "forward": "back",
            "stay": "leave",
            "run": "stay still",
            "stop": "keep going",
            "rest": "keep moving",
            "calm": "panic",
        }
        
        # Apply all inversions found in the text
        inverted_text = text.lower()
        for original, inverted in inversions.items():
            if original in inverted_text:
                inverted_text = inverted_text.replace(original, inverted)
                
        return inverted_text
        
    def get_current_advice(self):
        """Get current advice text"""
        if self.current_advice:
            return self.current_advice["text"]
        return None
