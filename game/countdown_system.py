"""
Lying Countdown System
AI announces something is coming, timer appears/disappears.
Sometimes nothing happens, sometimes everything does.
Uncertainty creates instant engagement.
"""

import random


# Event spawn weights
SPAWN_WEIGHT = 0.6
CORRUPTION_WEIGHT = 0.3
BLESSING_WEIGHT = 0.1


class Countdown:
    """A single countdown event"""
    
    def __init__(self, duration, event_type, will_trigger):
        self.duration = duration
        self.time_remaining = duration
        self.event_type = event_type  # 'spawn', 'corruption', 'blessing', 'nothing'
        self.will_trigger = will_trigger  # Will this countdown actually trigger?
        self.active = True
        self.triggered = False
        
        # Countdown display behavior
        self.visible = True
        self.flicker_timer = 0
        self.should_disappear = random.random() < 0.3  # 30% chance to disappear
        self.disappeared_at = None
        
    def update(self, dt):
        """Update countdown"""
        if not self.active:
            return False
        
        self.time_remaining -= dt
        
        # Countdown might disappear before finishing
        if self.should_disappear and not self.disappeared_at:
            if self.time_remaining < self.duration * 0.4:
                self.disappeared_at = self.time_remaining
                self.visible = False
        
        # Flicker effect near end
        if self.time_remaining < 3.0:
            self.flicker_timer += dt
            if self.flicker_timer > 0.2:
                self.visible = not self.visible
                self.flicker_timer = 0
        
        # Trigger or expire
        if self.time_remaining <= 0:
            self.active = False
            if self.will_trigger:
                self.triggered = True
                return True
        
        return False


