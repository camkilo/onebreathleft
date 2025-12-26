"""
Renderer
Handles all game rendering with foggy, minimal aesthetic
"""

import pygame
import math

class Renderer:
    """Renders the game with a foggy, psychological horror aesthetic"""
    
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
        
        # Colors
        self.color_bg = (15, 15, 20)
        self.color_fog = (30, 30, 40)
        self.color_player = (180, 180, 200)
        self.color_enemy_shadow = (80, 60, 90)
        self.color_enemy_whisper = (90, 70, 70)
        self.color_enemy_presence = (100, 50, 50)
        self.color_text = (200, 200, 210)
        self.color_advice = (150, 180, 200)
        self.color_warning = (200, 100, 100)
        
    def render(self, game_state):
        """Render the current game state"""
        # Clear screen with dark background
        self.screen.fill(self.color_bg)
        
        # Render world with fog
        self._render_fog(game_state)
        
        # Render exploration zones
        self._render_zones(game_state)
        
        # Render enemies
        self._render_enemies(game_state)
        
        # Render player
        self._render_player(game_state)
        
        # Render UI
        self._render_ui(game_state)
        
        # Render AI advice
        self._render_advice(game_state)
        
        # Render ending if triggered
        if game_state.ending_triggered:
            self._render_ending(game_state)
            
    def _render_fog(self, game_state):
        """Render atmospheric fog effect"""
        visibility = game_state.world.get_visibility_radius(game_state.player.fear)
        
        # Create fog overlay
        fog_surface = pygame.Surface((self.width, self.height))
        fog_surface.fill(self.color_fog)
        
        # Calculate fog alpha based on distance from player
        player_screen_x = self.width // 2
        player_screen_y = self.height // 2
        
        # Apply darkness based on world state
        darkness = int(255 * game_state.world.ambient_darkness)
        fog_surface.set_alpha(darkness)
        self.screen.blit(fog_surface, (0, 0))
        
    def _render_zones(self, game_state):
        """Render exploration zones"""
        player = game_state.player
        
        for zone in game_state.world.zones:
            # Calculate screen position relative to player
            screen_x = self.width // 2 + (zone["x"] - player.x)
            screen_y = self.height // 2 + (zone["y"] - player.y)
            
            # Only render if in visibility range
            visibility = game_state.world.get_visibility_radius(player.fear)
            dx = zone["x"] - player.x
            dy = zone["y"] - player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < visibility:
                if zone["explored"]:
                    color = (60, 60, 80)
                else:
                    color = (80, 80, 100)
                    
                # Draw zone as subtle circle
                alpha = int(255 * (1 - distance / visibility))
                if alpha > 0:
                    pygame.draw.circle(self.screen, color, 
                                     (int(screen_x), int(screen_y)), 
                                     zone["radius"], 1)
                    
    def _render_enemies(self, game_state):
        """Render abstract enemies"""
        player = game_state.player
        visibility = game_state.world.get_visibility_radius(player.fear)
        
        for enemy in game_state.enemy_manager.enemies:
            # Calculate screen position
            screen_x = self.width // 2 + (enemy.x - player.x)
            screen_y = self.height // 2 + (enemy.y - player.y)
            
            # Check if enemy is in visibility range
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < visibility:
                # Choose color based on type
                if enemy.type == "shadow":
                    color = self.color_enemy_shadow
                elif enemy.type == "whisper":
                    color = self.color_enemy_whisper
                else:
                    color = self.color_enemy_presence
                    
                # Draw enemy as abstract shape
                alpha = int(255 * (1 - distance / visibility) * 0.7)
                if alpha > 0:
                    if enemy.alert:
                        # Draw as aggressive shape when alert
                        size = 20
                        points = [
                            (screen_x, screen_y - size),
                            (screen_x + size, screen_y + size),
                            (screen_x - size, screen_y + size)
                        ]
                        pygame.draw.polygon(self.screen, color, points)
                    else:
                        # Draw as circle when passive
                        pygame.draw.circle(self.screen, color, 
                                         (int(screen_x), int(screen_y)), 15)
                        
    def _render_player(self, game_state):
        """Render player at center of screen"""
        player = game_state.player
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Player is always at screen center
        pygame.draw.circle(self.screen, self.color_player, 
                         (center_x, center_y), 8)
        
        # Draw direction indicator if moving
        if player.velocity_x != 0 or player.velocity_y != 0:
            angle = math.atan2(player.velocity_y, player.velocity_x)
            end_x = center_x + math.cos(angle) * 15
            end_y = center_y + math.sin(angle) * 15
            pygame.draw.line(self.screen, self.color_player, 
                           (center_x, center_y), 
                           (int(end_x), int(end_y)), 2)
            
    def _render_ui(self, game_state):
        """Render UI elements"""
        player = game_state.player
        
        # Health bar
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 10
        
        # Background
        pygame.draw.rect(self.screen, (40, 40, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_width = int(bar_width * (player.health / player.max_health))
        health_color = (100, 180, 100) if player.health > 50 else (180, 100, 100)
        pygame.draw.rect(self.screen, health_color, 
                        (bar_x, bar_y, health_width, bar_height))
        
        # Health text
        health_text = self.font_small.render(f"Health: {int(player.health)}", 
                                            True, self.color_text)
        self.screen.blit(health_text, (bar_x + 5, bar_y + 2))
        
        # Stamina bar
        bar_y = 35
        pygame.draw.rect(self.screen, (40, 40, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        stamina_width = int(bar_width * (player.stamina / player.max_stamina))
        pygame.draw.rect(self.screen, (100, 150, 180), 
                        (bar_x, bar_y, stamina_width, bar_height))
        
        stamina_text = self.font_small.render(f"Stamina: {int(player.stamina)}", 
                                             True, self.color_text)
        self.screen.blit(stamina_text, (bar_x + 5, bar_y + 2))
        
        # Fear indicator
        bar_y = 60
        pygame.draw.rect(self.screen, (40, 40, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        fear_width = int(bar_width * (player.fear / 100))
        pygame.draw.rect(self.screen, (180, 100, 130), 
                        (bar_x, bar_y, fear_width, bar_height))
        
        fear_text = self.font_small.render(f"Fear: {int(player.fear)}", 
                                          True, self.color_text)
        self.screen.blit(fear_text, (bar_x + 5, bar_y + 2))
        
        # Trust level
        trust_text = self.font_small.render(
            f"Trust: {int(game_state.trust_level * 100)}%", 
            True, self.color_text
        )
        self.screen.blit(trust_text, (self.width - 120, 10))
        
        # Game time
        time_text = self.font_small.render(
            f"Time: {int(game_state.game_time)}s", 
            True, self.color_text
        )
        self.screen.blit(time_text, (self.width - 120, 35))
        
        # Controls hint
        hint_text = self.font_small.render("WASD: Move | Shift: Run | Y: Accept | N: Reject", 
                                          True, (100, 100, 120))
        self.screen.blit(hint_text, (10, self.height - 25))
        
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
