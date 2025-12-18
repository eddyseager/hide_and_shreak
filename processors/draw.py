import esper
from components import *
import tcod.console

class Draw(esper.Processor):
    
    def process(self):
        _, (_, player_pos, player_graphic, player_level) = esper.get_components(Player, Position, Graphic, Level)[0]
        for e, (fov, level) in esper.get_components(FOV, Level):
            if level == player_level:

                #Draw entities
                _, console = esper.get_component(tcod.console.Console)[0]
                for e, (pos, graphic) in esper.get_components(Position, Graphic):
                    if fov.visible[pos.x, pos.y]:
                        console.print(x=pos.x, y=pos.y, text=graphic.g, fg=graphic.fg)
                    elif fov.explored[pos.x, pos.y] and not esper.has_component(e, Enemy):
                        console.print(x=pos.x, y=pos.y, text=graphic.g, fg=(128, 128, 128))

                #Draw the player last
                console.print(x=player_pos.x, y=player_pos.y, text=player_graphic.g, fg=player_graphic.fg)