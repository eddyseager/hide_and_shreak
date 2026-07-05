import esper
from components import *
from tcod.map import compute_fov

class Update_FOV(esper.Processor):

    def process(self):
        player_query = esper.get_components(Player, Position)
        assert player_query, "Active player entity not found in ECS world during FOV update phase!"
        _, (_, player_pos) = player_query[0]
        
        _, level_map = esper.get_component(LevelMap)[0]
        level_map.visible = compute_fov(level_map.transparent, (player_pos.x, player_pos.y), radius=10)
        level_map.explored |= level_map.visible