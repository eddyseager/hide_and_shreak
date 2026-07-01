import os
from random import Random
import esper
import numpy as np
from components import *

# Mapping of character glyphs to specific tiles: (sheet, col, row, default_fg)
CHAR_MAP = {
    '.': ('general', 1, 0, (139, 90, 43)),     # Original Brown Floor
    ',': ('autotile', 13, 1, (115, 75, 35)),    # Alternate Floor (Autotile C:13 R:1)
    '<': ('general', 3, 0, (110, 110, 110)),    # Stairs Up
    '>': ('general', 2, 0, (110, 110, 110)),    # Stairs Down
    '+': ('general', 4, 0, (110, 110, 110)),    # Door
    '@': ('creatures', 0, 0, (255, 255, 255)),   # Player
    '§': ('general', 30, 0, (255, 255, 255)),   # Spawn Point
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
    '├': ('autotile', 5, 1, (110, 110, 110)),
    '┤': ('autotile', 6, 1, (110, 110, 110)),
    '╬': ('autotile', 8, 4, (110, 110, 110)),
}

def get_graphic_for_char(g: str) -> Graphic:
    if g in WALL_MAP:
        sheet, col, row, color = WALL_MAP[g]
    elif ord(g) & 0xFF00 == 0x2500 or g == '#': #Fallback wall
        sheet, col, row, color = ('autotile', 1, 3, (110, 110, 110))
    elif g in CHAR_MAP:
        sheet, col, row, color = CHAR_MAP[g]
    else:
        # Fallback default (general dot)
        sheet, col, row, color = ('general', 1, 0, (110, 110, 110))
    return Graphic(g=g, fg=color, sheet=sheet, col=col, row=row)

def create_player(x: int, y: int, level: int) -> None:
    esper.create_entity(Map_Object(), Player(), Position(x, y), get_graphic_for_char('@'), Level(level))

def create_enemy(x: int, y: int) -> None:
    # Pick random enemy sprite from row 3 (0-15) or row 4 (0-12)
    enemy_sprites = [(c, 3) for c in range(16)] + [(c, 4) for c in range(13)]
    col, row = Random().choice(enemy_sprites)
    esper.create_entity(PlayerMover(), Blocks_Movement(), Map_Object(), Enemy(), Position(x, y), Graphic('&', (255, 0, 0), sheet="creatures", col=col, row=row))

def create_spawn_point(x: int, y: int) -> None:
    esper.create_entity(Blocks_Movement(), Map_Object(), SpawnPoint(), Position(x, y), get_graphic_for_char('§'))

def create_door(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), Position(x, y), get_graphic_for_char('+'))

def create_stairs_down(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), StairsDown(), Position(x, y), get_graphic_for_char('>'))

def create_stairs_up(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), StairsUp(), Position(x, y), get_graphic_for_char('<'))

def create_wall(x: int, y: int, g: str, level: int) -> None:
    esper.create_entity(Blocks_Movement(), Map_Object(), Wall(), Position(x, y), get_graphic_for_char(g))

    # Walls are not transparent
    for _, (fov, l) in esper.get_components(FOV, Level):
        if l.val == level:
            fov.transparent[x, y] = False

def create_floor(x: int, y: int, g: str) -> None:
    esper.create_entity(Floor(), Position(x, y), get_graphic_for_char(g))

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
    '+': create_door,
    '§': create_spawn_point,
    '.': lambda x, y: create_floor(x, y, '.'),
    ',': lambda x, y: create_floor(x, y, ','),
}

def load_level(level: int) -> None:
    with open(f'levels{os.sep}{level}.level', encoding="utf-8") as file:
        for y, line in enumerate(file):
            for x, c in enumerate(line.rstrip("\r\n")):
                if c in BUILDER_MAP:
                    BUILDER_MAP[c](x, y)
                elif ord(c) & 0xFF00 == 0x2500:
                    create_wall(x, y, c, level)

def create_level(level: int) -> None:
    # Check whether entity for this level already exists
    create_level = True
    for e, (l, f) in esper.get_components(Level, FOV):
        if l.val == level:
            create_level = False

    if create_level:
        # Create numpy array of walls to track transparency and explored tiles
        trans = np.ones((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
        exp = np.zeros((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
        visible = np.zeros((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
        esper.create_entity(Level(level), FOV(explored=exp, transparent=trans, visible=visible))

    load_level(level) # TODO - don't reload level from file each time, keep in memory