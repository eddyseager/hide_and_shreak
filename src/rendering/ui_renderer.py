import pygame

class UIRenderer:
    def __init__(self, screen: pygame.Surface, view_width: int, view_height: int, tile_size: int):
        self.screen = screen
        self.view_width = view_width
        self.view_height = view_height
        self.tile_size = tile_size
        self._font_title = None
        self._font_sub = None
        self._backdrop_banner = None

    def _get_fonts(self):
        if self._font_title is None:
            # Authentic gothic / medieval font cascade (regular weight for legibility)
            gothic_fonts = ["oldenglishtext", "blackadderitc", "chiller", "goudyoldstyle", "georgia", "serif"]
            self._font_title = pygame.font.SysFont(gothic_fonts, 100)
            self._font_sub = pygame.font.SysFont(gothic_fonts, 36)
        return self._font_title, self._font_sub

    def _get_backdrop(self, width: int, height: int) -> pygame.Surface:
        if self._backdrop_banner is None or self._backdrop_banner.get_size() != (width, height):
            banner = pygame.Surface((width, height), pygame.SRCALPHA)
            # Translucent dark banner overlay to guarantee 100% contrast
            banner.fill((0, 0, 0, 175))
            self._backdrop_banner = banner
        return self._backdrop_banner

    def render_game_over(self):
        font_title, font_sub = self._get_fonts()
        screen_w = self.view_width * self.tile_size
        screen_h = self.view_height * self.tile_size
        cx, cy = screen_w // 2, screen_h // 2

        # 1. Render dark backdrop banner across the text area
        banner_h = 240
        banner_y = cy - 120
        banner = self._get_backdrop(screen_w, banner_h)
        self.screen.blit(banner, (0, banner_y))

        # 2. Render Game Over Title in Title Case with regular font weight
        title_str = "Game Over"
        title_shadow = font_title.render(title_str, True, (0, 0, 0))
        title_text = font_title.render(title_str, True, (255, 255, 255))

        title_y = cy - 50
        self.screen.blit(title_shadow, title_shadow.get_rect(center=(cx + 3, title_y + 3)))
        self.screen.blit(title_text, title_text.get_rect(center=(cx, title_y)))

        # 3. Render Restart option on its own line
        restart_str = "Press R to Restart"
        restart_shadow = font_sub.render(restart_str, True, (0, 0, 0))
        restart_text = font_sub.render(restart_str, True, (255, 255, 255))

        restart_y = cy + 30
        self.screen.blit(restart_shadow, restart_shadow.get_rect(center=(cx + 2, restart_y + 2)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(cx, restart_y)))

        # 4. Render Quit option on a new line below restart
        quit_str = "Press ESC to Quit"
        quit_shadow = font_sub.render(quit_str, True, (0, 0, 0))
        quit_text = font_sub.render(quit_str, True, (220, 220, 220))

        quit_y = cy + 75
        self.screen.blit(quit_shadow, quit_shadow.get_rect(center=(cx + 2, quit_y + 2)))
        self.screen.blit(quit_text, quit_text.get_rect(center=(cx, quit_y)))
