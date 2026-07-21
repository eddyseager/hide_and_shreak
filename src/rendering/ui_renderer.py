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
        self._font_credits = None
        self._backdrop_banner = None

    def _get_fonts(self):
        if self._font_title is None:
            # Gothic / medieval font cascade for titles ("Hide and Shreak", "Game Over")
            gothic_fonts = ["oldenglishtext", "blackadderitc", "chiller", "goudyoldstyle", "georgia", "serif"]
            # Clean, highly readable sans-serif font cascade for menu options and instructions
            readable_fonts = ["segoeui", "arial", "helvetica", "sans-serif"]
            self._font_title = pygame.font.SysFont(gothic_fonts, 100)
            self._font_sub = pygame.font.SysFont(readable_fonts, 32, bold=True)
            self._font_credits = pygame.font.SysFont(readable_fonts, 22)
        return self._font_title, self._font_sub, self._font_credits

    def _get_backdrop(self, width: int, height: int) -> pygame.Surface:
        if self._backdrop_banner is None or self._backdrop_banner.get_size() != (width, height):
            banner = pygame.Surface((width, height), pygame.SRCALPHA)
            # Translucent dark banner overlay to guarantee 100% contrast
            banner.fill((0, 0, 0, 175))
            self._backdrop_banner = banner
        return self._backdrop_banner

    def render_title_screen(self):
        font_title, font_sub, font_credits = self._get_fonts()
        renderer = TitleRenderer(self.screen, self.view_width, self.view_height, self.tile_size, font_title, font_sub, font_credits)
        renderer.render()

    def render_game_over(self):
        font_title, font_sub, _ = self._get_fonts()
        screen_w = self.view_width * self.tile_size
        screen_h = self.view_height * self.tile_size
        backdrop = self._get_backdrop(screen_w, screen_h)
        renderer = GameOverRenderer(self.screen, self.view_width, self.view_height, self.tile_size, font_title, font_sub, backdrop)
        renderer.render()

    def render_story_overlay(self, line1: str, line2: str):
        font_title, font_sub, _ = self._get_fonts()
        screen_w = self.view_width * self.tile_size
        screen_h = self.view_height * self.tile_size
        cx = screen_w // 2

        # 1. Dark translucent message box at top/center of screen
        box_w = min(screen_w - 40, 880)
        box_h = 135
        box_y = 35
        box_x = cx - box_w // 2

        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((10, 10, 18, 235))
        # Gold/white border around story box
        pygame.draw.rect(box_surf, (190, 170, 110), (0, 0, box_w, box_h), 2)
        self.screen.blit(box_surf, (box_x, box_y))

        # 2. Story text lines
        text1 = font_sub.render(line1, True, (255, 245, 210))
        text2 = font_sub.render(line2, True, (230, 220, 200))
        prompt_text = pygame.font.SysFont(["segoeui", "arial", "sans-serif"], 20, italic=True).render("[ Press any key to continue ]", True, (170, 170, 180))

        self.screen.blit(text1, text1.get_rect(center=(cx, box_y + 30)))
        self.screen.blit(text2, text2.get_rect(center=(cx, box_y + 65)))
        self.screen.blit(prompt_text, prompt_text.get_rect(center=(cx, box_y + 102)))
