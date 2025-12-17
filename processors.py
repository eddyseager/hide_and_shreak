import esper
from components import *
import tcod.console
from tcod.map import compute_fov
import numpy as np
import random as rng
from entities import create_enemy

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
                    elif fov.explored[pos.x, pos.y]:
                        console.print(x=pos.x, y=pos.y, text=graphic.g, fg=(128, 128, 128))

                #Draw the player last
                console.print(x=player_pos.x, y=player_pos.y, text=player_graphic.g, fg=player_graphic.fg)

class Update_FOV(esper.Processor):
    def process(self):
        _, (_, player_pos, player_level) = esper.get_components(Player, Position, Level)[0]
        for e, (fov, level) in esper.get_components(FOV, Level):
            if level == player_level:
                fov.visible = compute_fov(fov.transparent, (player_pos.x, player_pos.y), radius= 10)
                fov.explored |= fov.visible

class Monster_Spawn(esper.Processor):
    def process(self):
        e, counter = esper.get_component(Counter)[0]
        if counter.val == SPAWN_COUNT:
            counter.val = 0

            pos = self.spawn_at()
            if pos:
                create_enemy(pos.x, pos.y)

    def spawn_at(self) -> Position:
        spawns = esper.get_components(SpawnPoint, Position)

        while (len(spawns) > 0):

            #Get a random spawn point
            i = rng.randrange(len(spawns))
            _, (_, spawn) = spawns.pop(i)

            positions = esper.get_components(Position, Map_Object)

            #bools track if anything is next to the spawn point
            below = True
            left = True
            right = True
            above = True

            for _, (pos, _) in positions :
                if spawn.y + 1 == pos.y and spawn.x == pos.x:
                    below = False
                elif spawn.y - 1 == pos.y and spawn.x == pos.x:
                    above = False
                elif spawn.y == pos.y and spawn.x + 1 == pos.x:
                    right = False
                elif spawn.y == pos.y and spawn.x - 1 == pos.x:
                    left = False

            if below:
                return Position(spawn.x, spawn.y + 1)
            elif above:
                return Position(spawn.x, spawn.y -1)
            elif right:
                return Position(spawn.x + 1, spawn.y)
            elif left:
                return Position(spawn.x - 1, spawn.y)

        return None
