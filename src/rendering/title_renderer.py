import math
import webbrowser

import pygame

from .mist_renderer import MistRenderer
from ..resources import resource_path


class TitleRenderer:
    CLICK_FEEDBACK_MS = 130
    FADE_DURATION_MS = 400
    GITHUB_URL = 'https://github.com/jupitersoftwarecorp/hide_and_shriek'

    def __init__(
        self,
        screen: pygame.Surface,
        view_width: int,
        view_height: int,
        tile_size: int,
        font_title: pygame.font.Font,
        font_menu: pygame.font.Font,
        font_sub: pygame.font.Font,
        font_credits: pygame.font.Font | None = None,
    ):
        self.screen = screen
        self.view_width = view_width
        self.view_height = view_height
        self.tile_size = tile_size
        self.font_title = font_title
        self.font_menu = font_menu
        self.font_sub = font_sub
        self.font_credits = font_credits if font_credits is not None else font_sub

        screen_w = view_width * tile_size
        screen_h = view_height * tile_size
        castle_image = pygame.image.load(resource_path('assets', 'dark_castle.png')).convert_alpha()
        self.background = pygame.transform.scale(castle_image, (screen_w, screen_h))
        self.background_shade = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        self.background_shade.fill((0, 0, 0, 85))
        self.mist_renderer = MistRenderer(screen_w, screen_h)
        self.menu_click_sound = pygame.mixer.Sound(resource_path('sounds', 'Menu_click_1.wav'))

        self.page = 'main'
        self.menu_item_rects: dict[str, pygame.Rect] = {}
        self.item_scales: dict[str, float] = {}
        self.pressed_item: str | None = None
        self.click_feedback_item: str | None = None
        self.click_feedback_start = 0
        self.pending_action: tuple[str, int] | None = None
        self.transition_action: str | None = None
        self.transition_phase: str | None = None
        self.transition_start = 0
        self.fade_surface: pygame.Surface | None = None
        self.last_render_time: int | None = None
        self.github_link_rect: pygame.Rect | None = None
        self.pressed_github_link = False
        self.github_link_hovered = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.pending_action is not None or self.transition_phase is not None:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.github_link_rect and self.github_link_rect.collidepoint(event.pos):
                self.pressed_github_link = True
                return
            self.pressed_item = self._item_at(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed_github_link:
                self.pressed_github_link = False
                if self.github_link_rect and self.github_link_rect.collidepoint(event.pos):
                    webbrowser.open(self.GITHUB_URL)
                return
            clicked = self.pressed_item
            self.pressed_item = None
            if (
                clicked is None
                or clicked not in self.menu_item_rects
                or not self.menu_item_rects[clicked].collidepoint(event.pos)
            ):
                return

            action = self._item_action(clicked)
            if action is not None:
                now = pygame.time.get_ticks()
                self.menu_click_sound.play()
                self.click_feedback_item = clicked
                self.click_feedback_start = now
                self.pending_action = (action, now + self.CLICK_FEEDBACK_MS)

    def render(self) -> str | None:
        screen_w, screen_h = self.screen.get_size()
        cx, cy = screen_w // 2, screen_h // 2
        now = pygame.time.get_ticks()
        action = self._advance_pending_action(now)

        if self.last_render_time is None:
            delta_seconds = 1 / 30
        else:
            delta_seconds = max(0, now - self.last_render_time) / 1000
        self.last_render_time = now

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.background_shade, (0, 0))
        self.mist_renderer.render(self.screen, now)
        self._render_title(cx, cy)

        self.github_link_rect = None
        if self.page == 'options':
            self._render_centered_text(
                'Options are coming soon.', self.font_sub, (205, 214, 224), (cx, cy + 10)
            )
        elif self.page == 'credits':
            credits = (
                'Game and code: Jupiter Software',
                'Music: Jupiter Software',
                'Sound effects: Jupiter Software, YourPalRob',
                'Tilesheets: Hexany Ives',
                'Dark Castle background: Captainskolot',
                'https://github.com/jupitersoftwarecorp/hide_and_shriek',
            )
            for index, line in enumerate(credits):
                center = (cx, cy - 82 + index * 28)
                if line == self.GITHUB_URL:
                    color = (151, 220, 255)
                    rendered = self.font_credits.render(line, True, color)
                    link_rect = rendered.get_rect(center=center)
                    self.screen.blit(rendered, link_rect)
                    pygame.draw.line(
                        self.screen,
                        color,
                        (link_rect.left, link_rect.bottom + 2),
                        (link_rect.right, link_rect.bottom + 2),
                        1,
                    )
                    self.github_link_rect = link_rect.inflate(8, 8)
                else:
                    self._render_centered_text(
                        line,
                        self.font_credits,
                        (205, 214, 224),
                        center,
                    )

        hovered_link = bool(
            self.github_link_rect
            and self.github_link_rect.collidepoint(pygame.mouse.get_pos())
        )
        if hovered_link != self.github_link_hovered:
            cursor = pygame.SYSTEM_CURSOR_HAND if hovered_link else pygame.SYSTEM_CURSOR_ARROW
            pygame.mouse.set_cursor(cursor)
            self.github_link_hovered = hovered_link

        self._render_menu_items(cx, cy, now, delta_seconds)
        self._render_transition_fade(now)
        return action

    def _render_title(self, cx: int, cy: int) -> None:
        title = self.font_title.render('Hide and Shriek', True, (255, 255, 255))
        shadow = self.font_title.render('Hide and Shriek', True, (0, 0, 0))
        title_y = cy - 180
        self.screen.blit(shadow, shadow.get_rect(center=(cx + 3, title_y + 3)))
        self.screen.blit(title, title.get_rect(center=(cx, title_y)))

    def _render_centered_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        center: tuple[int, int],
    ) -> None:
        rendered = font.render(text, True, color)
        self.screen.blit(rendered, rendered.get_rect(center=center))

    def _menu_items(self, cx: int, cy: int) -> list[tuple[str, str, tuple[int, int]]]:
        if self.page == 'main':
            options = (
                ('play', 'Play'),
                ('options', 'Options'),
                ('credits', 'Credits'),
                ('quit', 'Quit'),
            )
            return [
                (item_id, label, (cx, cy - 30 + index * 60))
                for index, (item_id, label) in enumerate(options)
            ]
        return [('back', 'Back', (cx, cy + 205))]

    def _render_menu_items(self, cx: int, cy: int, now: int, delta_seconds: float) -> None:
        items = self._menu_items(cx, cy)
        self.menu_item_rects = {}
        mouse_pos = pygame.mouse.get_pos()
        interpolation = min(1.0, delta_seconds * 14)

        for item_id, label, center in items:
            normal = self.font_menu.render(label, True, (236, 243, 247))
            hit_rect = normal.get_rect(center=center).inflate(90, 24)
            self.menu_item_rects[item_id] = hit_rect
            hovered = hit_rect.collidepoint(mouse_pos)

            target_scale = 1.18 if hovered else 1.0
            if self.pressed_item == item_id:
                target_scale = 0.90

            click_feedback_active = False
            if self.click_feedback_item == item_id:
                elapsed = now - self.click_feedback_start
                progress = min(1.0, elapsed / self.CLICK_FEEDBACK_MS)
                target_scale = 0.88 + 0.12 * math.sin(progress * math.pi / 2)
                click_feedback_active = True
                if progress >= 1.0:
                    self.click_feedback_item = None

            current_scale = self.item_scales.get(item_id, 1.0)
            if click_feedback_active:
                scale = target_scale
            else:
                scale = current_scale + (target_scale - current_scale) * interpolation
            self.item_scales[item_id] = scale

            text = self.font_menu.render(label, True, (236, 243, 247))
            scaled_size = (max(1, round(text.get_width() * scale)), max(1, round(text.get_height() * scale)))
            text = pygame.transform.smoothscale(text, scaled_size)
            text_rect = text.get_rect(center=center)
            shadow = text.copy()
            shadow.fill((0, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(shadow, shadow.get_rect(center=(center[0] + 2, center[1] + 3)))
            self.screen.blit(text, text_rect)

    def _item_at(self, position: tuple[int, int]) -> str | None:
        for item_id, rect in self.menu_item_rects.items():
            if rect.collidepoint(position):
                return item_id
        return None

    def _item_action(self, item_id: str) -> str | None:
        if item_id == 'options':
            return 'show_options'
        if item_id == 'credits':
            return 'show_credits'
        if item_id == 'back':
            return 'back'
        if item_id in ('play', 'quit'):
            return item_id
        return None

    def _advance_pending_action(self, now: int) -> str | None:
        if self.pending_action is not None:
            action, due_time = self.pending_action
            if now >= due_time:
                self.pending_action = None
                self.transition_action = action
                self.transition_phase = 'out'
                self.transition_start = now

        if self.transition_phase is None:
            return None

        elapsed = now - self.transition_start
        if elapsed < self.FADE_DURATION_MS:
            return None

        if self.transition_phase == 'out':
            action = self.transition_action
            if action == 'show_options':
                self.page = 'options'
            elif action == 'show_credits':
                self.page = 'credits'
            elif action == 'back':
                self.page = 'main'
            elif action in ('play', 'quit'):
                self.transition_phase = 'complete'
                return action

            self.transition_phase = 'in'
            self.transition_start = now
        elif self.transition_phase == 'in':
            self.transition_phase = None
            self.transition_action = None

        return None

    def _render_transition_fade(self, now: int) -> None:
        if self.transition_phase is None:
            return

        screen_size = self.screen.get_size()
        if self.fade_surface is None or self.fade_surface.get_size() != screen_size:
            self.fade_surface = pygame.Surface(screen_size, pygame.SRCALPHA)

        if self.transition_phase == 'complete':
            alpha = 255
        else:
            progress = min(1.0, (now - self.transition_start) / self.FADE_DURATION_MS)
            alpha = round(255 * progress) if self.transition_phase == 'out' else round(255 * (1 - progress))

        if alpha > 0:
            self.fade_surface.fill((0, 0, 0, alpha))
            self.screen.blit(self.fade_surface, (0, 0))
