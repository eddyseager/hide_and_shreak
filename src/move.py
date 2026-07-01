import esper
import tcod.path
import numpy as np
from components import *

def move_map(dx: int, dy: int, pos: Position) -> bool:
    _, dim = esper.get_component(MapDimension)[0]
    x = pos.x + dx
    y = pos.y + dy

    if dim.in_bounds(x, y) and not _blocks_movement(x, y):
        pos.x = x
        pos.y = y
        return True
    return False

def _blocks_movement(x: int, y: int):
    for e, (_, pos) in esper.get_components(Blocks_Movement, Position):
        if pos.x == x and pos.y == y:
            return True
    return False