class CountdownSystem:
    """
    Manages AI countdown announcements.
    Creates tension through uncertainty.
    """
    
    def __init__(self):
        self.active_countdowns = []
        self.spawn_timer = 0
        self.spawn_interval = 25.0  # New countdown every ~25 seconds
        
        # Track lies for AI personality
        self.total_countdowns = 0
        self.false_countdowns = 0
        self.lie_ratio = 0.4  # 40% of countdowns are lies
        
    def update(self, dt, game_state):
        """Update countdown system"""
        self.spawn_timer += dt
        
        # Spawn new countdowns periodically
        if self.spawn_timer >= self.spawn_interval:
            # Only after 20 seconds of gameplay
            if game_state.game_time > 20:
                self._create_countdown(game_state)
                self.spawn_timer = 0
        
        # Update active countdowns
        countdowns_to_remove = []
        for countdown in self.active_countdowns:
            triggered = countdown.update(dt)
            
            if triggered:
                # Execute countdown effect
                self._execute_countdown_event(countdown, game_state)
            
            if not countdown.active:
                countdowns_to_remove.append(countdown)
        
        for countdown in countdowns_to_remove:
            self.active_countdowns.remove(countdown)
    
    def _create_countdown(self, game_state):
        """Create a new countdown"""
        # Decide if this countdown will actually trigger
        will_trigger = random.random() > self.lie_ratio
        
        # Choose event type
        if will_trigger:
            event_types = ['spawn', 'corruption', 'blessing']
            # Weight spawn higher when pressure is high
            if hasattr(game_state, 'pressure_system'):
                pressure = game_state.pressure_system.pressure_score
                if pressure > 0.7:
                    event_type = random.choices(
                        event_types,
                        weights=[SPAWN_WEIGHT, CORRUPTION_WEIGHT, BLESSING_WEIGHT]
                    )[0]
                else:
                    event_type = random.choice(event_types)
            else:
                event_type = random.choice(event_types)
        else:
            event_type = 'nothing'
        
        # Duration varies
        duration = random.uniform(5.0, 12.0)
        
        countdown = Countdown(duration, event_type, will_trigger)
        self.active_countdowns.append(countdown)
        
        self.total_countdowns += 1
        if not will_trigger:
            self.false_countdowns += 1
        
        # AI announces countdown
        self._announce_countdown(game_state, countdown)
    
    def _announce_countdown(self, game_state, countdown):
        """AI announces the countdown"""
        ai = game_state.ai_companion
        
        announcements = {
            'spawn': [
                "Something's coming. I can feel it.",
                "They're gathering. Get ready.",
                "Prepare yourself. They're almost here.",
                "I sense movement. Incoming.",
            ],
            'corruption': [
                "The world is shifting. Brace yourself.",
                "Reality is tearing. Find shelter.",
                "Something's wrong with the space around you.",
                "The corruption is spreading. Move.",
            ],
            'blessing': [
                "Wait... this might help you.",
                "Something's different. This could be good.",
                "A rare moment of clarity is coming.",
                "For once, the world might be kind.",
            ],
            'nothing': [
                "Something's coming. I think.",
                "I'm not sure, but... be careful.",
                "Maybe something. Maybe nothing. Watch out.",
                "I might be wrong, but... prepare.",
            ]
        }
        
        announcement = random.choice(announcements[countdown.event_type])
        
        # Override AI's current advice with countdown announcement
        if ai:
            ai.current_advice = {
                'text': announcement,
                'type': 'countdown',
                'is_lie': not countdown.will_trigger
            }
    
    def _execute_countdown_event(self, countdown, game_state):
        """Execute the countdown event"""
        if countdown.event_type == 'spawn':
            # Spawn multiple threats
            self._spawn_threat_wave(game_state)
            
        elif countdown.event_type == 'corruption':
            # Create corruption fields
            self._spawn_corruption_wave(game_state)
            
        elif countdown.event_type == 'blessing':
            # Give player a temporary benefit
            self._grant_blessing(game_state)
        
        # 'nothing' does nothing (the lie)
    
    def _spawn_threat_wave(self, game_state):
        """Spawn a wave of threats"""
        if hasattr(game_state, 'threat_manager'):
            threat_manager = game_state.threat_manager
            player = game_state.player
            
            # Spawn 2-3 hunters
            for _ in range(random.randint(2, 3)):
                threat_manager._spawn_hunter(player)
            
            # Spawn 1-2 watchers
            for _ in range(random.randint(1, 2)):
                threat_manager._spawn_watcher(player)
    
    def _spawn_corruption_wave(self, game_state):
        """Spawn corruption fields"""
        if hasattr(game_state, 'threat_manager'):
            threat_manager = game_state.threat_manager
            player = game_state.player
            
            # Spawn 1-2 corruption fields
            for _ in range(random.randint(1, 2)):
                threat_manager._spawn_corruption_field(player)
    
    def _grant_blessing(self, game_state):
        """Grant temporary benefit"""
        player = game_state.player
        
        # Choose random blessing
        blessing_type = random.choice([
            'health',
            'stamina',
            'fear_reduce',
            'speed_boost'
        ])
        
        if blessing_type == 'health':
            player.health = min(player.max_health, player.health + 30)
        elif blessing_type == 'stamina':
            player.stamina = player.max_stamina
        elif blessing_type == 'fear_reduce':
            player.decrease_fear(40)
        elif blessing_type == 'speed_boost':
            # Would need to implement temporary speed boost
            # For now, just give stamina
            player.stamina = player.max_stamina
    
    def get_visible_countdowns(self):
        """Get all visible countdowns for display"""
        visible = []
        for countdown in self.active_countdowns:
            if countdown.visible:
                visible.append({
                    'time_remaining': countdown.time_remaining,
                    'duration': countdown.duration,
                    'event_type': countdown.event_type
                })
        return visible
    
    def get_lie_statistics(self):
        """Get statistics about countdown lies"""
        if self.total_countdowns == 0:
            return {'lie_ratio': 0.0, 'total': 0, 'lies': 0}
        
        return {
            'lie_ratio': self.false_countdowns / self.total_countdowns,
            'total': self.total_countdowns,
            'lies': self.false_countdowns
        }
