from dataclasses import dataclass
from .colors import RGB


SpriteCoordinate = tuple[int, int]


@dataclass(frozen=True)
class FloorStyle:
    sprites: tuple[SpriteCoordinate, ...]
    tints: tuple[RGB, ...]


@dataclass(frozen=True)
class FloorVariantAssignment:
    variant: str
    tint_seed: str


# Sprite coordinates and tint palettes for each floor style.
FLOOR_VARIANTS = {
    'dot': FloorStyle(
        sprites=((1, 0),),
        tints=((139, 90, 43),),
    ),
    'plant': FloorStyle(
        sprites=((0, 1),),
        tints=(
            (139, 90, 43),
            (65, 110, 55), (86, 130, 65), (48, 95, 45),
            (115, 70, 130), (140, 85, 155), (90, 55, 115),
        ),
    ),
    'stones': FloorStyle(
        sprites=tuple((col, 2) for col in range(1, 5)),
        tints=(
            (75, 75, 75), (95, 95, 95), (115, 115, 115),
            (105, 75, 48), (130, 95, 62), (155, 120, 82),
        ),
    ),
    'square': FloorStyle(
        sprites=((0, 0),),
        tints=(
            (139, 90, 43), (120, 78, 40), (158, 111, 62),
            (65, 65, 65), (80, 80, 80), (95, 95, 95),
        ),
    ),
}
