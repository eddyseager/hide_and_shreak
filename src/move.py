import esper
import tcod.path
import numpy as np
from components import *

def move_map(dx: int, dy: int, pos: Position) -> bool:
    _, dim = esper.get_component(MapDimension)[0]
    x = pos.x + dx
    y = pos.y + dy

    if dim.in_bounds(x, y) and not blocks_movement(x, y):
        pos.x = x
        pos.y = y
        return True
    return False

def blocks_movement(x: int, y: int):
    _, game_maps = esper.get_component(GameMaps)[0]
    active_map = game_maps.levels[game_maps.active_level]
    return not active_map.walkable[x, y]

def check_and_open_door(x: int, y: int) -> None:
    for e, (door, pos, graphic) in esper.get_components(Door, Position, Graphic):
        if pos.x == x and pos.y == y and not door.is_open:
            door.is_open = True
            graphic.col = 5  # Open door column (c5 r0)
            
            # Remove Blocks_FOV component since the door is now open and transparent
            if esper.has_component(e, Blocks_FOV):
                esper.remove_component(e, Blocks_FOV)

            # Mark the door tile as transparent for the active level FOV
            _, game_maps = esper.get_component(GameMaps)[0]
            active_map = game_maps.levels[game_maps.active_level]
            active_map.transparent[x, y] = True