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

def check_and_open_door(x: int, y: int) -> None:
    for e, (door, pos, graphic) in esper.get_components(Door, Position, Graphic):
        if pos.x == x and pos.y == y and not door.is_open:
            door.is_open = True
            graphic.col = 5  # Open door column (c5 r0)

            # Mark the door tile as transparent for the active level FOV
            player_query = esper.get_components(Player, Level)
            if player_query:
                _, (_, player_level) = player_query[0]
                for _, (fov, l) in esper.get_components(FOV, Level):
                    if l.val == player_level.val:
                        fov.transparent[x, y] = True