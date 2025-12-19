import esper
import tcod.path
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
    for e, (_, pos, d) in esper.get_components(PlayerMover, Position, Dijkstra):
        _, (_, player_pos, player_level) = esper.get_components(Player, Position, Level)[0]
        d.distance = tcod.path. maxarray((MAP_WIDTH, MAP_HEIGHT), dtype=np.int32, order="F")
        d.distance[player_pos.x, player_pos.y] = 0 #Player is goal

        for _, (fov, level) in esper.get_components(FOV, Level):
            if level == player_level:
                #print(d.distance)
                tcod.path.dijkstra2d(d.distance, fov.transparent, 2, 3, out=d.distance)
                #print(d.distance)
                path = tcod.path.hillclimb2d(d.distance, (pos.x, pos.y), True, False)
                list = path[1:].tolist()
                print(list)
                if list:
                    (pos.x, pos.y) = list.pop(0)