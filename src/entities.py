import os
from random import Random
import esper
import numpy as np
import tcod.noise
from .components import *
from .resources import resource_path

# Mapping of character glyphs to specific tiles: (sheet, col, row, default_fg)
CHAR_MAP = {
    '.': ('general', 1, 0, (139, 90, 43)),     # Original Brown Floor
    ',': ('autotile', 13, 1, (59, 38, 18)),    # Alternate Floor (Autotile C:13 R:1)
    '<': ('general', 3, 0, (110, 110, 110)),    # Stairs Up
    '>': ('general', 2, 0, (110, 110, 110)),    # Stairs Down
    '+': ('general', 4, 0, (110, 110, 110)),    # Door
    '@': ('creatures', 0, 0, (255, 255, 255)),   # Player
    '§': ('general', 30, 0, (255, 255, 255)),   # Spawn Point
    'S': ('general', 1, 0, (139, 90, 43)),   # Start Point (Floor tile)
}

# Mapping of wall glyphs to autotile coordinates (medium grey)
WALL_MAP = {
    '─': ('autotile', 1, 3, (110, 110, 110)),
    '│': ('autotile', 3, 1, (110, 110, 110)),
    '┌': ('autotile', 4, 0, (110, 110, 110)),
    '┐': ('autotile', 7, 0, (110, 110, 110)),
    '└': ('autotile', 0, 2, (110, 110, 110)),
    '┘': ('autotile', 2, 2, (110, 110, 110)),
    '┬': ('autotile', 8, 0, (110, 110, 110)),
    '┴': ('autotile', 8, 3, (110, 110, 110)),
    '├': ('autotile', 4, 4, (110, 110, 110)),
    '┤': ('autotile', 7, 4, (110, 110, 110)),
    '╬': ('autotile', 8, 4, (110, 110, 110)),
}

# Standard floor sprites and their tint palettes.
FLOOR_VARIANTS = {
    'dot': {
        'tile': (1, 0),
        'tints': [(139, 90, 43)],
    },
    'plant': {
        'tile': (0, 1),
        'tints': [
            (139, 90, 43),
            (65, 110, 55), (86, 130, 65), (48, 95, 45),
            (115, 70, 130), (140, 85, 155), (90, 55, 115),
        ],
    },
    'stones': {
        'tile': (1, 2),
        'tints': [(75, 75, 75)],
    },
    'square': {
        'tile': (0, 0),
        'tints': [
            (139, 90, 43), (120, 78, 40), (158, 111, 62),
            (65, 65, 65), (80, 80, 80), (95, 95, 95),
        ],
    },
}

def get_graphic_for_char(g: str, floor_variant: str = 'dot', floor_seed=None) -> Graphic:
    if g == '.':
        variant = FLOOR_VARIANTS[floor_variant]
        col, row = variant['tile']
        color = Random(floor_seed).choice(variant['tints'])
        sheet = 'general'
    elif g in WALL_MAP:
        sheet, col, row, color = WALL_MAP[g]
    elif ord(g) & 0xFF00 == 0x2500 or g == '#': #Fallback wall
        sheet, col, row, color = ('autotile', 1, 3, (110, 110, 110))
    elif g in CHAR_MAP:
        sheet, col, row, color = CHAR_MAP[g]
    else:
        # Fallback default (general dot)
        sheet, col, row, color = ('general', 1, 0, (110, 110, 110))
    return Graphic(g=g, fg=color, sheet=sheet, col=col, row=row)

def create_player(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), Player(), Position(x, y), get_graphic_for_char('@'))

def create_enemy(x: int, y: int) -> None:
    # Pick random enemy sprite from row 3 (0-15) or row 4 (0-12)
    enemy_sprites = [(c, 3) for c in range(16)] + [(c, 4) for c in range(13)]
    col, row = Random().choice(enemy_sprites)
    
    explored = np.zeros((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
    
    esper.create_entity(
        PlayerMover(), 
        Map_Object(), 
        Enemy(), 
        Position(x, y), 
        Graphic('&', (255, 0, 0), sheet="creatures", col=col, row=row),
        EnemyAI(state="explore", explored=explored)
    )

def create_spawn_point(x: int, y: int, level_map: LevelMap) -> None:
    esper.create_entity(Blocks_Movement(), Map_Object(), SpawnPoint(), Position(x, y), get_graphic_for_char('§'))
    
    # Spawn points block movement
    level_map.walkable[x, y] = False

def create_door(x: int, y: int, level_map: LevelMap) -> None:
    # Doors are always spawned closed initially
    esper.create_entity(Map_Object(), ClosedDoor(), Position(x, y), get_graphic_for_char('+'))
    level_map.transparent[x, y] = False

def create_stairs_down(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), StairsDown(), Position(x, y), get_graphic_for_char('>'))

def create_stairs_up(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), StairsUp(), Position(x, y), get_graphic_for_char('<'))

