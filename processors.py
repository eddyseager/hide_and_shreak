import esper
from components import *
import tcod.console
from tcod.map import compute_fov
import numpy as np

class Draw(esper.Processor):
    
    def process(self):
        #Recalculate FOV for player's level - make this a separate process?
        _, (_, player_pos, player_graphic, player_level) = esper.get_components(Player, Position, Graphic, Level)[0]
        for e, (fov, level) in esper.get_components(FOV, Level):
            if level == player_level:
                visible = compute_fov(fov.transparent, (player_pos.x, player_pos.y), radius= 10)
                fov.explored |= visible

                #Draw entities
                _, console = esper.get_component(tcod.console.Console)[0]
                for e, (pos, graphic) in esper.get_components(Position, Graphic):
                    if visible[pos.x, pos.y]:
                        console.print(x=pos.x, y=pos.y, text=graphic.g, fg=graphic.fg)
                    elif fov.explored[pos.x, pos.y]:
                        console.print(x=pos.x, y=pos.y, text=graphic.g, fg=(128, 128, 128))

                #Draw the player last
                console.print(x=player_pos.x, y=player_pos.y, text=player_graphic.g, fg=player_graphic.fg)
