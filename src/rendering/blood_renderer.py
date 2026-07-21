import random
import pygame
from components import Blood

class BloodRenderer:
    def __init__(self, screen: pygame.Surface, tile_size: int):
        self.screen = screen
        self.tile_size = tile_size

    def render(self, blood: Blood, rect: pygame.Rect, visible: bool):
        rng = random.Random(blood.seed)
        base_color = (150, 10, 10) if visible else (60, 4, 4)

        cx = rect.x + self.tile_size // 2
        cy = rect.y + self.tile_size // 2

        if blood.intensity == 1:
            main_r = rng.randint(4, 5)
            num_drops = rng.randint(3, 4)
        else:
            main_r = rng.randint(6, 8)
            num_drops = rng.randint(5, 7)

        # Draw main center splatter
        pygame.draw.circle(self.screen, base_color, (cx + rng.randint(-2, 2), cy + rng.randint(-2, 2)), main_r)

        # Draw satellite droplets
        for _ in range(num_drops):
            off_x = rng.randint(-self.tile_size // 3, self.tile_size // 3)
            off_y = rng.randint(-self.tile_size // 3, self.tile_size // 3)
            drop_r = rng.randint(1, 2)
            drop_color = (
                max(0, min(255, base_color[0] + rng.randint(-15, 15))),
                max(0, min(255, base_color[1] + rng.randint(-2, 2))),
                max(0, min(255, base_color[2] + rng.randint(-2, 2)))
            )
            pygame.draw.circle(self.screen, drop_color, (cx + off_x, cy + off_y), drop_r)
