import esper
from components import *
from random import Random
import os
import numpy as np

def load_level(level: int) -> None:
    with open(f'levels{os.sep}{level}.level') as file:
        x = 0
        y = 0
        for line in file:
            x =0
            for c in line:
                if c == CHAR_UP_STAIR:
                    create_stairs_up(x, y)
                elif c == CHAR_DOWN_STAIR:
                    create_stairs_down(x, y)
                elif ord(c) & 0xFF00 == 0x2500:
                    create_wall(x, y, c, level)
                elif c == '.' or c == ',':
                    create_floor(x, y, c)
                elif c == CHAR_SPAWN_POINT:
                    create_spawn_point(x, y)
                x += 1
            y += 1

def remove_level() -> None:
    for e, _ in esper.get_component(Position):
        esper.delete_entity(e, True)

def create_player(x: int, y: int, level: int) -> None:
    esper.create_entity(Map_Object(), Player(), Position(x, y), Graphic(CHAR_PLAYER, (255, 255, 255)), Level(level))

def create_enemy(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), Enemy(), Position(x, y), Graphic(CHAR_ENEMY, (255, 0, 0)))

def create_spawn_point(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), SpawnPoint(), Position(x, y), Graphic(CHAR_SPAWN_POINT, (255, 0, 0)))

def create_stairs_down(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), StairsDown(), Position(x, y), Graphic(CHAR_DOWN_STAIR, (255, 255, 255)))

def create_stairs_up(x: int, y: int) -> None:
    esper.create_entity(Map_Object(), StairsUp(), Position(x, y), Graphic(CHAR_UP_STAIR, (255, 255, 255)))

def create_wall(x: int, y: int, g: str, level: int) -> None:
    esper.create_entity(Map_Object(), Wall(), Position(x, y), Graphic(g, (255, 255, 255)))

    #Walls are not transparent
    for _, (fov, l) in esper.get_components(FOV, Level):
        if l.val == level:
            fov.transparent[x, y] = False

def create_floor(x: int, y: int, g: str) -> None:
    esper.create_entity(Floor(), Position(x, y), Graphic(g, (255, 255, 255)))

def create_map_dimension() -> None:
    esper.create_entity(MapDimension(MAP_HEIGHT, MAP_WIDTH))

def create_level(level: int) -> None:

    #Check whether entity for this level already exists
    create_level = True
    for e, (l, f) in esper.get_components(Level, FOV):
        if l.val == level:
            create_level = False

    if create_level:
        #Create numpy array of walls to track transparency and explored tiles
        trans = np.ones((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
        exp = np.zeros((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
        visible = np.zeros((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
        esper.create_entity(Level(level), FOV(explored=exp, transparent=trans, visible=visible))

    load_level(level) #TODO - don't reload level from file each time, keep in memory

def create_counter() -> None:
    e = esper.create_entity(Counter(0))
    print (e)