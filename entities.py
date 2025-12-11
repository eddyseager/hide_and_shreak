import esper
from components import *
from random import Random
import os
import numpy as np

#Some example entities
def create_entities():
    player = esper.create_entity(Player(), Position(MAP_WIDTH // 2, MAP_HEIGHT // 2), Graphic("@", (255, 255, 255)))
    
    #Add some walls
    for x in range (MAP_WIDTH) :
        esper.create_entity(Wall(), Position(x, 3), Graphic("─", (255, 255, 255)))
 
    #make some gold
    rng = Random()
    for _ in range(10):
        esper.create_entity(Gold(), Position(rng.randint(0, MAP_WIDTH), rng.randint(0, MAP_HEIGHT)), Graphic("$", (255, 255, 0)))

def load_level() -> None:
    _, level = esper.get_component(Level)[0]
    with open(f'levels{os.sep}{level.val}.level') as file:
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
                    create_wall(x, y, c)
                x += 1
            y += 1

def create_fov() -> None:
    #Create numpy array of walls to track transparency
    trans = np.ones((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
    exp = np.zeros((MAP_WIDTH, MAP_HEIGHT), dtype=bool, order="F")
    esper.create_entity(FOV(explored=exp, transparent=trans))

def remove_level() -> None:
    #Deletes all entities with a position component - may want to fix later for the player
    for e, _ in esper.get_component(Position):
        esper.delete_entity(e, True)

    e, _ = esper.get_component(FOV)[0]
    esper.delete_entity(e, True)
    create_fov()

def create_player(x: int, y: int) -> None:
    esper.create_entity(Player(), Position(x, y), Graphic("@", (255, 255, 255)))

def create_stairs_down(x: int, y: int) -> None:
    esper.create_entity(StairsDown(), Position(x, y), Graphic(">", (255, 255, 255)))

def create_stairs_up(x: int, y: int) -> None:
    esper.create_entity(StairsUp(), Position(x, y), Graphic("<", (255, 255, 255)))

def create_wall(x: int, y: int, g: str) -> None:
    esper.create_entity(Wall(), Position(x, y), Graphic(g, (255, 255, 255)))

    #Walls are not transparent
    _, fov = esper.get_component(FOV)[0]
    fov.transparent[x, y] = False

def create_map_dimension() -> None:
    esper.create_entity(MapDimension(MAP_HEIGHT, MAP_WIDTH))

def create_level() -> None:
    esper.create_entity(Level(0))