import esper
import pygame
import tcod.path
from tcod.map import compute_fov
import numpy as np
import random
from components import *
from move import blocks_movement, check_and_open_door

class Move_Enemy(esper.Processor):

    def __init__(self):
        super().__init__()
        self.last_processed_turn = 0

    def process(self):
        _, counter = esper.get_component(Counter)[0]
        #We only move on even turns
        if counter.val == self.last_processed_turn or counter.val % 2 != 0:
            return
        self.last_processed_turn = counter.val

        player_query = esper.get_components(Player, Position)
        assert player_query, "Active player entity not found in ECS world during enemy movement phase!"
        _, (player, player_pos) = player_query[0]

        # Stop enemy AI if the player is dead
        if player.hp <= 0:
            return

        _, active_map = esper.get_component(LevelMap)[0]
        walkable = active_map.walkable
        transparent = active_map.transparent

        # Process FOV updates and movement for all enemies
        for e, (_, pos, enemy_ai) in esper.get_components(PlayerMover, Position, EnemyAI):
            # Update FOV
            visible = compute_fov(transparent, (pos.x, pos.y), radius=enemy_ai.fov_radius)
            enemy_ai.explored |= visible

            # Check player visibility
            if visible[player_pos.x, player_pos.y]:
                enemy_ai.state = "chase"
            else:
                enemy_ai.state = "explore"

            # Determine target and compute distance map
            # Build a walkable grid that treats other enemies as obstacles
            blocking_walkable = walkable.copy()
            for other_e, (_, other_pos) in esper.get_components(Enemy, Position):
                if other_e != e:
                    blocking_walkable[other_pos.x, other_pos.y] = False

            dist_map = tcod.path.maxarray((MAP_WIDTH, MAP_HEIGHT), dtype=np.int32, order="F")
            
            if enemy_ai.state == "chase":
                dist_map[player_pos.x, player_pos.y] = 0
            else:
                unexplored_walkable = blocking_walkable & (~enemy_ai.explored)
                if np.any(unexplored_walkable):
                    dist_map[unexplored_walkable] = 0
                else:
                    # Map is fully explored! Stand still.
                    continue

            tcod.path.dijkstra2d(dist_map, blocking_walkable, 2, 3, out=dist_map)

            # Hillclimb to find next step
            path = tcod.path.hillclimb2d(dist_map, (pos.x, pos.y), True, False)
            path_list = path[1:].tolist()

            if path_list:
                new_x, new_y = path_list[0]
                
                # Move enemy
                old_x, old_y = pos.x, pos.y
                pos.x, pos.y = new_x, new_y
                check_and_open_door(new_x, new_y)
                
                # Add movement animation
                esper.add_component(e, MovementAnim(
                    start_x=old_x, start_y=old_y, target_x=new_x, target_y=new_y,
                    start_time=pygame.time.get_ticks(), duration=350
                ))
