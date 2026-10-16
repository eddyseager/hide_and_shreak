import esper
import pygame
import random
from ..components import *
from ..resources import resource_path
from tcod.map import compute_fov

class Update_FOV(esper.Processor):
    def __init__(self):
        super().__init__()
        self.visible_enemies = set()
        self.roar_sounds = [
            pygame.mixer.Sound(resource_path("sounds", filename))
            for filename in ("roar1.wav", "roar2.wav", "roar3.wav", "roar4.wav", "roar5.wav")
        ]

    def process(self):
        _, (_, player_pos) = get_singleton_by_components(Player, Position)
        
        level_map = get_singleton(LevelMap)
        level_map.visible = compute_fov(level_map.transparent, (player_pos.x, player_pos.y), radius=10)
        level_map.explored |= level_map.visible

        visible_enemies = set()
        for enemy_ent, (_, enemy_pos) in esper.get_components(Enemy, Position):
            if level_map.visible[enemy_pos.x, enemy_pos.y]:
                visible_enemies.add(enemy_ent)
                if enemy_ent not in self.visible_enemies:
                    random.choice(self.roar_sounds).play()
        self.visible_enemies = visible_enemies
