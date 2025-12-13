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
                if c == '<':
                    create_stairs_up(x, y)
                elif c == '>':
                    create_stairs_down(x, y)
                elif ord(c) & 0xFF00 == 0x2500:
                    create_wall(x, y, c, level)
                elif c == '.' or c == ',':
                    create_floor(x, y, c)
                x += 1
            y += 1

def create_fov(level: int) -> None:
    for e, l in esper.get_component(Level):
        if l.val == level:
            #Create the FOV if this level hasn't been visited before.
            if not esper.has_component(e, FOV):
                print(f"create fov level {l}")
                #Create numpy array of walls to track transparency
                trans = np.ones((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
                exp = np.zeros((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
                esper.add_component(e, FOV(explored=exp, transparent=trans))

def remove_level() -> None:
    #Deletes all entities with a position component - may want to fix later for the player
    for e, _ in esper.get_component(Position):
        esper.delete_entity(e, True)

def create_player(x: int, y: int, level: int) -> None:
    esper.create_entity(Player(), Position(x, y), Graphic("@", (255, 255, 255)), Level(level))

def create_stairs_down(x: int, y: int) -> None:
    esper.create_entity(StairsDown(), Position(x, y), Graphic(">", (255, 255, 255)))

def create_stairs_up(x: int, y: int) -> None:
    esper.create_entity(StairsUp(), Position(x, y), Graphic("<", (255, 255, 255)))

def create_wall(x: int, y: int, g: str, level: int) -> None:
    esper.create_entity(Wall(), Position(x, y), Graphic(g, (255, 255, 255)))

    #Walls are not transparent
    for _, (fov, l) in esper.get_components(FOV, Level):
        if l.val == level:
            fov.transparent[x, y] = False

def create_floor(x: int, y: int, g: str) -> None:
    esper.create_entity(Floor(), Position(x, y), Graphic(g, (255, 255, 255)))

def create_map_dimension() -> None:
    esper.create_entity(MapDimension(MAP_HEIGHT, MAP_WIDTH))

def create_level(level: int) -> None:
    esper.create_entity(Level(level))