import pygame
import random
from config import get_best_font, FONT_FAMILIES

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=(255, 255, 255), 
                 border_radius=12, font_size=22, border_color=None, border_width=2, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.border_color = border_color
        self.border_width = border_width
        self.enabled = enabled
        self.is_hovered = False
        
        # Soft animation properties
        self.current_scale = 1.0
        self.target_scale = 1.0
        self.glow_alpha = 0
        self.target_glow_alpha = 0
        
        # Fonts
        self.font = get_best_font(FONT_FAMILIES, font_size, bold=True)
        
    def update(self, mouse_pos):
        if not self.enabled:
            self.is_hovered = False
            self.target_scale = 1.0
            self.target_glow_alpha = 0
            self.current_scale += (self.target_scale - self.current_scale) * 0.15
            self.glow_alpha += (self.target_glow_alpha - self.glow_alpha) * 0.15
            return
            
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered:
            self.target_scale = 1.04
            self.target_glow_alpha = 130
        else:
            self.target_scale = 1.0
            self.target_glow_alpha = 0
            
        # Linear interpolation (lerp) for smooth scaling and glowing animations
        self.current_scale += (self.target_scale - self.current_scale) * 0.15
        self.glow_alpha += (self.target_glow_alpha - self.glow_alpha) * 0.15
        
    def draw(self, screen):
        cx, cy = self.rect.center
        w = int(self.rect.width * self.current_scale)
        h = int(self.rect.height * self.current_scale)
        draw_rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        
        # Color selection
        if not self.enabled:
            bg_color = (30, 30, 35)
            border_color = (60, 60, 65)
            text_color = (80, 80, 85)
        else:
            bg_color = self.hover_color if self.is_hovered else self.color
            border_color = self.hover_color if self.is_hovered else (self.border_color or self.color)
            text_color = self.text_color
            
        # Draw outer neon glow if enabled & hovered
        if self.enabled and self.glow_alpha > 1:
            glow_surf = pygame.Surface((w + 12, h + 12), pygame.SRCALPHA)
            g_color = (*self.hover_color, int(self.glow_alpha))
            pygame.draw.rect(glow_surf, g_color, (0, 0, w + 12, h + 12), border_radius=self.border_radius + 3)
            screen.blit(glow_surf, (cx - (w + 12) // 2, cy - (h + 12) // 2))
            
        # Draw main button shape
        pygame.draw.rect(screen, bg_color, draw_rect, border_radius=self.border_radius)
        
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(screen, border_color, draw_rect, width=self.border_width, border_radius=self.border_radius)
            
        # Draw multi-line text
        lines = self.text.split('\n')
        line_height = self.font.get_height()
        total_h = len(lines) * line_height
        
        for i, line in enumerate(lines):
            txt_surf = self.font.render(line, True, text_color)
            txt_rect = txt_surf.get_rect()
            txt_rect.center = (cx, cy - total_h // 2 + i * line_height + line_height // 2)
            screen.blit(txt_surf, txt_rect)
            
    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False


class Card:
    """A nice visual container with borders and details to show information."""
    def __init__(self, x, y, width, height, title, body_text="", border_color=(79, 195, 247), border_radius=12):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.body_text = body_text
        self.border_color = border_color
        self.border_radius = border_radius
        self.title_font = get_best_font(FONT_FAMILIES, 22, bold=True)
        self.body_font = get_best_font(FONT_FAMILIES, 16)
        
    def draw(self, screen):
        # Semi-transparent dark blue panel background (glassmorphism feel)
        bg_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (15, 23, 42, 220), (0, 0, self.rect.width, self.rect.height), border_radius=self.border_radius)
        screen.blit(bg_surf, self.rect.topleft)
        
        # Draw border
        pygame.draw.rect(screen, self.border_color, self.rect, width=2, border_radius=self.border_radius)
        
        # Render title
        title_surf = self.title_font.render(self.title, True, (255, 255, 255))
        screen.blit(title_surf, (self.rect.x + 20, self.rect.y + 15))
        
        # Render dividing line
        pygame.draw.line(screen, (40, 60, 80), (self.rect.x + 20, self.rect.y + 45), 
                         (self.rect.x + self.rect.width - 20, self.rect.y + 45), 2)
        
        # Render wrapped body text
        x_start = self.rect.x + 20
        y_curr = self.rect.y + 60
        max_w = self.rect.width - 40
        
        paragraphs = self.body_text.split('\n')
        for para in paragraphs:
            words = para.split(' ')
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                test_surf = self.body_font.render(test_line, True, (200, 215, 230))
                if test_surf.get_width() > max_w:
                    # Draw current_line and start a new one
                    draw_surf = self.body_font.render(current_line, True, (200, 215, 230))
                    screen.blit(draw_surf, (x_start, y_curr))
                    y_curr += self.body_font.get_height() + 3
                    current_line = word + " "
                else:
                    current_line = test_line
            # Draw remaining text of the paragraph
            if current_line:
                draw_surf = self.body_font.render(current_line, True, (200, 215, 230))
                screen.blit(draw_surf, (x_start, y_curr))
                y_curr += self.body_font.get_height() + 3
            # Add extra spacing between paragraphs
            y_curr += 5


class ParticleSystem:
    """Floating particles in the background to simulate Pac-dot pellets."""
    def __init__(self, width, height, num_particles=30):
        self.width = width
        self.height = height
        self.particles = []
        for _ in range(num_particles):
            self.particles.append(self.spawn_particle(random.randint(0, height)))
            
    def spawn_particle(self, y=None):
        return {
            'x': random.randint(0, self.width),
            'y': y if y is not None else self.height + random.randint(5, 50),
            'speed_y': random.uniform(-0.3, -1.0),
            'size': random.randint(2, 4),
            'color': random.choice([
                (254, 189, 17, 80),   # Yellow
                (255, 64, 129, 80),   # Pink (Pinky)
                (79, 195, 247, 80),   # Cyan (Inky)
                (255, 145, 0, 80),    # Orange (Clyde)
                (244, 67, 54, 80)     # Red (Blinky)
            ])
        }
        
    def update(self):
        for p in self.particles:
            p['y'] += p['speed_y']
            if p['y'] < -10:
                # Re-spawn at the bottom
                p['x'] = random.randint(0, self.width)
                p['y'] = self.height + random.randint(5, 20)
                p['speed_y'] = random.uniform(-0.3, -1.0)
                p['size'] = random.randint(2, 4)
                
    def draw(self, screen):
        for p in self.particles:
            # Render transparency using a circular surface
            size = p['size']
            part_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(part_surf, p['color'], (size, size), size)
            screen.blit(part_surf, (int(p['x'] - size), int(p['y'] - size)))


class Transition:
    """Screen fade in / out effect."""
    def __init__(self, speed=8):
        self.speed = speed
        self.alpha = 255
        self.mode = 'fade_in' # 'fade_in', 'fade_out', 'done'
        
    def fade_in(self):
        self.mode = 'fade_in'
        self.alpha = 255
        
    def fade_out(self):
        self.mode = 'fade_out'
        self.alpha = 0
        
    def update(self):
        if self.mode == 'fade_in':
            self.alpha = max(0, self.alpha - self.speed)
            if self.alpha == 0:
                self.mode = 'done'
        elif self.mode == 'fade_out':
            self.alpha = min(255, self.alpha + self.speed)
            if self.alpha == 255:
                self.mode = 'done'
                
    def draw(self, screen):
        if self.alpha > 0:
            fade_surf = pygame.Surface(screen.get_size())
            fade_surf.fill((10, 15, 30))
            fade_surf.set_alpha(self.alpha)
            screen.blit(fade_surf, (0, 0))
            
    def is_done(self):
        return self.mode == 'done'
