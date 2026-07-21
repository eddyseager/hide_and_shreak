import math
import random
import pygame

class MistRenderer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.rng = random.Random(42)

        # Generate 48 native 1:1 High-Definition smoke tendrils
        self.particles = []
        for _ in range(48):
            w_size = self.rng.randint(220, 480)
            h_size = self.rng.randint(50, 150)

            # Generate 1:1 HD wisp surface without low-res downscaling
            wisp_surf = self._generate_hd_wisp(w_size, h_size, self.rng)

            self.particles.append({
                'surf': wisp_surf,
                'width': w_size,
                'height': h_size,
                'x': float(self.rng.randint(0, width)),
                'base_y': float(self.rng.randint(-30, height - 10)),
                'speed_x': self.rng.uniform(0.18, 0.85),
                'freq': self.rng.uniform(0.0007, 0.0022),
                'phase': self.rng.uniform(0.0, 6.28),
                'amp': self.rng.uniform(6.0, 24.0),
                'alpha_freq': self.rng.uniform(0.0008, 0.0028),
                'base_alpha': self.rng.randint(130, 220),
            })

    def _generate_hd_wisp(self, w: int, h: int, rng: random.Random) -> pygame.Surface:
        # Full 1:1 High-Definition surface (no resolution scaling)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        color = rng.choice([(35, 40, 50), (55, 60, 70), (85, 90, 100)])

        # Composite 12 smooth concentric sub-ellipses for crisp HD gradient tendrils
        for _ in range(12):
            ew = rng.randint(w // 3, w)
            eh = rng.randint(h // 4, h)
            ex = rng.randint(0, max(1, w - ew))
            ey = rng.randint(0, max(1, h - eh))

            sub_puff = pygame.Surface((ew, eh), pygame.SRCALPHA)
            steps = 10
            for step in range(steps, 0, -1):
                factor = step / float(steps)
                curr_w = int(ew * factor)
                curr_h = int(eh * factor)
                rx = (ew - curr_w) // 2
                ry = (eh - curr_h) // 2
                alpha = int(10 * (1.0 - factor))
                if alpha > 0 and curr_w > 0 and curr_h > 0:
                    pygame.draw.ellipse(sub_puff, (*color, alpha), (rx, ry, curr_w, curr_h))

            surf.blit(sub_puff, (ex, ey))

        return surf

    def render(self, screen: pygame.Surface, time: int):
        scr_w, scr_h = self.width, self.height

        for p in self.particles:
            px = (p['x'] + time * p['speed_x'] * 0.05) % (scr_w + p['width']) - p['width']
            py = p['base_y'] + math.sin(time * p['freq'] + p['phase']) * p['amp']

            # Smooth alpha modulation (crystal-clear HD rendering with zero rescaling artifacts)
            alpha_mult = 0.75 + math.sin(time * p['alpha_freq'] + p['phase']) * 0.25
            cur_alpha = int(p['base_alpha'] * alpha_mult)

            p['surf'].set_alpha(max(0, min(255, cur_alpha)))
            screen.blit(p['surf'], (int(px), int(py)))
