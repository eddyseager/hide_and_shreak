import pygame

class UIRenderer:
    def __init__(self, screen: pygame.Surface, view_width: int, view_height: int, tile_size: int):
        self.screen = screen
        self.view_width = view_width
        self.view_height = view_height
        self.tile_size = tile_size
        self._font_72 = None
        self._font_36 = None

    def _get_fonts(self):
        if self._font_72 is None:
            self._font_72 = pygame.font.Font(None, 72)
            self._font_36 = pygame.font.Font(None, 36)
        return self._font_72, self._font_36

    def render_game_over(self):
        font_72, font_36 = self._get_fonts()
        screen_w = self.view_width * self.tile_size
        screen_h = self.view_height * self.tile_size

        go_text = font_72.render("GAME OVER", True, (255, 255, 255))
        go_rect = go_text.get_rect(center=(screen_w // 2, screen_h // 2 - 25))
        self.screen.blit(go_text, go_rect)

        sub_text = font_36.render("Press ESC to Quit", True, (200, 200, 200))
        sub_rect = sub_text.get_rect(center=(screen_w // 2, screen_h // 2 + 30))
        self.screen.blit(sub_text, sub_rect)
