import esper
from components import *

class Combat(esper.Processor):
    def process(self):
        player_query = esper.get_components(Player, Position)
        assert player_query, "Active player entity not found in ECS world during combat phase!"
        _, (player, player_pos) = player_query[0]

        # Stop combat checks if the player is already dead
        if player.hp <= 0:
            return

        # Find any enemy occupying the same position as the player
        for e, (_, pos) in esper.get_components(Enemy, Position):
            if pos.x == player_pos.x and pos.y == player_pos.y:
                # Combat exchange
                player.hp = max(0, player.hp - 1)
                player.steps_since_hit = 0
                player.just_hit = True
                esper.delete_entity(e)
