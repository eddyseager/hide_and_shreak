import esper
from components import *
import tcod.console
from tcod.map import compute_fov
import numpy as np

class Draw(esper.Processor):
    
    def process(self):
        #Recalculate FOV
        _, (_, player_pos, player_graphic) = esper.get_components(Player, Position, Graphic)[0]
        _, fov = esper.get_component(FOV)[0]
        visible = compute_fov(fov.transparent, (player_pos.x, player_pos.y), radius= 10)
        fov.explored |= visible

        #Draw entities
        _, console = esper.get_component(tcod.console.Console)[0]
        for e, (pos, graphic) in esper.get_components(Position, Graphic):
            if fov.explored[pos.x, pos.y]:
                console.print(x=pos.x, y=pos.y, text=graphic.g, fg=graphic.fg)

        #Draw the player last
        console.print(x=player_pos.x, y=player_pos.y, text=player_graphic.g, fg=player_graphic.fg)
