import esper
import tcod.path
import numpy as np
from components import *

def move_map(dx: int, dy: int, pos: Position) -> None:
    _, dim = esper.get_component(MapDimension)[0]
    x = pos.x + dx
    y = pos.y + dy

    if dim.in_bounds(x, y) and not _blocks_movement(x, y):
        pos.x = x
        pos.y = y

def _blocks_movement(x: int, y: int):
    for e, (_, pos) in esper.get_components(Blocks_Movement, Position):
        if pos.x == x and pos.y == y:
            return True
    return False

def move_to_player():
    player_query = esper.get_components(Player, Position, Level)
    if not player_query:
        return
    _, (_, player_pos, player_level) = player_query[0]

    # Find FOV for the player's level
    current_fov = None
    for _, (fov, level) in esper.get_components(FOV, Level):
        if level.val == player_level.val:
            current_fov = fov
            break

    if not current_fov:
        return

    # Compute Dijkstra map once for the current player position
    dist_map = tcod.path.maxarray((MAP_WIDTH, MAP_HEIGHT), dtype=np.int32, order="F")
    dist_map[player_pos.x, player_pos.y] = 0
    tcod.path.dijkstra2d(dist_map, current_fov.transparent, 2, 3, out=dist_map)

    for e, (_, pos) in esper.get_components(PlayerMover, Position):
        # Optional: Check if enemy is on the same level as the player if/when enemies have Level components
        path = tcod.path.hillclimb2d(dist_map, (pos.x, pos.y), True, False)
        path_list = path[1:].tolist()
        if path_list:
            new_x, new_y = path_list[0]
            if not _blocks_movement(new_x, new_y):
                pos.x, pos.y = new_x, new_y