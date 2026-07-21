import pygame

class GameOverRenderer:
    def __init__(self, screen: pygame.Surface, view_width: int, view_height: int, tile_size: int, font_title: pygame.font.Font, font_sub: pygame.font.Font, backdrop_ref=None):
        self.screen = screen
        self.view_width = view_width
        self.view_height = view_height
        self.tile_size = tile_size
        self.font_title = font_title
        self.font_sub = font_sub
        self.backdrop_ref = backdrop_ref

    def render(self):
        screen_w = self.view_width * self.tile_size
        screen_h = self.view_height * self.tile_size
        cx, cy = screen_w // 2, screen_h // 2

        # 1. Render full screen translucent dark overlay
        if self.backdrop_ref is not None:
            self.screen.blit(self.backdrop_ref, (0, 0))

        # 2. Render Game Over Title in gothic font
        title_str = "Game Over"
        title_shadow = self.font_title.render(title_str, True, (0, 0, 0))
        title_text = self.font_title.render(title_str, True, (255, 255, 255))

        title_y = cy - 50
        self.screen.blit(title_shadow, title_shadow.get_rect(center=(cx + 3, title_y + 3)))
        self.screen.blit(title_text, title_text.get_rect(center=(cx, title_y)))

        # 3. Render Restart option in clean readable font
        restart_str = "Press R to Restart"
        restart_shadow = self.font_sub.render(restart_str, True, (0, 0, 0))
        restart_text = self.font_sub.render(restart_str, True, (255, 255, 255))

        restart_y = cy + 30
        self.screen.blit(restart_shadow, restart_shadow.get_rect(center=(cx + 2, restart_y + 2)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(cx, restart_y)))

        # 4. Render Quit option in clean readable font
        quit_str = "Press ESC to Quit"
        quit_shadow = self.font_sub.render(quit_str, True, (0, 0, 0))
        quit_text = self.font_sub.render(quit_str, True, (220, 220, 220))

        quit_y = cy + 75
        self.screen.blit(quit_shadow, quit_shadow.get_rect(center=(cx + 2, quit_y + 2)))
        self.screen.blit(quit_text, quit_text.get_rect(center=(cx, quit_y)))
