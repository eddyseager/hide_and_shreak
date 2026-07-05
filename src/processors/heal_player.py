import esper
from components import *
from constants import HEAL_STEPS

class HealPlayer(esper.Processor):
    def __init__(self):
        super().__init__()
        self.last_processed_turn = 0

    def process(self):
        counter = get_singleton(Counter)
        if counter.val == self.last_processed_turn:
            return
        self.last_processed_turn = counter.val

        player = get_singleton(Player)

        # Healing logic: heals 1 HP every HEAL_STEPS steps if damaged (and not dead)
        if 0 < player.hp < player.max_hp:
            player.steps_since_hit += 1
            if player.steps_since_hit >= HEAL_STEPS:
                player.hp = min(player.max_hp, player.hp + 1)
                player.steps_since_hit = 0
        else:
            player.steps_since_hit = 0
