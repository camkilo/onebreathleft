"""
Renderer
Handles all game rendering with cinematic, psychological horror aesthetic
"""

import pygame
import math
import random
import time

class Renderer:
    """Renders the game with a cinematic, psychological horror aesthetic"""
    
    def __init__(self, screen, width, height):
        """Initialize renderer"""
        self.screen = screen
        self.width = width
        self.height = height
        
        # Fonts
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 36)
        
        # Near-black gradient colors (not pure black)
        self.color_bg_top = (8, 10, 12)  # Slightly blue-tinted near-black
        self.color_bg_bottom = (10, 12, 14)  # Slightly green-tinted near-black
        self.color_fog = (20, 22, 28)  # Near-black with blue tint
        
        # Player colors (for "Presence Core")
        self.color_player_core = (200, 210, 230)  # Bright center
        self.color_player_glow = (150, 170, 200)  # Soft glow
        
        # Enemy colors with subtle variations
        self.color_enemy_shadow = (70, 55, 85)
        self.color_enemy_whisper = (85, 65, 65)
        self.color_enemy_presence = (95, 45, 45)
        
        # UI colors with subtle tints
        self.color_text = (180, 185, 195)
        self.color_advice = (140, 165, 190)
        self.color_warning = (185, 95, 95)
        
        # Cinematic effects state
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.camera_shake_intensity = 0
        self.vignette_pulse = 0
        self.noise_offset_x = 0
        self.noise_offset_y = 0
        self.film_grain_alpha = 15  # 1-2% opacity
        
        # Enemy rendering state (for delayed rendering)
        self.enemy_render_buffer = []
        self.enemy_render_delay_frames = 0
        
        # Time tracking for animations
        self.time_accumulator = 0
        
        # Pre-generate noise pattern for film grain
        self.noise_surface = None
        self._generate_noise_pattern()
        
    def _generate_noise_pattern(self):
        """Generate film grain noise pattern"""
        self.noise_surface = pygame.Surface((self.width, self.height))
        self.noise_surface.set_alpha(self.film_grain_alpha)
        
        # Create noise pattern
        for x in range(0, self.width, 2):
            for y in range(0, self.height, 2):
                brightness = random.randint(0, 255)
                color = (brightness, brightness, brightness)
                pygame.draw.rect(self.noise_surface, color, (x, y, 2, 2))
    
    def render(self, game_state):
        """Render the current game state with cinematic effects"""
        self.time_accumulator += 0.016  # Approximate frame time
        
        # Update cinematic effects
        self._update_camera_effects(game_state)
        
        # Clear screen with gradient background (not pure black)
        self._render_gradient_background()
        
        # Add animated film grain
        self._render_film_grain()
        
        # Render world with enhanced fog
        self._render_fog(game_state)
        
        # Render exploration zones with light scars
        self._render_zones(game_state)
        
        # Render enemies with delayed rendering and instability
        self._render_enemies(game_state)
        
        # Render player as "Presence Core"
        self._render_player(game_state)
        
        # Render minimized UI (light-based indicators)
        self._render_minimal_ui(game_state)
        
        # Render AI advice
        self._render_advice(game_state)
        
        # Add pulsing vignette effect
        self._render_vignette(game_state)
        
        # Render ending if triggered
        if game_state.ending_triggered:
            self._render_ending(game_state)
    
    def _update_camera_effects(self, game_state):
        """Update cinematic camera effects"""
        player = game_state.player
        
        # Get boundary effects for zoom
        _, zoom_factor, _ = game_state.world.get_boundary_effect(player.x, player.y)
        
        # Camera drag (player slightly off-center based on movement)
        target_offset_x = -player.velocity_x * 0.05
        target_offset_y = -player.velocity_y * 0.05
        
        # Smooth camera movement
        self.camera_offset_x += (target_offset_x - self.camera_offset_x) * 0.1
        self.camera_offset_y += (target_offset_y - self.camera_offset_y) * 0.1
        
        # Camera shake when enemies are close
        self.camera_shake_intensity = 0
        for enemy in game_state.enemy_manager.enemies:
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < 100:
                self.camera_shake_intensity = max(self.camera_shake_intensity, 
                                                  (100 - distance) / 100 * 2)
        
        # Calculate vignette pulse based on danger, trust, and boundary proximity
        danger_level = min(player.fear / 100.0, 1.0)
        enemy_count = len(game_state.enemy_manager.enemies)
        boundary_effect = 1.0 - zoom_factor  # More vignette near boundaries
        
        base_pulse = danger_level * 0.3 + enemy_count * 0.05 + boundary_effect * 0.2
        
        # Pulse with breathing pattern
        pulse_wave = math.sin(self.time_accumulator * 2) * 0.5 + 0.5
        self.vignette_pulse = base_pulse + pulse_wave * 0.15
        
        # Update delayed enemy rendering based on tension
        tension = danger_level + game_state.world.hostility * 0.5
        if tension > 0.6:
            self.enemy_render_delay_frames = 2
        elif tension > 0.4:
            self.enemy_render_delay_frames = 1
        else:
            self.enemy_render_delay_frames = 0
    
    def _render_gradient_background(self):
        """Render near-black gradient background"""
        # Create vertical gradient from top to bottom
        for y in range(self.height):
            t = y / self.height
            r = int(self.color_bg_top[0] * (1-t) + self.color_bg_bottom[0] * t)
            g = int(self.color_bg_top[1] * (1-t) + self.color_bg_bottom[1] * t)
            b = int(self.color_bg_top[2] * (1-t) + self.color_bg_bottom[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
    
    def _render_film_grain(self):
        """Render animated film grain noise"""
        # Slightly shift noise pattern each frame for animation
        self.noise_offset_x = random.randint(-2, 2)
        self.noise_offset_y = random.randint(-2, 2)
        
        # Occasionally regenerate noise for more animation
        if random.random() < 0.1:
            self._generate_noise_pattern()
        
        self.screen.blit(self.noise_surface, (self.noise_offset_x, self.noise_offset_y))
    
    def _render_vignette(self, game_state):
        """Render pulsing vignette effect"""
        vignette_surface = pygame.Surface((self.width, self.height))
        vignette_surface.fill((0, 0, 0))
        
        # Create radial gradient for vignette
        center_x = self.width // 2
        center_y = self.height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        # Adjust vignette intensity based on pulse
        intensity = int(self.vignette_pulse * 180)
        
        vignette_surface.set_alpha(intensity)
        
        # Draw radial gradient
        for r in range(int(max_radius), 0, -20):
            alpha = int((1 - (r / max_radius)) * intensity)
            if alpha > 0:
                circle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, (0, 0, 0, alpha), 
                                 (center_x, center_y), r)
                self.screen.blit(circle_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            
    def _get_camera_position(self, world_x, world_y, player):
        """Convert world position to screen position with camera effects"""
        # Base screen position (player-centered)
        screen_x = self.width // 2 + (world_x - player.x)
        screen_y = self.height // 2 + (world_y - player.y)
        
        # Apply camera drag
        screen_x += self.camera_offset_x
        screen_y += self.camera_offset_y
        
        # Apply camera shake
        if self.camera_shake_intensity > 0:
            shake_x = random.uniform(-self.camera_shake_intensity, self.camera_shake_intensity)
            shake_y = random.uniform(-self.camera_shake_intensity, self.camera_shake_intensity)
            screen_x += shake_x
            screen_y += shake_y
        
        return int(screen_x), int(screen_y)
            
    def _render_fog(self, game_state):
        """Render atmospheric fog effect with dynamic lighting"""
        # Dynamic light radius based on game state
        base_visibility = game_state.world.get_visibility_radius(game_state.player.fear)
        
        # Shrink light when AI lies
        if hasattr(game_state, 'reality_system'):
            lie_factor = 1.0 - (game_state.reality_system.lie_count * 0.05)
            lie_factor = max(0.5, lie_factor)
            base_visibility *= lie_factor
        
        # Flicker when danger spikes
        danger_factor = 1.0
        if game_state.player.fear > 70:
            flicker = math.sin(self.time_accumulator * 10) * 0.1
            danger_factor = 1.0 + flicker
        
        # Expand briefly when making independent choices
        choice_bonus = 1.0
        if game_state.advice_ignored > 0 and self.time_accumulator % 5 < 0.5:
            choice_bonus = 1.15
        
        visibility = base_visibility * danger_factor * choice_bonus
        
        # Create fog overlay with dynamic density
        fog_surface = pygame.Surface((self.width, self.height))
        fog_surface.fill(self.color_fog)
        
        # Calculate fog alpha based on world state and trust
        darkness = int(200 * game_state.world.ambient_darkness)
        
        # Color temperature shift based on trust (warm = trust, cold = defiance)
        trust_shift = game_state.trust_level
        fog_r = int(self.color_fog[0] + (20 * trust_shift))
        fog_g = int(self.color_fog[1] + (15 * trust_shift))
        fog_b = int(self.color_fog[2] - (10 * trust_shift))
        fog_surface.fill((fog_r, fog_g, fog_b))
        
        fog_surface.set_alpha(darkness)
        self.screen.blit(fog_surface, (0, 0))
        
    def _render_zones(self, game_state):
        """Render exploration zones as light scars and floating geometry"""
        player = game_state.player
        
        for zone in game_state.world.zones:
            screen_x, screen_y = self._get_camera_position(zone["x"], zone["y"], player)
            
            # Only render if in visibility range
            visibility = game_state.world.get_visibility_radius(player.fear)
            dx = zone["x"] - player.x
            dy = zone["y"] - player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < visibility:
                alpha = int(255 * (1 - distance / visibility))
                if alpha > 0:
                    if zone["explored"]:
                        # Draw as fading light scar
                        color = (50, 55, 70, alpha)
                        self._draw_light_scar(screen_x, screen_y, zone["radius"], color)
                    else:
                        # Draw as broken grid lines that fade in/out
                        fade = (math.sin(self.time_accumulator * 2 + distance * 0.01) * 0.5 + 0.5)
                        color = (70, 75, 90, int(alpha * fade))
                        self._draw_broken_grid(screen_x, screen_y, zone["radius"], color)
                    
                    # Occasional vertical light streaks for depth
                    if random.random() < 0.05:
                        self._draw_light_streak(screen_x, screen_y, alpha)
    
    def _draw_light_scar(self, x, y, radius, color):
        """Draw a light scar (explored zone marker)"""
        scar_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(scar_surface, color, (radius, radius), radius, 2)
        # Add some inner glow
        pygame.draw.circle(scar_surface, (*color[:3], color[3] // 2), 
                          (radius, radius), radius - 5, 1)
        self.screen.blit(scar_surface, (x - radius, y - radius))
    
    def _draw_broken_grid(self, x, y, radius, color):
        """Draw broken grid lines"""
        # Draw segments of a grid, not complete
        for angle in range(0, 360, 45):
            if random.random() < 0.6:  # Not all segments drawn
                rad = math.radians(angle)
                start_x = x + math.cos(rad) * (radius - 10)
                start_y = y + math.sin(rad) * (radius - 10)
                end_x = x + math.cos(rad) * radius
                end_y = y + math.sin(rad) * radius
                
                line_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.line(line_surface, color, 
                               (int(start_x), int(start_y)), 
                               (int(end_x), int(end_y)), 1)
                self.screen.blit(line_surface, (0, 0))
    
    def _draw_light_streak(self, x, y, alpha):
        """Draw vertical light streak for depth illusion"""
        height = random.randint(30, 80)
        streak_surface = pygame.Surface((2, height), pygame.SRCALPHA)
        for i in range(height):
            fade = 1 - (i / height)
            color = (100, 110, 140, int(alpha * fade * 0.3))
            pygame.draw.line(streak_surface, color, (0, i), (2, i))
        self.screen.blit(streak_surface, (x - 1, y - height))
                    
    def _render_enemies(self, game_state):
        """Render abstract enemies with instability and delayed rendering"""
        player = game_state.player
        visibility = game_state.world.get_visibility_radius(player.fear)
        
        # Prepare current frame enemy data
        current_enemies = []
        for enemy in game_state.enemy_manager.enemies:
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < visibility:
                current_enemies.append({
                    'enemy': enemy,
                    'distance': distance,
                    'screen_pos': self._get_camera_position(enemy.x, enemy.y, player)
                })
        
        # Add to buffer for delayed rendering
        self.enemy_render_buffer.append(current_enemies)
        
        # Keep buffer size limited
        while len(self.enemy_render_buffer) > max(3, self.enemy_render_delay_frames + 1):
            self.enemy_render_buffer.pop(0)
        
        # Render from delayed buffer (if tension is high)
        if self.enemy_render_delay_frames > 0 and len(self.enemy_render_buffer) > self.enemy_render_delay_frames:
            render_data = self.enemy_render_buffer[-self.enemy_render_delay_frames - 1]
        else:
            render_data = current_enemies
        
        # Render each enemy with instability effects
        for data in render_data:
            enemy = data['enemy']
            distance = data['distance']
            screen_x, screen_y = data['screen_pos']
            
            # Choose color based on type with behavior-based rendering
            base_color = self._get_enemy_color(enemy)
            
            # Adjust color based on enemy state (aggression affects appearance)
            if enemy.alert:
                # More saturated and brighter when aggressive
                color = tuple(min(255, int(c * 1.2)) for c in base_color)
            else:
                # Dimmer when passive
                color = tuple(int(c * 0.8) for c in base_color)
            
            # Draw enemy with instability
            alpha = int(255 * (1 - distance / visibility) * 0.7)
            if alpha > 0:
                self._draw_unstable_enemy(screen_x, screen_y, enemy, color, alpha)
    
    def _get_enemy_color(self, enemy):
        """Get enemy color based on type"""
        if enemy.type == "shadow":
            return self.color_enemy_shadow
        elif enemy.type == "whisper":
            return self.color_enemy_whisper
        else:
            return self.color_enemy_presence
    
    def _draw_unstable_enemy(self, x, y, enemy, color, alpha):
        """Draw enemy with jitter, breathing, and vertex drift"""
        # Jitter (subtle random movement)
        jitter_x = random.uniform(-1.5, 1.5)
        jitter_y = random.uniform(-1.5, 1.5)
        x += jitter_x
        y += jitter_y
        
        # Breathing effect (size pulsing)
        breathe = math.sin(self.time_accumulator * 3 + id(enemy) % 10) * 0.1 + 1.0
        
        if enemy.alert:
            # Draw as aggressive triangle with vertex drift
            size = int(20 * breathe)
            
            # Base triangle points
            angle_offset = self.time_accumulator * 0.5  # Slow rotation
            points = []
            for i in range(3):
                angle = (i * 120 + angle_offset * 57.3) * (math.pi / 180)
                # Vertex drift
                drift_x = math.sin(self.time_accumulator * 2 + i) * 2
                drift_y = math.cos(self.time_accumulator * 1.5 + i) * 2
                
                px = x + math.cos(angle) * size + drift_x
                py = y + math.sin(angle) * size + drift_y
                points.append((int(px), int(py)))
            
            # Draw with alpha
            enemy_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            offset = size * 1.5
            adjusted_points = [(p[0] - x + offset, p[1] - y + offset) for p in points]
            pygame.draw.polygon(enemy_surface, (*color, alpha), adjusted_points)
            
            # Add sharp edges for aggression (behavior-based rendering)
            if enemy.aggression > 0.7:
                pygame.draw.polygon(enemy_surface, (*color, alpha // 2), adjusted_points, 2)
            
            self.screen.blit(enemy_surface, (x - offset, y - offset))
        else:
            # Draw as circle with rounded edges (fear/confusion)
            size = int(15 * breathe)
            
            # Behavior-based rendering: round edges when not aggressive
            enemy_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            offset = size * 1.5
            pygame.draw.circle(enemy_surface, (*color, alpha), 
                             (int(offset), int(offset)), size)
            
            # Add soft glow
            for i in range(3):
                glow_size = size + i * 3
                glow_alpha = alpha // (4 + i * 2)
                pygame.draw.circle(enemy_surface, (*color, glow_alpha), 
                                 (int(offset), int(offset)), glow_size, 1)
            
            self.screen.blit(enemy_surface, (x - offset, y - offset))
                        
    def _render_player(self, game_state):
        """Render player as 'Presence Core' with soft glow and effects"""
        player = game_state.player
        center_x = self.width // 2 + int(self.camera_offset_x)
        center_y = self.height // 2 + int(self.camera_offset_y)
        
        # Calculate movement speed for chromatic aberration
        speed = math.sqrt(player.velocity_x**2 + player.velocity_y**2)
        fast_movement = speed > 150
        
        # Micro-pulse synced to danger and AI speech
        danger_pulse = game_state.player.fear / 100.0
        ai_speaking = game_state.ai_companion.current_advice is not None
        
        pulse_base = 1.0
        if ai_speaking:
            pulse_base = 1.0 + math.sin(self.time_accumulator * 8) * 0.15
        elif danger_pulse > 0.5:
            pulse_base = 1.0 + math.sin(self.time_accumulator * 6) * danger_pulse * 0.1
        
        base_size = int(8 * pulse_base)
        
        # Create surface for glow effects
        glow_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        glow_center = 50
        
        # Chromatic aberration when moving fast
        if fast_movement:
            direction = math.atan2(player.velocity_y, player.velocity_x)
            offset = 3
            
            # Red channel slightly behind movement
            r_x = glow_center - math.cos(direction) * offset
            r_y = glow_center - math.sin(direction) * offset
            pygame.draw.circle(glow_surface, (255, 100, 100, 100), 
                             (int(r_x), int(r_y)), base_size + 2)
            
            # Blue channel slightly ahead
            b_x = glow_center + math.cos(direction) * offset
            b_y = glow_center + math.sin(direction) * offset
            pygame.draw.circle(glow_surface, (100, 100, 255, 100), 
                             (int(b_x), int(b_y)), base_size + 2)
        
        # Outer glow rings with falloff
        for i in range(5, 0, -1):
            glow_size = base_size + i * 4
            glow_alpha = int(120 / (i + 1))
            pygame.draw.circle(glow_surface, (*self.color_player_glow, glow_alpha), 
                             (glow_center, glow_center), glow_size)
        
        # Core circle (bright center)
        pygame.draw.circle(glow_surface, (*self.color_player_core, 255), 
                         (glow_center, glow_center), base_size)
        
        # Inner glow
        pygame.draw.circle(glow_surface, (*self.color_player_core, 200), 
                         (glow_center, glow_center), base_size + 2)
        
        # Blit to screen
        self.screen.blit(glow_surface, (center_x - glow_center, center_y - glow_center))
        
        # Draw direction indicator if moving (subtle energy trail)
        if player.velocity_x != 0 or player.velocity_y != 0:
            angle = math.atan2(player.velocity_y, player.velocity_x)
            
            # Draw energy trail
            for i in range(3):
                trail_len = 15 + i * 5
                trail_alpha = 150 - i * 50
                end_x = center_x + math.cos(angle) * trail_len
                end_y = center_y + math.sin(angle) * trail_len
                
                trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.line(trail_surface, (*self.color_player_glow, trail_alpha),
                               (center_x, center_y), 
                               (int(end_x), int(end_y)), 2)
                self.screen.blit(trail_surface, (0, 0))
            
    def _render_minimal_ui(self, game_state):
        """Render minimized UI - felt, not shown"""
        player = game_state.player
        
        # Only show essential control hints at bottom
        hint_text = self.font_small.render("WASD: Move | Shift: Run | Y: Follow | N: Ignore", 
                                          True, (90, 95, 110))
        hint_rect = hint_text.get_rect(center=(self.width // 2, self.height - 15))
        self.screen.blit(hint_text, hint_rect)
        
        # Subtle indicators in corners (very minimal)
        # Top left: Light intensity indicator (represents health indirectly)
        light_intensity = player.health / player.max_health
        light_size = int(20 + light_intensity * 10)
        light_alpha = int(150 * light_intensity)
        
        light_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        for i in range(3, 0, -1):
            size = light_size - i * 3
            alpha = light_alpha // i
            pygame.draw.circle(light_surface, (200, 210, 220, alpha), (30, 30), size)
        self.screen.blit(light_surface, (10, 10))
        
        # Top right: Trust level shown via color temperature
        # (Warm = trust, Cold = defiance) - very subtle
        trust = game_state.trust_level
        if trust > 0.6:
            trust_color = (180, 140, 100, 100)  # Warm
            trust_text = "Aligned"
        elif trust < 0.4:
            trust_color = (100, 140, 180, 100)  # Cold
            trust_text = "Independent"
        else:
            trust_color = (140, 140, 140, 100)  # Neutral
            trust_text = "Uncertain"
        
        trust_indicator = self.font_small.render(trust_text, True, trust_color[:3])
        self.screen.blit(trust_indicator, (self.width - 90, 15))
        
    def _render_advice(self, game_state):
        """Render AI companion advice"""
        advice = game_state.ai_companion.get_current_advice()
        
        if advice:
            # Create semi-transparent box for advice
            box_width = 600
            box_height = 80
            box_x = (self.width - box_width) // 2
            box_y = self.height - 120
            
            # Background
            advice_surface = pygame.Surface((box_width, box_height))
            advice_surface.fill((20, 25, 35))
            advice_surface.set_alpha(220)
            self.screen.blit(advice_surface, (box_x, box_y))
            
            # Border
            pygame.draw.rect(self.screen, self.color_advice, 
                           (box_x, box_y, box_width, box_height), 2)
            
            # Advice text
            lines = self._wrap_text(advice, box_width - 20)
            y_offset = box_y + 10
            for line in lines:
                text_surface = self.font_medium.render(line, True, self.color_advice)
                self.screen.blit(text_surface, (box_x + 10, y_offset))
                y_offset += 25
                
            # Response hint
            hint = self.font_small.render("(Y to follow / N to ignore)", 
                                         True, (120, 140, 160))
            self.screen.blit(hint, (box_x + 10, box_y + box_height - 22))
            
    def _render_ending(self, game_state):
        """Render ending screen"""
        # Dark overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # Ending text based on type
        endings = {
            "death": "You took your last breath.",
            "trust": "You became one with the voice.",
            "defiance": "You broke free, but at what cost?",
            "balance": "You found your own path.",
            "transcendence": "You understood the cycle."
        }
        
        ending_text = endings.get(game_state.ending_type, "The end.")
        
        # Main ending text
        text_surface = self.font_large.render(ending_text, True, self.color_text)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 - 40))
        self.screen.blit(text_surface, text_rect)
        
        # Stats
        stats = [
            f"Time survived: {int(game_state.game_time)}s",
            f"Trust level: {int(game_state.trust_level * 100)}%",
            f"Zones explored: {game_state.player.zones_explored}",
            f"Advice followed: {game_state.advice_followed}",
            f"Advice ignored: {game_state.advice_ignored}"
        ]
        
        y_offset = self.height // 2 + 20
        for stat in stats:
            stat_surface = self.font_small.render(stat, True, (150, 150, 160))
            stat_rect = stat_surface.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(stat_surface, stat_rect)
            y_offset += 25
            
        # Continue hint
        hint_surface = self.font_small.render(
            "Your choices will guide the next traveler...", 
            True, (120, 120, 140)
        )
        hint_rect = hint_surface.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(hint_surface, hint_rect)
        
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_surface = self.font_medium.render(test_line, True, (255, 255, 255))
            
            if text_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
