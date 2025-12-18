from typing import Optional
import esper
from components import *
import random as rng
from entities import create_enemy

class Spawn_Enemy(esper.Processor):

    def process(self):
        e, counter = esper.get_component(Counter)[0]
        if counter.val == SPAWN_COUNT:
            counter.val = 0

            pos = self._spawn_at()
            if pos:
                create_enemy(pos.x, pos.y)

    def _spawn_at(self) -> Optional[Position]:
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
