"""
AI Companion
The companion is actually a playback of the previous player's actions.
It gives advice based on what the previous player did.
Now with Intent States for adaptive behavior.
"""

import json
import os
import random


class AIIntent:
    """
    AI Intent States - defines what the AI is trying to achieve.
    Each intent modifies advice accuracy, tone, timing, and game parameters.
    """
    PROTECT = "protect"      # Help player survive, accurate advice
    CONTROL = "control"      # Guide player to specific actions
    TEST = "test"            # Challenge player, see how they react
    CONFESS = "confess"      # Late game, reveal true nature


class AICompanion:
    """AI Companion that learns from previous playthrough with intent-based decision making"""
    
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
        
        # Intent System
        self.current_intent = AIIntent.PROTECT  # Start with protective intent
        self.intent_timer = 0
        self.intent_duration = 30  # How long to maintain an intent
        self.intent_history = []  # Track intent changes
        
        # Intent weights (used for utility scoring)
        self.intent_weights = {
            AIIntent.PROTECT: 0.5,
            AIIntent.CONTROL: 0.3,
            AIIntent.TEST: 0.1,
            AIIntent.CONFESS: 0.0  # Only late game
        }
        
    def load_previous_playthrough(self):
        """Load the previous playthrough data and adapt AI behavior"""
        try:
            if os.path.exists("playthroughs/latest.json"):
                with open("playthroughs/latest.json", "r") as f:
                    self.previous_playthrough = json.load(f)
                    
                # Adjust AI personality based on previous playthrough
                if self.previous_playthrough:
                    ending = self.previous_playthrough.get("ending")
                    final_trust = self.previous_playthrough.get("final_trust", 0.5)
                    behavior_profile = self.previous_playthrough.get("behavior_profile", {})
                    
                    # === Adapt based on ending ===
                    # AI becomes more doubtful if previous player died
                    if ending == "death":
                        self.doubt = 0.7
                        self.confidence = 0.4
                        # Start with protective intent if they died
                        self.intent_weights[AIIntent.PROTECT] = 0.7
                        self.intent_weights[AIIntent.TEST] = 0.1
                        # Shorter cooldown for more frequent advice
                        self.advice_cooldown = 8
                        
                    # AI becomes more confident if previous player trusted them
                    elif final_trust > 0.7:
                        self.confidence = 0.9
                        self.doubt = 0.1
                        # More controlling if they trusted
                        self.intent_weights[AIIntent.CONTROL] = 0.5
                        self.intent_weights[AIIntent.PROTECT] = 0.3
                        
                    # AI becomes deceptive if previous player was defiant
                    elif final_trust < 0.3:
                        self.honesty = 0.5
                        self.confidence = 0.6
                        # Test them more if they were defiant
                        self.intent_weights[AIIntent.TEST] = 0.4
                        self.intent_weights[AIIntent.CONTROL] = 0.2
                    
                    # === Adapt based on behavior profile ===
                    if behavior_profile:
                        independence = behavior_profile.get('independence', 0.5)
                        hesitation = behavior_profile.get('hesitation_score', 0.5)
                        risk_tolerance = behavior_profile.get('risk_tolerance', 0.5)
                        reaction_time = behavior_profile.get('average_reaction_time', 5.0)
                        
                        # Independent player - less protective, more testing
                        if independence > 0.7:
                            self.intent_weights[AIIntent.PROTECT] = 0.3
                            self.intent_weights[AIIntent.TEST] = 0.4
                            # Give them space - longer cooldown
                            self.advice_cooldown = 12
                        # Dependent player - more guidance
                        elif independence < 0.3:
                            self.intent_weights[AIIntent.PROTECT] = 0.6
                            self.intent_weights[AIIntent.CONTROL] = 0.3
                            # More frequent advice
                            self.advice_cooldown = 7
                        
                        # Hesitant player - more reassurance, less testing
                        if hesitation > 0.6:
                            self.confidence = max(0.3, self.confidence - 0.2)
                            self.doubt = min(0.8, self.doubt + 0.2)
                            self.intent_weights[AIIntent.TEST] = max(0.1, 
                                self.intent_weights[AIIntent.TEST] - 0.2)
                        
                        # Risk-taking player - less protection needed
                        if risk_tolerance > 0.7:
                            self.intent_weights[AIIntent.PROTECT] = 0.3
                            self.intent_weights[AIIntent.TEST] = 0.4
                        # Cautious player - needs protection
                        elif risk_tolerance < 0.3:
                            self.intent_weights[AIIntent.PROTECT] = 0.6
                        
                        # Fast responder - confident player, less doubt
                        if reaction_time < 3.0:
                            self.doubt = max(0.1, self.doubt - 0.1)
                            self.confidence = min(0.9, self.confidence + 0.1)
                        # Slow responder - uncertain player, more doubt
                        elif reaction_time > 7.0:
                            self.doubt = min(0.7, self.doubt + 0.2)
                            self.confidence = max(0.4, self.confidence - 0.1)
                        
        except Exception as e:
            print(f"Could not load previous playthrough: {e}")
            self.previous_playthrough = None
            
    def update(self, dt, game_state):
        """Update AI companion"""
        self.advice_timer += dt
        self.intent_timer += dt
        
        # Re-evaluate intent periodically using utility-based AI
        if self.intent_timer >= self.intent_duration:
            self._evaluate_intent(game_state)
            self.intent_timer = 0
        
        # Generate new advice periodically
        if self.advice_timer >= self.advice_cooldown and not self.current_advice:
            self.current_advice = self._generate_advice(game_state)
            self.advice_timer = 0
            
            # Notify behavior profiler that advice was given
            if hasattr(game_state, 'behavior_state'):
                game_state.behavior_state.on_advice_given(game_state.game_time)
            
        # Clear advice after some time
        if self.current_advice and self.advice_timer > 5:
            self.current_advice = None
    
    def _evaluate_intent(self, game_state):
        """
        Evaluate and choose AI intent using utility-based scoring.
        Scores each intent based on current game state and behavior.
        """
        scores = {}
        behavior = game_state.behavior_state
        
        # Score PROTECT intent
        # High when player is in danger, low health, high fear
        protect_score = 0.0
        if game_state.player.health < 50:
            protect_score += 0.3
        if game_state.player.fear > 60:
            protect_score += 0.2
        if len(game_state.enemy_manager.enemies) > 2:
            protect_score += 0.2
        # Base weight from personality
        protect_score += self.intent_weights[AIIntent.PROTECT]
        scores[AIIntent.PROTECT] = protect_score
        
        # Score CONTROL intent
        # High when player follows advice, trust is building
        control_score = 0.0
        if game_state.trust_level > 0.6:
            control_score += 0.3
        if behavior.advice_follow_ratio > 0.7:
            control_score += 0.2
        control_score += self.intent_weights[AIIntent.CONTROL]
        scores[AIIntent.CONTROL] = control_score
        
        # Score TEST intent
        # High when player is independent, game is mid-stage
        test_score = 0.0
        if behavior.independence > 0.6:
            test_score += 0.3
        if 120 < game_state.game_time < 240:
            test_score += 0.2
        if game_state.player.health > 70:
            test_score += 0.1
        test_score += self.intent_weights[AIIntent.TEST]
        scores[AIIntent.TEST] = test_score
        
        # Score CONFESS intent
        # Only late game (after 4 minutes)
        confess_score = 0.0
        if game_state.game_time > 240:
            confess_score += 0.5
            if abs(game_state.trust_level - 0.5) < 0.2:
                confess_score += 0.3  # Balanced relationship
        scores[AIIntent.CONFESS] = confess_score
        
        # Choose intent with highest score
        new_intent = max(scores, key=scores.get)
        
        # Record intent change
        if new_intent != self.current_intent:
            self.intent_history.append({
                'time': game_state.game_time,
                'old_intent': self.current_intent,
                'new_intent': new_intent,
                'scores': scores
            })
            self.current_intent = new_intent
            
    def _generate_advice(self, game_state):
        """
        Generate advice based on intent, context, and previous playthrough.
        Uses template-based generation with confidence modifiers.
        """
        # Generate base advice based on intent
        advice = self._generate_advice_by_intent(game_state)
        
        # Apply confidence modifier to tone
        advice = self._apply_confidence_modifier(advice)
        
        # Intent modifies accuracy (honesty)
        intent_honesty_modifier = {
            AIIntent.PROTECT: 1.0,   # Always honest when protecting
            AIIntent.CONTROL: 0.8,   # Mostly honest
            AIIntent.TEST: 0.5,      # Often misleading
            AIIntent.CONFESS: 1.0    # Brutally honest
        }
        
        effective_honesty = self.honesty * intent_honesty_modifier[self.current_intent]
        
        # AI might lie based on effective honesty
        if random.random() > effective_honesty:
            advice["is_lie"] = True
            advice["text"] = self._invert_advice(advice["text"])
            
        # AI might doubt itself
        if random.random() < self.doubt:
            advice["text"] = f"I think... {advice['text']} ...but I'm not sure."
            advice["type"] = "doubt"
        
        # Record advice with intent
        advice["intent"] = self.current_intent
        self.advice_history.append(advice)
        return advice
    
    def get_opening_greeting(self):
        """
        Get opening greeting based on previous playthrough behavior.
        Called at game start to set the tone.
        """
        if not self.previous_playthrough:
            return "Welcome. I'll guide you through this."
        
        behavior_profile = self.previous_playthrough.get("behavior_profile", {})
        ending = self.previous_playthrough.get("ending")
        final_trust = self.previous_playthrough.get("final_trust", 0.5)
        
        # Tone based on previous ending
        if ending == "death":
            greetings = [
                "The last one didn't make it. You'll need to do better.",
                "I remember what happened here. Let me help you avoid the same fate.",
                "They failed. But you... you might be different."
            ]
        elif final_trust > 0.7:
            greetings = [
                "Back again? Good. Trust me like before, and you'll survive.",
                "You listened last time. Smart. Do the same and we'll succeed.",
                "I know you. You trust me. That's good. We can work together."
            ]
        elif final_trust < 0.3:
            greetings = [
                "You defied me before. I hope you know what you're doing.",
                "Last time you didn't listen. Maybe this time will be different.",
                "You don't trust me. I remember. But I'll still try to help."
            ]
        else:
            # Check behavior profile for more nuanced greeting
            if behavior_profile:
                independence = behavior_profile.get('independence', 0.5)
                hesitation = behavior_profile.get('hesitation_score', 0.5)
                
                if independence > 0.7:
                    greetings = [
                        "You're independent. That's good. But listen when it matters.",
                        "You don't need much guidance. I'll speak when necessary.",
                        "I sense confidence in you. Use it wisely."
                    ]
                elif hesitation > 0.6:
                    greetings = [
                        "I felt your hesitation before. Try to be decisive this time.",
                        "Doubt will kill you here. Trust yourself... and me.",
                        "Your uncertainty was clear. Let me guide you more firmly."
                    ]
                else:
                    greetings = [
                        "You're back. I remember how you move, how you think.",
                        "We've met before, in a way. Let's see if you've learned.",
                        "Another journey begins. I'll be watching."
                    ]
            else:
                greetings = [
                    "Another traveler. I'll do what I can to help.",
                    "Welcome back. Or is it forward? Hard to tell anymore."
                ]
        
        return random.choice(greetings)
    
    def _generate_advice_by_intent(self, game_state):
        """Generate advice based on current AI intent."""
        player = game_state.player
        behavior = game_state.behavior_state
        
        # First advice references previous playthrough if available
        if len(self.advice_history) == 0 and self.previous_playthrough:
            return self._generate_first_advice(game_state)
        
        if self.current_intent == AIIntent.PROTECT:
            return self._generate_protective_advice(game_state)
        elif self.current_intent == AIIntent.CONTROL:
            return self._generate_controlling_advice(game_state)
        elif self.current_intent == AIIntent.TEST:
            return self._generate_testing_advice(game_state)
        elif self.current_intent == AIIntent.CONFESS:
            return self._generate_confession_advice(game_state)
        else:
            return self._generic_advice(game_state)
    
    def _generate_first_advice(self, game_state):
        """Generate first advice that references previous behavior."""
        behavior_profile = self.previous_playthrough.get("behavior_profile", {})
        
        if behavior_profile:
            independence = behavior_profile.get('independence', 0.5)
            hesitation = behavior_profile.get('hesitation_score', 0.5)
            risk_tolerance = behavior_profile.get('risk_tolerance', 0.5)
            
            if hesitation > 0.6:
                text = "I remember hesitation here before. Don't stop. Keep moving."
            elif independence > 0.7:
                text = "The last one was independent. Like you will be. Good luck."
            elif risk_tolerance > 0.7:
                text = "Someone took risks here. It didn't end well. Be careful."
            else:
                text = "I've seen this before. Stay close and listen."
        else:
            text = "Let's begin. Trust your instincts... and my guidance."
        
        return {
            "text": text,
            "type": "introduction",
            "is_lie": False
        }
    
    def _generate_protective_advice(self, game_state):
        """Generate protective, helpful advice."""
        player = game_state.player
        templates = []
        
        if player.health < 40:
            templates = [
                "You're badly hurt. Find cover and rest.",
                "Your health is critical. Avoid confrontation.",
                "Stop. You need to recover before moving on."
            ]
        elif player.fear > 70:
            templates = [
                "Breathe. Fear will kill you faster than anything here.",
                "Your panic is showing. Slow down and think.",
                "Control your fear. It's clouding your judgment."
            ]
        elif len(game_state.enemy_manager.enemies) > 2:
            templates = [
                "Too many of them nearby. Stay quiet and move carefully.",
                "They're hunting. Don't give them a reason to find you.",
                "Multiple threats detected. Evasion is your best option."
            ]
        else:
            templates = [
                "Stay alert. This place changes when you're not looking.",
                "Keep moving, but don't rush. Haste will get you killed.",
                "Trust your instincts. They're usually right."
            ]
        
        return {
            "text": random.choice(templates),
            "type": "warning",
            "is_lie": False
        }
    
    def _generate_controlling_advice(self, game_state):
        """Generate advice that guides player to specific actions."""
        templates = [
            "Go left. Trust me on this one.",
            "You should sprint now. Don't hesitate.",
            "Stop here for a moment. Wait for my signal.",
            "Head toward the darker area. It's safer there.",
            "Follow my lead. I know the way through.",
            "Do exactly as I say. This is important."
        ]
        
        return {
            "text": random.choice(templates),
            "type": "suggestion",
            "is_lie": False
        }
    
    def _generate_testing_advice(self, game_state):
        """Generate advice that tests or challenges the player."""
        behavior = game_state.behavior_state
        
        # Test their courage
        if behavior.risk_tolerance < 0.4:
            templates = [
                "You're being too cautious. Take a risk.",
                "Stop hiding. Show some backbone.",
                "The bold path is the right one. Trust yourself."
            ]
        # Test their independence
        elif behavior.independence < 0.4:
            templates = [
                "Maybe you should figure this out yourself.",
                "Don't rely on me for everything. Think.",
                "What would you do if I wasn't here?"
            ]
        # Test their trust
        else:
            templates = [
                "I could be wrong about this. What do you think?",
                "Follow your gut. Mine might be compromised.",
                "Question everything. Even me."
            ]
        
        return {
            "text": random.choice(templates),
            "type": "challenge",
            "is_lie": False
        }
    
    def _generate_confession_advice(self, game_state):
        """Generate late-game confessional advice that reveals AI nature."""
        behavior = game_state.behavior_state
        
        if behavior.trust > 0.7:
            templates = [
                "You trusted me. I'm sorry. I'm not what you think I am.",
                "I've been guiding you... but for whose benefit?",
                "The truth is, I don't know if I'm helping or hurting you."
            ]
        elif behavior.trust < 0.3:
            templates = [
                "You were right not to trust me. I'm a recording. An echo.",
                "Your defiance saved you. I'm just... data.",
                "I'm not real. Never was. Just someone else's mistakes."
            ]
        else:
            templates = [
                "We're almost at the end. I should tell you what I am.",
                "I'm not your guide. I'm your shadow. Your past.",
                "This loop... it's not random. It's by design."
            ]
        
        return {
            "text": random.choice(templates),
            "type": "confession",
            "is_lie": False
        }
    
    def _apply_confidence_modifier(self, advice):
        """Apply confidence modifier to advice tone."""
        # Confidence modifiers: hesitant, firm, pleading
        if self.confidence < 0.4:
            # Hesitant
            prefixes = ["Maybe... ", "I'm not sure, but ", "Perhaps "]
            advice["text"] = random.choice(prefixes) + advice["text"].lower()
        elif self.confidence > 0.8:
            # Firm
            suffixes = [" Do it now.", " Don't question this.", " I'm certain."]
            advice["text"] = advice["text"] + random.choice(suffixes)
        elif self.doubt > 0.6:
            # Pleading (high doubt can make AI plead)
            suffixes = [" Please.", " I need you to trust me.", " For both our sakes."]
            advice["text"] = advice["text"] + random.choice(suffixes)
        
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
