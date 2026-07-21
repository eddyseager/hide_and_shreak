import os
from random import Random
import esper
import numpy as np
from components import *

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
    'S': create_start_point,
    '.': lambda x, y: create_floor(x, y, '.'),
    ',': lambda x, y: create_floor(x, y, ','),
}

def load_level(level: int, level_map: LevelMap) -> None:
    with open(f'levels{os.sep}{level}.level', encoding="utf-8") as file:
        for y, line in enumerate(file):
            for x, c in enumerate(line.rstrip("\r\n")):
                if c == '+':
                    create_door(x, y, level_map)
                elif c == '§':
                    create_spawn_point(x, y, level_map)
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