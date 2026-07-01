import esper
import tcod.path
import numpy as np
from components import *
from move import _blocks_movement, check_and_open_door

class Move_Enemy(esper.Processor):

    def __init__(self):
        super().__init__()
        self.last_processed_turn = 0

    def process(self):
        _, counter = esper.get_component(Counter)[0]
        if counter.val == self.last_processed_turn:
            return
        self.last_processed_turn = counter.val

        player_query = esper.get_components(Player, Position, Level)
        assert player_query, "Active player entity not found in ECS world during enemy movement phase!"
        _, (player, player_pos, player_level) = player_query[0]

        # Stop enemy AI if the player is dead
        if player.hp <= 0:
            return

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
            path = tcod.path.hillclimb2d(dist_map, (pos.x, pos.y), True, False)
            path_list = path[1:].tolist()
            if path_list:
                new_x, new_y = path_list[0]
                
                # Blocked by static environment (walls, doors, cages)
                is_blocked = _blocks_movement(new_x, new_y)
                if not is_blocked:
                    # Blocked by another enemy (excluding self)
                    for other_e, (_, other_pos) in esper.get_components(Enemy, Position):
                        if other_e != e and other_pos.x == new_x and other_pos.y == new_y:
                            is_blocked = True
                            break
                            
                if not is_blocked:
                    pos.x, pos.y = new_x, new_y
                    check_and_open_door(new_x, new_y)
