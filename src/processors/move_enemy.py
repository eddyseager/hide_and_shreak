import esper
import tcod.path
import numpy as np
from components import *
from move import _blocks_movement

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
        if not player_query:
            return
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
                if new_x == player_pos.x and new_y == player_pos.y:
                    # Enemy hits player: deal damage, reset healing steps, and remove enemy
                    player.hp = max(0, player.hp - 1)
                    player.steps_since_hit = 0
                    esper.delete_entity(e)
                elif not _blocks_movement(new_x, new_y):
                    pos.x, pos.y = new_x, new_y
