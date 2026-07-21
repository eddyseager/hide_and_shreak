import pygame

class VignetteRenderer:
    def __init__(self, tile_size: int, cache_ref: dict = None):
        self.tile_size = tile_size
        self.cache = cache_ref if cache_ref is not None else {}

    def get_vignette(self, w: int, h: int, hp: int, player_screen_x: int, player_screen_y: int) -> pygame.Surface:
        key = (w, h, hp, player_screen_x, player_screen_y)
        if key in self.cache:
            return self.cache[key]

        # Generate high-resolution gradient vignette at 1/2 resolution and smoothscale
        low_w = w // 2
        low_h = h // 2
        vignette_low = pygame.Surface((low_w, low_h), pygame.SRCALPHA)
        vignette_low.fill((0, 0, 0, 0))

        # Determine vignette color based on player hp
        if hp == 1:
            vignette_color = (120, 0, 0)
        elif hp <= 0:
            vignette_color = (255, 0, 0)
            vignette_low.fill((255, 0, 0, 180))
        else:
            vignette_color = (0, 0, 0)

        # Center spotlight on player's screen tile position
        px_ratio = (player_screen_x * self.tile_size + self.tile_size // 2) / w
        py_ratio = (player_screen_y * self.tile_size + self.tile_size // 2) / h
        cx = int(low_w * px_ratio)
        cy = int(low_h * py_ratio)

        x_offset_ratio = abs(px_ratio - 0.5) / 0.5
        y_offset_ratio = abs(py_ratio - 0.5) / 0.5
        max_factor = 1.414 * (1.0 + max(x_offset_ratio, y_offset_ratio))

        # Draw 100 concentric ellipses for smooth gradient
        for step in range(100, 0, -1):
            factor = (step / 100.0) * max_factor
            ellipse_w = int(low_w * factor)
            ellipse_h = int(low_h * factor)
            rx = cx - ellipse_w // 2
            ry = cy - ellipse_h // 2

            norm_factor = factor / max_factor
            if hp == 0:
                alpha = int(255 * (norm_factor ** 0.45))
                alpha = max(0, min(alpha, 255))
            elif hp == 1:
                clamped_factor = min(1.0, norm_factor * 1.25)
                alpha = int(140 * (clamped_factor ** 0.65))
                alpha = max(0, min(alpha, 140))
            else:
                clamped_factor = min(1.0, norm_factor * 1.25)
                alpha = int(250 * (clamped_factor ** 0.65))
                alpha = max(0, min(alpha, 250))

            if alpha > 0:
                rect = pygame.Rect(rx, ry, ellipse_w, ellipse_h)
                pygame.draw.ellipse(vignette_low, (*vignette_color, alpha), rect)

        vignette_surf = pygame.transform.smoothscale(vignette_low, (w, h))
        self.cache[key] = vignette_surf
        return vignette_surf
