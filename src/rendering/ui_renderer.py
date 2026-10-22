import math
import pygame
from .title_renderer import TitleRenderer
from .game_over_renderer import GameOverRenderer
from ..resources import resource_path

class UIRenderer:
    def __init__(self, screen: pygame.Surface, view_width: int, view_height: int, tile_size: int):
        self.screen = screen
        self.view_width = view_width
        self.view_height = view_height
        self.tile_size = tile_size
        self._font_title = None
        self._font_title_menu = None
        self._font_menu_options = None
        self._font_story = None
        self._font_sub = None
        self._font_credits = None
        self._scream_wave_phase = 0.0
        self._scream_wave_last_ticks = None
        self._backdrop_banner = None
        self._title_renderer = None

    def _get_fonts(self):
        if self._font_title is None:
            # Gothic / medieval font cascade for titles ("Hide and shriek", "Game Over")
            gothic_fonts = ["oldenglishtext", "blackadderitc", "chiller", "goudyoldstyle", "georgia", "serif"]
            # Clean, highly readable sans-serif font cascade for menu options and instructions
            readable_fonts = ["segoeui", "arial", "helvetica", "sans-serif"]
            self._font_title = pygame.font.SysFont(gothic_fonts, 100)
            self._font_title_menu = pygame.font.Font(resource_path("fonts", "Unutterable-Regular.ttf"), 100)
            self._font_menu_options = pygame.font.Font(resource_path("fonts", "Unutterable-Regular.ttf"), 42)
            self._font_sub = pygame.font.Font(resource_path("fonts", "Not Jam Mono Clean 13.ttf"), 39)
            self._font_credits = pygame.font.Font(resource_path("fonts", "Not Jam Mono Clean 13.ttf"), 26)
        return self._font_title, self._font_sub, self._font_credits

    def _get_backdrop(self, width: int, height: int) -> pygame.Surface:
        if self._backdrop_banner is None or self._backdrop_banner.get_size() != (width, height):
            banner = pygame.Surface((width, height), pygame.SRCALPHA)
            # Translucent dark banner overlay to guarantee 100% contrast
            banner.fill((0, 0, 0, 175))
            self._backdrop_banner = banner
        return self._backdrop_banner

    def render_title_screen(self) -> str | None:
        _, font_sub, font_credits = self._get_fonts()
        if self._title_renderer is None:
            self._title_renderer = TitleRenderer(
                self.screen,
                self.view_width,
                self.view_height,
                self.tile_size,
                self._font_title_menu,
                self._font_menu_options,
                font_sub,
                font_credits,
            )
        return self._title_renderer.render()

    def handle_title_event(self, event: pygame.event.Event) -> None:
        if self._title_renderer is not None:
            self._title_renderer.handle_event(event)

    def render_game_over(self):
        font_title, font_sub, _ = self._get_fonts()
        screen_w = self.view_width * self.tile_size
        screen_h = self.view_height * self.tile_size
        backdrop = self._get_backdrop(screen_w, screen_h)
        renderer = GameOverRenderer(self.screen, self.view_width, self.view_height, self.tile_size, font_title, font_sub, backdrop)
        renderer.render()

    def render_story_overlay(self, line1: str, line2: str):
        if self._font_story is None:
            self._font_story = pygame.font.Font(
                resource_path("fonts", "Not Jam Mono Clean 13.ttf"), 26
            )
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
        # grey border around story box
        pygame.draw.rect(box_surf, (65, 65, 65), (0, 0, box_w, box_h), 2)
        self.screen.blit(box_surf, (box_x, box_y))

        # 2. Story text lines
        text1 = self._font_story.render(line1, True, (255, 245, 210))
        text2 = self._font_story.render(line2, True, (230, 220, 200))
        prompt_text = pygame.font.SysFont(["segoeui", "arial", "sans-serif"], 20, italic=True).render("[ Press any key to continue ]", True, (170, 170, 180))

        self.screen.blit(text1, text1.get_rect(center=(cx, box_y + 30)))
        self.screen.blit(text2, text2.get_rect(center=(cx, box_y + 65)))
        self.screen.blit(prompt_text, prompt_text.get_rect(center=(cx, box_y + 102)))

    def render_scream_orb(self, charge: int, required: int):
        charge = max(0, min(charge, required))
        orb = self._build_scream_orb(charge, required)

        size = orb.get_width()
        x = 20
        y = self.screen.get_height() - size - 20
        self.screen.blit(orb, (x, y))

    def _build_scream_orb(self, charge: int, required: int) -> pygame.Surface:
        size = 76
        center = (size // 2, size // 2)
        orb = pygame.Surface((size, size), pygame.SRCALPHA)
        fraction = max(0.0, min(1.0, charge / required))

        # Use a circular reservoir for a cleaner HUD shape.
        outer_radius = 34
        face_radius = 27
        pygame.draw.circle(orb, (2, 8, 14, 170), (center[0] + 2, center[1] + 3), outer_radius)
        pygame.draw.circle(orb, (68, 112, 125, 255), center, outer_radius)
        pygame.draw.circle(orb, (8, 23, 31, 255), center, face_radius + 3)

        face_mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(face_mask, (255, 255, 255, 255), center, face_radius)
        pygame.draw.circle(orb, (5, 20, 28, 255), center, face_radius)

        if fraction > 0:
            # Fill up to the top of the inner circle; its rim contains the energy.
            fill_top = int(center[1] + face_radius - face_radius * 2 * fraction)
            energy = pygame.Surface((size, size), pygame.SRCALPHA)
            for y in range(fill_top, center[1] + face_radius + 1):
                shade = (y - fill_top) / max(1, center[1] + face_radius - fill_top)
                color = (int(42 - 17 * shade), int(218 - 65 * shade), int(244 - 36 * shade), 245)
                pygame.draw.line(energy, color, (0, y), (size - 1, y))
            energy.blit(face_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            orb.blit(energy, (0, 0))

        # A compact angular sound pulse grows with charge and brightens when ready.
        ready = fraction >= 1.0
        ticks = pygame.time.get_ticks()
        pulse = (math.sin(ticks * 0.008) + 1.0) / 2.0
        icon_scale = 1.0
        if ready:
            brightness = 0.7 + 0.3 * pulse
            wave_color = (int(105 + 145 * brightness), int(205 + 50 * brightness), 255, 255)
            edge_color = (int(70 + 90 * pulse), 245, 255, 255)
        else:
            wave_color = (175, 184, 188, 255)
            edge_color = (140, 182, 188, 255)

        def scaled_points(points):
            return [
                (center[0] + int(round(x * icon_scale)), center[1] + int(round(y * icon_scale)))
                for x, y in points
            ]

        # Move the waveform through the center like a live audio trace.
        wave_speed = 0.0015 + 0.0105 * fraction
        if self._scream_wave_last_ticks is not None:
            elapsed_ms = max(0, ticks - self._scream_wave_last_ticks)
            self._scream_wave_phase += elapsed_ms * wave_speed
        self._scream_wave_last_ticks = ticks
        wave_phase = self._scream_wave_phase
        wave = []
        for x in range(-15, 16, 2):
            envelope = max(0.0, 1.0 - abs(x) / 17.0)
            amplitude = (3.0 + 13.0 * fraction) * envelope
            y = int(round(math.sin(x * 0.9 - wave_phase) * amplitude))
            wave.append((x, y))
        wave_width = max(1, round(2 * icon_scale))
        shadow = (2, 12, 20, 255)
        pygame.draw.lines(orb, shadow, False, scaled_points(wave), wave_width + 2)
        pygame.draw.lines(orb, wave_color, False, scaled_points(wave), wave_width)

        pygame.draw.circle(orb, edge_color, center, outer_radius, 4 if ready else 3)
        pygame.draw.circle(orb, (70, 110, 125, 220), center, face_radius, 1)
        return orb
