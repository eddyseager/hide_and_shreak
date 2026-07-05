import esper
from components import *
from tcod.map import compute_fov

class Update_FOV(esper.Processor):

    def process(self):
        _, (_, player_pos) = get_singleton_by_components(Player, Position)
        
        level_map = get_singleton(LevelMap)
        level_map.visible = compute_fov(level_map.transparent, (player_pos.x, player_pos.y), radius=10)
        level_map.explored |= level_map.visible