def create_start_point(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), StartPoint(), Position(x, y), get_graphic_for_char('S'))

def create_wall(x: int, y: int, g: str, level_map: LevelMap) -> None:
    esper.create_entity(Blocks_Movement(), Blocks_FOV(), Map_Object(), Wall(), Position(x, y), get_graphic_for_char(g))

    # Walls block both transparency and movement
    level_map.transparent[x, y] = False
    level_map.walkable[x, y] = False

def create_floor(
    x: int,
    y: int,
    g: str,
    variant: str = 'dot',
    level: int = 0,
    tint_seed: str | None = None,
) -> None:
    floor_seed = tint_seed or f'{level}:{x}:{y}'
    graphic = get_graphic_for_char(g, floor_variant=variant, floor_seed=floor_seed)
    esper.create_entity(Floor(), Position(x, y), graphic)

def create_map_dimension() -> None:
    esper.create_entity(MapDimension(MAP_HEIGHT, MAP_WIDTH))

def create_counter() -> None:
    esper.create_entity(Counter(0))

def remove_level() -> None:
    for e, _ in esper.get_component(Position):
        esper.delete_entity(e, True)

# Map level characters to builder helper functions
BUILDER_MAP = {
    '<': create_stairs_up,
    '>': create_stairs_down,
    'S': create_start_point,
    ',': lambda x, y: create_floor(x, y, ','),
}

def _assign_floor_variants(lines: list[str], level: int) -> dict[tuple[int, int], tuple[str, str]]:
    """Use low-frequency Perlin noise to place alternate floor sprites in patches."""
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

    def sample_floor_noise(seed: int) -> np.ndarray:
        noise = tcod.noise.Noise(
            dimensions=2,
            algorithm=tcod.noise.Algorithm.PERLIN,
            seed=seed,
        )
        return noise.sample_mgrid(points)

    location_noise = sample_floor_noise(level)

    # Keep roughly 20% of the floor varied, grouping similar noise values together.
    varied_count = round(len(floor_positions) * 0.20)
    if varied_count == 0:
        return {}
    varied_positions = sorted(
        floor_positions,
        key=lambda position: location_noise[position[1], position[0]],
    )[-varied_count:]

    # A second smooth field assigns one variant to each broad patch, so different
    # sprites do not alternate tile by tile inside the varied areas.
    variant_noise = sample_floor_noise(level + 100_003)
    varied_positions.sort(key=lambda position: variant_noise[position[1], position[0]])
    alternate_variants = ('plant', 'stones', 'square')
    variant_by_position: dict[tuple[int, int], str] = {}
    for index, position in enumerate(varied_positions):
        variant_index = min(index * len(alternate_variants) // varied_count, len(alternate_variants) - 1)
        variant_by_position[position] = alternate_variants[variant_index]

    # Give each connected same-variant patch one tint seed, keeping its color uniform.
    tint_seed_by_position: dict[tuple[int, int], str] = {}
    unassigned = set(variant_by_position)
    while unassigned:
        patch_seed = min(unassigned, key=lambda position: (position[1], position[0]))
        patch_variant = variant_by_position[patch_seed]
        patch = [patch_seed]
        unassigned.remove(patch_seed)

        for x, y in patch:
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in unassigned and variant_by_position[neighbor] == patch_variant:
                    unassigned.remove(neighbor)
                    patch.append(neighbor)

        tint_seed = f'{level}:{patch_seed[0]}:{patch_seed[1]}'
        for position in patch:
            tint_seed_by_position[position] = tint_seed

    return {
        position: (variant, tint_seed_by_position[position])
        for position, variant in variant_by_position.items()
    }

def load_level(level: int, level_map: LevelMap) -> None:
    with resource_path("levels", f"{level}.level").open(encoding="utf-8") as file:
        lines = [line.rstrip("\r\n") for line in file]

    floor_variants = _assign_floor_variants(lines, level)
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c == '+':
                create_door(x, y, level_map)
            elif c == '§':
                create_spawn_point(x, y, level_map)
            elif c == '.':
                variant, tint_seed = floor_variants.get(
                    (x, y),
                    ('dot', f'{level}:{x}:{y}'),
                )
                create_floor(x, y, c, variant, level, tint_seed)
            elif c in BUILDER_MAP:
                BUILDER_MAP[c](x, y)
            elif ord(c) & 0xFF00 == 0x2500:
                create_wall(x, y, c, level_map)

def create_level(level: int) -> None:
    trans = np.ones((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
    exp = np.zeros((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
    visible = np.zeros((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
    walkable = np.ones((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
    level_map = LevelMap(explored=exp, transparent=trans, visible=visible, walkable=walkable, index=level)
    esper.create_entity(level_map)

    load_level(level, level_map)
