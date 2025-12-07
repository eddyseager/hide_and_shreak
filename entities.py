import esper
from components import *
from random import Random

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

def load_level(level: str) -> None:
    with open(level) as file:
        x = 0
        y = 0
        for line in file:
            x =0
            for c in line:
                if c == '@':
                    create_player(x, y)
                elif ord(c) >= 0x2500 and ord(c) < 0x2600:
                    create_wall(x, y, c)
                x += 1
            y += 1

def create_player(x: int, y: int) -> None:
    player = esper.create_entity(Player(), Position(x, y), Graphic("@", (255, 255, 255)))

def create_wall(x: int, y: int, g: str) -> None:
    player = esper.create_entity(Wall(), Position(x, y), Graphic(g, (255, 255, 255)))

def create_map_dimension() -> None:
    esper.create_entity(MapDimension(MAP_HEIGHT, MAP_WIDTH))
