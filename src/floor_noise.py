from random import Random

import numpy as np
import tcod.noise

from .floor_variants import FLOOR_VARIANTS, FloorVariantAssignment


def assign_floor_variants(
    lines: list[str], level: int
) -> dict[tuple[int, int], FloorVariantAssignment]:
    """Assign one floor style and tint seed to each noise-selected floor patch."""
    floor_positions = [
        (x, y)
        for y, line in enumerate(lines)
        for x, tile in enumerate(line)
        if tile == '.'
    ]
    if not floor_positions:
        return {}

    height = len(lines)
    width = max(map(len, lines))
    y_grid, x_grid = np.mgrid[0:height, 0:width]
    points = np.stack((x_grid, y_grid), axis=0).astype(np.float32) * 0.18

    noise = tcod.noise.Noise(
        dimensions=2,
        algorithm=tcod.noise.Algorithm.PERLIN,
        seed=level,
    )
    location_noise = noise.sample_mgrid(points)

    # Select the roughly 20% highest-noise floor positions.
    varied_count = round(len(floor_positions) * 0.20)
    if varied_count == 0:
        return {}
    varied_positions = sorted(
        floor_positions,
        key=lambda position: location_noise[position[1], position[0]],
    )[-varied_count:]

    # Find connected patches so neighboring varied tiles share one style.
    alternate_variants = tuple(name for name in FLOOR_VARIANTS if name != 'dot')
    assignments: dict[tuple[int, int], FloorVariantAssignment] = {}
    unassigned = set(varied_positions)
    patch_rng = Random(level)
    while unassigned:
        patch_seed = min(unassigned, key=lambda position: (position[1], position[0]))
        patch = [patch_seed]
        unassigned.remove(patch_seed)

        for x, y in patch:
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in unassigned:
                    unassigned.remove(neighbor)
                    patch.append(neighbor)

        patch_variant = patch_rng.choice(alternate_variants)
        tint_seed = f'{level}:{patch_seed[0]}:{patch_seed[1]}'
        assignment = FloorVariantAssignment(patch_variant, tint_seed)
        for position in patch:
            assignments[position] = assignment

    return assignments
