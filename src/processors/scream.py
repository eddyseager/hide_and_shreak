import esper
import pygame
from ..components import Enemy, Player, Position, ScreamEffect
from ..constants import SCREAM_CHARGE_REQUIRED


class Scream(esper.Processor):
    def process(self):
        effect_query = esper.get_component(ScreamEffect)
        if not effect_query:
            return

        _, effect = effect_query[0]
        if effect.damage_complete:
            return

        player_query = esper.get_component(Player)
        if not player_query:
            return
        player = player_query[0][1]

        elapsed = pygame.time.get_ticks() - effect.start_time
        progress = min(1.0, elapsed / effect.wave_duration)
        wave_radius = effect.radius * progress
        wave_radius_squared = wave_radius * wave_radius

        for enemy_ent, (_, enemy_pos) in esper.get_components(Enemy, Position):
            dx = enemy_pos.x - effect.center_x
            dy = enemy_pos.y - effect.center_y
            if dx * dx + dy * dy <= wave_radius_squared:
                esper.delete_entity(enemy_ent, immediate=True)
                player.scream_charge = min(
                    SCREAM_CHARGE_REQUIRED,
                    player.scream_charge + 1,
                )

        if progress >= 1.0:
            effect.damage_complete = True
