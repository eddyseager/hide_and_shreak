import pygame
from rendering.mist_renderer import MistRenderer

class TitleRenderer:
    def __init__(self, screen: pygame.Surface, view_width: int, view_height: int, tile_size: int, font_title: pygame.font.Font, font_sub: pygame.font.Font, font_credits: pygame.font.Font = None):
        self.screen = screen
        self.view_width = view_width
        self.view_height = view_height
        self.tile_size = tile_size
        self.font_title = font_title
        self.font_sub = font_sub
        self.font_credits = font_credits if font_credits is not None else font_sub
        
        screen_w = view_width * tile_size
        screen_h = view_height * tile_size
        self.mist_renderer = MistRenderer(screen_w, screen_h)

    def render(self):
        screen_w = self.view_width * self.tile_size
        screen_h = self.view_height * self.tile_size
        cx, cy = screen_w // 2, screen_h // 2
        time = pygame.time.get_ticks()

        # 1. Fill screen background with dark nocturnal void
        self.screen.fill((5, 5, 10))

        # 2. Render scary rolling mist animation layers
        self.mist_renderer.render(self.screen, time)

        # 3. Game Title "Hide and Shreak" in gothic font
        title_str = "Hide and Shreak"
        title_shadow = self.font_title.render(title_str, True, (0, 0, 0))
        title_text = self.font_title.render(title_str, True, (255, 255, 255))

        title_y = cy - 60
        self.screen.blit(title_shadow, title_shadow.get_rect(center=(cx + 3, title_y + 3)))
        self.screen.blit(title_text, title_text.get_rect(center=(cx, title_y)))

        # 4. Instructions in clean readable font
        start_str = "Press SPACE to Play"
        start_shadow = self.font_sub.render(start_str, True, (0, 0, 0))
        start_text = self.font_sub.render(start_str, True, (255, 255, 255))

        start_y = cy + 30
        self.screen.blit(start_shadow, start_shadow.get_rect(center=(cx + 2, start_y + 2)))
        self.screen.blit(start_text, start_text.get_rect(center=(cx, start_y)))

        quit_str = "Press ESC to Quit"
        quit_shadow = self.font_sub.render(quit_str, True, (0, 0, 0))
        quit_text = self.font_sub.render(quit_str, True, (200, 200, 200))

        quit_y = cy + 80
        self.screen.blit(quit_shadow, quit_shadow.get_rect(center=(cx + 2, quit_y + 2)))
        self.screen.blit(quit_text, quit_text.get_rect(center=(cx, quit_y)))

        # 5. Credits
        credit1_str = "Code & Music by Edwin van Seagull"
        credit1_shadow = self.font_credits.render(credit1_str, True, (0, 0, 0))
        credit1_text = self.font_credits.render(credit1_str, True, (190, 190, 200))

        c1_y = screen_h - 48
        self.screen.blit(credit1_shadow, credit1_shadow.get_rect(center=(cx + 1, c1_y + 1)))
        self.screen.blit(credit1_text, credit1_text.get_rect(center=(cx, c1_y)))

        credit2_str = "Tilesheets by Hexany"
        credit2_shadow = self.font_credits.render(credit2_str, True, (0, 0, 0))
        credit2_text = self.font_credits.render(credit2_str, True, (160, 160, 170))

        c2_y = screen_h - 24
        self.screen.blit(credit2_shadow, credit2_shadow.get_rect(center=(cx + 1, c2_y + 1)))
        self.screen.blit(credit2_text, credit2_text.get_rect(center=(cx, c2_y)))
