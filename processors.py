import esper
from components import *
import tcod.console

class Draw(esper.Processor):
    
    def process(self):
        _, console = esper.get_component(tcod.console.Console)[0]
        for e, (pos, graphic) in esper.get_components(Position, Graphic):
            console.print(x=pos.x, y=pos.y, text=graphic.g, fg=graphic.fg)