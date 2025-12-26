"""
Reality Degradation System
The environment responds to player trust levels and AI behavior.
Reality becomes unstable when trust breaks down or AI lies.
"""

import math
import random


# Reality degradation constants
LIE_PENALTY_PER_LIE = 0.05  # Stability reduction per AI lie
MAX_LIE_PENALTY = 0.5  # Maximum total lie penalty
DISOBEDIENCE_TIME_DIVISOR = 60.0  # Time in seconds for full disobedience penalty
MAX_DISOBEDIENCE_PENALTY = 0.3  # Maximum disobedience penalty
TRUST_BREAKDOWN_TIME_DIVISOR = 120.0  # Time for full breakdown penalty
MAX_BREAKDOWN_PENALTY = 0.4  # Maximum breakdown penalty


class RealitySystem:
    """
    Manages reality stability and environmental degradation.
    
    This system tracks and responds to player behavior and AI interactions,
    degrading the game world's stability when trust breaks down or deception
    occurs. The degradation is subtle and affects multiple aspects:
    
    - Visual stability: Fog density, geometry warping, color shifts
    - Audio stability: Audio desync and distortion
    - Navigation stability: Movement reliability and drift
    
    The system uses three component stability values that feed into various
    game systems. All effects are designed to be felt by the player without
    explicit UI indicators.
    
    Attributes:
        stability: Overall reality stability (0-1)
        visual_stability: Visual rendering stability (0-1)
        audio_stability: Audio playback stability (0-1)
        navigation_stability: Movement reliability (0-1)
        lie_count: Number of times AI has lied
        disobedience_count: Duration of player disobedience
        trust_breakdown_duration: Time spent in low trust state
    
    Methods:
        update: Update stability based on game state
        apply_fog_density_modifier: Modify fog based on stability
        apply_geometry_warp: Apply visual warping to coordinates
        apply_movement_unreliability: Add drift to player movement
    """
    
    def __init__(self):
        """Initialize reality system"""
        # Core stability value (0 = completely degraded, 1 = stable)
        self.stability = 1.0
        
        # Component stability values
        self.visual_stability = 1.0    # Affects fog, geometry
        self.audio_stability = 1.0     # Would affect audio timing/pitch
        self.navigation_stability = 1.0  # Affects movement/path reliability
        
        # Degradation factors
        self.lie_count = 0  # How many times AI has lied
        self.disobedience_count = 0  # Times player ignored advice
        self.trust_breakdown_duration = 0  # Time spent in low trust
        
        # Geometry warping
        self.warp_intensity = 0.0
        self.warp_frequency = 0.0
        
        # Visual effects
        self.fog_distortion = 0.0
        self.color_shift = 0.0
        
    def update(self, dt, game_state):
        """
        Update reality stability based on game state.
        
        Args:
            dt: Delta time
            game_state: Current game state
        """
        behavior = game_state.behavior_state
        ai = game_state.ai_companion
        
        # Track lie detection
        if ai.current_advice and ai.current_advice.get('is_lie', False):
            self.lie_count += 1
        
        # Track disobedience streak
        if behavior.advice_given_count > 0:
            recent_ignore_ratio = behavior.advice_ignored_count / behavior.advice_given_count
            if recent_ignore_ratio > 0.6:
                self.disobedience_count += dt
        
        # Track time in low trust state
        if game_state.trust_level < 0.3:
            self.trust_breakdown_duration += dt
        else:
            # Recovery when trust improves
            self.trust_breakdown_duration = max(0, self.trust_breakdown_duration - dt * 0.5)
        
        # Calculate stability from factors
        self._calculate_stability(game_state)
        
        # Update component stabilities
        self._update_visual_stability(dt, game_state)
        self._update_audio_stability(dt)
        self._update_navigation_stability(dt)
        
        # Update degradation effects
        self._update_degradation_effects(dt)
    
    def _calculate_stability(self, game_state):
        """Calculate overall reality stability."""
        # Base stability from trust level
        trust_factor = game_state.trust_level
        
        # Penalty from lies (each lie reduces stability)
        lie_penalty = min(MAX_LIE_PENALTY, self.lie_count * LIE_PENALTY_PER_LIE)
        
        # Penalty from sustained disobedience
        disobedience_penalty = min(MAX_DISOBEDIENCE_PENALTY, 
                                   self.disobedience_count / DISOBEDIENCE_TIME_DIVISOR)
        
        # Penalty from prolonged low trust
        breakdown_penalty = min(MAX_BREAKDOWN_PENALTY, 
                               self.trust_breakdown_duration / TRUST_BREAKDOWN_TIME_DIVISOR)
        
        # Calculate stability (0-1)
        self.stability = max(0.0, min(1.0,
            trust_factor - lie_penalty - disobedience_penalty - breakdown_penalty
        ))
    
    def _update_visual_stability(self, dt, game_state):
        """Update visual stability (affects fog and geometry)."""
        target_visual = self.stability
        
        # When AI lies, visual stability drops sharply
        if game_state.ai_companion.current_advice:
            if game_state.ai_companion.current_advice.get('is_lie', False):
                target_visual *= 0.6
        
        # Smooth transition
        self.visual_stability += (target_visual - self.visual_stability) * dt * 0.3
        
        # Update fog distortion (high when stability is low)
        self.fog_distortion = 1.0 - self.visual_stability
        
        # Update geometry warp
        self.warp_intensity = (1.0 - self.visual_stability) * 0.3
        self.warp_frequency = (1.0 - self.visual_stability) * 2.0
    
    def _update_audio_stability(self, dt):
        """Update audio stability (would affect audio timing/pitch)."""
        target_audio = self.stability
        
        # Audio degrades faster with repeated disobedience
        if self.disobedience_count > 10:
            target_audio *= 0.7
        
        # Smooth transition
        self.audio_stability += (target_audio - self.audio_stability) * dt * 0.2
    
    def _update_navigation_stability(self, dt):
        """Update navigation stability (affects movement)."""
        target_nav = self.stability
        
        # Navigation becomes unreliable in unstable reality
        if self.stability < 0.5:
            target_nav *= 0.8
        
        # Smooth transition
        self.navigation_stability += (target_nav - self.navigation_stability) * dt * 0.25
    
    def _update_degradation_effects(self, dt):
        """Update visual degradation effects."""
        # Color shift increases as reality degrades
        self.color_shift = (1.0 - self.stability) * 0.2
    
    def apply_fog_density_modifier(self, base_fog):
        """
        Apply reality-based modification to fog density.
        
        Args:
            base_fog: Base fog density
            
        Returns:
            Modified fog density
        """
        # Low stability = more fog + distortion
        stability_modifier = 1.0 + (1.0 - self.visual_stability) * 0.5
        distortion = self.fog_distortion * 0.2
        
        return base_fog * stability_modifier + distortion
    
    def apply_geometry_warp(self, x, y, time):
        """
        Apply reality warping to geometry coordinates.
        When reality is unstable, positions subtly shift.
        
        Args:
            x, y: Original coordinates
            time: Current game time
            
        Returns:
            Warped (x, y) coordinates
        """
        if self.warp_intensity < 0.01:
            return x, y
        
        # Sine wave distortion
        warp_x = math.sin(time * self.warp_frequency + y * 0.01) * self.warp_intensity * 10
        warp_y = math.cos(time * self.warp_frequency + x * 0.01) * self.warp_intensity * 10
        
        return x + warp_x, y + warp_y
    
    def apply_movement_unreliability(self, velocity_x, velocity_y):
        """
        Apply navigation instability to player movement.
        Low stability = slight drift in movement.
        
        Args:
            velocity_x, velocity_y: Intended velocity
            
        Returns:
            Modified velocity with drift
        """
        if self.navigation_stability > 0.9:
            return velocity_x, velocity_y
        
        # Add random drift inversely proportional to stability
        drift_amount = (1.0 - self.navigation_stability) * 20
        drift_x = random.uniform(-drift_amount, drift_amount)
        drift_y = random.uniform(-drift_amount, drift_amount)
        
        return velocity_x + drift_x, velocity_y + drift_y
    
    def get_audio_desync(self):
        """
        Get audio desynchronization amount.
        Returns delay in seconds for audio playback.
        """
        # More desync when audio stability is low
        max_desync = 0.5  # seconds
        return (1.0 - self.audio_stability) * max_desync
    
    def get_color_shift_values(self):
        """
        Get RGB color shift values for rendering.
        Returns tuple of (r_shift, g_shift, b_shift) in range 0-1.
        """
        # Shift toward red/orange when reality degrades (unsettling)
        r_shift = self.color_shift * 0.3
        g_shift = -self.color_shift * 0.1
        b_shift = -self.color_shift * 0.2
        
        return r_shift, g_shift, b_shift
    
    def should_glitch(self, dt):
        """
        Determine if a visual glitch should occur this frame.
        Returns True randomly based on instability.
        """
        glitch_probability = (1.0 - self.stability) * 0.1 * dt
        return random.random() < glitch_probability
    
    def get_state_dict(self):
        """Get current reality state as dictionary."""
        return {
            'stability': self.stability,
            'visual_stability': self.visual_stability,
            'audio_stability': self.audio_stability,
            'navigation_stability': self.navigation_stability,
            'lie_count': self.lie_count,
            'disobedience_count': self.disobedience_count,
            'trust_breakdown_duration': self.trust_breakdown_duration,
            'warp_intensity': self.warp_intensity,
            'fog_distortion': self.fog_distortion
        }
