"""
Player Behavior Profiler
Tracks how the player behaves in real-time, not just what they do.
This feeds into all other adaptive systems.
"""

import time
from collections import deque
import math


class BehaviorState:
    """
    Live model tracking player behavior patterns.
    Updated every frame with sliding window averages.
    """
    
    def __init__(self, window_size=60):
        """
        Initialize behavior state tracker.
        
        Args:
            window_size: Time window in seconds for averaging (default 60)
        """
        self.window_size = window_size
        
        # Core output values (0-1 normalized)
        self.trust = 0.5  # Trust in AI companion
        self.fear = 0.0  # Fear/anxiety level
        self.independence = 0.5  # Independent decision making
        
        # Reaction time tracking
        self.advice_timestamps = deque(maxlen=100)  # When advice was given
        self.response_timestamps = deque(maxlen=100)  # When player responded
        self.reaction_times = deque(maxlen=20)  # Last 20 reaction times
        self.average_reaction_time = 5.0  # seconds
        
        # Advice tracking
        self.advice_given_count = 0
        self.advice_followed_count = 0
        self.advice_ignored_count = 0
        self.advice_follow_ratio = 0.5  # % followed (0-1)
        
        # Movement behavior tracking
        self.position_history = deque(maxlen=300)  # 5 seconds at 60fps
        self.velocity_history = deque(maxlen=300)
        self.stop_events = deque(maxlen=50)  # Micro-stops detected
        self.backtrack_events = deque(maxlen=50)  # Direction reversals
        self.hesitation_score = 0.0  # 0-1, higher = more hesitant
        
        # Risk tolerance tracking
        self.enemy_proximity_samples = deque(maxlen=600)  # 10 seconds
        self.sprint_usage_samples = deque(maxlen=600)
        self.risk_tolerance = 0.5  # 0-1, higher = more risk-taking
        
        # Time tracking
        self.last_update_time = time.time()
        self.current_time = 0
        
        # Pending advice (waiting for response)
        self.pending_advice_time = None
        
    def update(self, dt, player, enemy_manager, current_game_time):
        """
        Update behavior state with current frame data.
        
        Args:
            dt: Delta time since last frame
            player: Player object
            enemy_manager: EnemyManager object
            current_game_time: Current game time in seconds
        """
        self.current_time = current_game_time
        
        # Update position and velocity history
        self._track_movement(player, dt)
        
        # Update risk tolerance
        self._track_risk_behavior(player, enemy_manager, dt)
        
        # Calculate derived values
        self._calculate_hesitation()
        self._calculate_independence()
        
        # Update trust based on advice follow ratio
        if self.advice_given_count > 0:
            self.advice_follow_ratio = self.advice_followed_count / self.advice_given_count
            # Trust slowly converges toward follow ratio
            self.trust += (self.advice_follow_ratio - self.trust) * dt * 0.1
        
        # Update fear from player's fear stat
        self.fear = player.fear / 100.0
        
    def _track_movement(self, player, dt):
        """Track player movement patterns to detect hesitation."""
        # Record current position and velocity
        pos = (player.x, player.y)
        vel = (player.velocity_x, player.velocity_y)
        
        self.position_history.append((self.current_time, pos))
        self.velocity_history.append((self.current_time, vel))
        
        # Detect micro-stops (velocity drops to near zero briefly)
        if len(self.velocity_history) >= 3:
            recent_vels = list(self.velocity_history)[-3:]
            speeds = [math.sqrt(v[1][0]**2 + v[1][1]**2) for v in recent_vels]
            
            # If speed dropped significantly and then recovered
            if speeds[1] < 20 and speeds[0] > 50 and speeds[2] > 50:
                self.stop_events.append(self.current_time)
        
        # Detect backtracking (significant direction changes)
        if len(self.velocity_history) >= 30:
            old_vel = self.velocity_history[-30][1]
            new_vel = vel
            
            # Calculate direction change
            old_mag = math.sqrt(old_vel[0]**2 + old_vel[1]**2)
            new_mag = math.sqrt(new_vel[0]**2 + new_vel[1]**2)
            
            if old_mag > 10 and new_mag > 10:
                # Normalize and compute dot product
                old_dir = (old_vel[0] / old_mag, old_vel[1] / old_mag)
                new_dir = (new_vel[0] / new_mag, new_vel[1] / new_mag)
                dot_product = old_dir[0] * new_dir[0] + old_dir[1] * new_dir[1]
                
                # If moving in opposite direction (dot product < -0.5)
                if dot_product < -0.5:
                    self.backtrack_events.append(self.current_time)
    
    def _track_risk_behavior(self, player, enemy_manager, dt):
        """Track risk-taking behavior with enemies."""
        # Find closest enemy
        min_distance = float('inf')
        for enemy in enemy_manager.enemies:
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            distance = math.sqrt(dx*dx + dy*dy)
            min_distance = min(min_distance, distance)
        
        # Normalize distance (0 = very close, 1 = far away)
        if min_distance != float('inf'):
            normalized_distance = min(1.0, min_distance / 300.0)
            proximity = 1.0 - normalized_distance  # Invert: 1 = close, 0 = far
        else:
            proximity = 0.0
        
        self.enemy_proximity_samples.append((self.current_time, proximity))
        
        # Track if player is sprinting
        is_sprinting = 1.0 if player.is_running else 0.0
        self.sprint_usage_samples.append((self.current_time, is_sprinting))
        
        # Calculate risk tolerance from recent samples
        cutoff_time = self.current_time - self.window_size
        
        # Risk tolerance: high proximity while sprinting = high risk
        recent_proximity = [p for t, p in self.enemy_proximity_samples if t > cutoff_time]
        recent_sprinting = [s for t, s in self.sprint_usage_samples if t > cutoff_time]
        
        if recent_proximity and recent_sprinting:
            avg_proximity = sum(recent_proximity) / len(recent_proximity)
            avg_sprinting = sum(recent_sprinting) / len(recent_sprinting)
            
            # Risk = being close to enemies + sprinting often
            self.risk_tolerance = (avg_proximity * 0.5 + avg_sprinting * 0.5)
    
    def _calculate_hesitation(self):
        """Calculate hesitation score from movement patterns."""
        cutoff_time = self.current_time - self.window_size
        
        # Count recent stops and backtracks
        recent_stops = sum(1 for t in self.stop_events if t > cutoff_time)
        recent_backtracks = sum(1 for t in self.backtrack_events if t > cutoff_time)
        
        # Normalize to 0-1 range (assume max 20 events per window is very hesitant)
        stop_score = min(1.0, recent_stops / 20.0)
        backtrack_score = min(1.0, recent_backtracks / 20.0)
        
        # Combined hesitation score
        self.hesitation_score = (stop_score * 0.5 + backtrack_score * 0.5)
    
    def _calculate_independence(self):
        """Calculate independence score from behavior patterns."""
        # Independence = low hesitation + risk tolerance + ignoring advice
        ignore_ratio = 1.0 - self.advice_follow_ratio if self.advice_given_count > 0 else 0.5
        confidence = 1.0 - self.hesitation_score
        
        # Weighted combination
        self.independence = (
            ignore_ratio * 0.4 +
            confidence * 0.3 +
            self.risk_tolerance * 0.3
        )
    
    def on_advice_given(self, game_time):
        """Record when advice is given to player."""
        self.advice_given_count += 1
        self.advice_timestamps.append(game_time)
        self.pending_advice_time = game_time
    
    def on_advice_followed(self, game_time):
        """Record when player follows advice."""
        self.advice_followed_count += 1
        self.response_timestamps.append(game_time)
        
        # Calculate reaction time if there was pending advice
        if self.pending_advice_time is not None:
            reaction_time = game_time - self.pending_advice_time
            self.reaction_times.append(reaction_time)
            
            # Update average reaction time
            if self.reaction_times:
                self.average_reaction_time = sum(self.reaction_times) / len(self.reaction_times)
            
            self.pending_advice_time = None
    
    def on_advice_ignored(self, game_time):
        """Record when player ignores advice."""
        self.advice_ignored_count += 1
        self.response_timestamps.append(game_time)
        
        # Calculate reaction time if there was pending advice
        if self.pending_advice_time is not None:
            reaction_time = game_time - self.pending_advice_time
            self.reaction_times.append(reaction_time)
            
            # Update average reaction time
            if self.reaction_times:
                self.average_reaction_time = sum(self.reaction_times) / len(self.reaction_times)
            
            self.pending_advice_time = None
    
    def get_state_dict(self):
        """Get current behavior state as dictionary for serialization."""
        return {
            'trust': self.trust,
            'fear': self.fear,
            'independence': self.independence,
            'average_reaction_time': self.average_reaction_time,
            'advice_follow_ratio': self.advice_follow_ratio,
            'hesitation_score': self.hesitation_score,
            'risk_tolerance': self.risk_tolerance,
            'advice_given_count': self.advice_given_count,
            'advice_followed_count': self.advice_followed_count,
            'advice_ignored_count': self.advice_ignored_count
        }
