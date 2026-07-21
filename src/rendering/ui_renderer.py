import pygame
from rendering.title_renderer import TitleRenderer
from rendering.game_over_renderer import GameOverRenderer

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
            # Gothic / medieval font cascade for titles ("Hide and Shreak", "Game Over")
            gothic_fonts = ["oldenglishtext", "blackadderitc", "chiller", "goudyoldstyle", "georgia", "serif"]
            # Clean, highly readable sans-serif font cascade for menu options and instructions
            readable_fonts = ["segoeui", "arial", "helvetica", "sans-serif"]
            self._font_title = pygame.font.SysFont(gothic_fonts, 100)
            self._font_sub = pygame.font.SysFont(readable_fonts, 32, bold=True)
        return self._font_title, self._font_sub

    def _get_backdrop(self, width: int, height: int) -> pygame.Surface:
        if self._backdrop_banner is None or self._backdrop_banner.get_size() != (width, height):
            banner = pygame.Surface((width, height), pygame.SRCALPHA)
            # Translucent dark banner overlay to guarantee 100% contrast
            banner.fill((0, 0, 0, 175))
            self._backdrop_banner = banner
        return self._backdrop_banner

    def render_title_screen(self):
        font_title, font_sub = self._get_fonts()
        renderer = TitleRenderer(self.screen, self.view_width, self.view_height, self.tile_size, font_title, font_sub)
        renderer.render()

    def render_game_over(self):
        font_title, font_sub = self._get_fonts()
        screen_w = self.view_width * self.tile_size
        screen_h = self.view_height * self.tile_size
        backdrop = self._get_backdrop(screen_w, screen_h)
        renderer = GameOverRenderer(self.screen, self.view_width, self.view_height, self.tile_size, font_title, font_sub, backdrop)
        renderer.render()
