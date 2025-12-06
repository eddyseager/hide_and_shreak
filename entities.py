import esper
from components import *
from random import Random

def create_entities():
    esper.create_entity(MapDimension(MAP_HEIGHT, MAP_WIDTH))
    player = esper.create_entity(Player(), Position(MAP_WIDTH // 2, MAP_HEIGHT // 2), Graphic("@", (255, 255, 255)))
    
    #Add some walls
    for x in range (MAP_WIDTH) :
        esper.create_entity(Wall(), Position(x, 3), Graphic("#", (255, 255, 255)))
 
    #make some gold
    rng = Random()
    for _ in range(10):
        esper.create_entity(Gold(), Position(rng.randint(0, MAP_WIDTH), rng.randint(0, MAP_HEIGHT)), Graphic("$", (255, 255, 0)))