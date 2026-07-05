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
    _, level_map = esper.get_component(LevelMap)[0]
    return not level_map.walkable[x, y]

def check_and_open_door(x: int, y: int) -> None:
    for e, (_, pos, graphic) in esper.get_components(ClosedDoor, Position, Graphic):
        if pos.x == x and pos.y == y:
            # Swap component ClosedDoor -> OpenDoor
            esper.remove_component(e, ClosedDoor)
            esper.add_component(e, OpenDoor())
            graphic.col = 5  # Open door column (c5 r0)

            # Mark the door tile as transparent for the active level FOV
            _, level_map = esper.get_component(LevelMap)[0]
            level_map.transparent[x, y] = True