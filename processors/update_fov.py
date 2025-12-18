import esper
from components import *
from tcod.map import compute_fov

class Update_FOV(esper.Processor):

    def process(self):
        _, (_, player_pos, player_level) = esper.get_components(Player, Position, Level)[0]
        for e, (fov, level) in esper.get_components(FOV, Level):
            if level == player_level:
                fov.visible = compute_fov(fov.transparent, (player_pos.x, player_pos.y), radius= 10)
                fov.explored |= fov.visible