import esper
import pygame
import random
from ..components import *
from ..resources import resource_path

class Combat(esper.Processor):
    def __init__(self):
        super().__init__()
        self.hit_sounds = []
        for filename in ("explosion.wav", "explosion2.wav", "explosion3.wav"):
            try:
                self.hit_sounds.append(pygame.mixer.Sound(resource_path("sounds", filename)))
            except (pygame.error, FileNotFoundError):
                pass
            
        try:
            self.die_sound = pygame.mixer.Sound(resource_path("sounds", "die.wav"))
        except (pygame.error, FileNotFoundError):
            self.die_sound = None

    def process(self):
        player_query = esper.get_components(Player, Position)
        assert player_query, "Active player entity not found in ECS world during combat phase!"
        _, (player, player_pos) = player_query[0]

        # Stop combat checks if the player is already dead
        if player.hp <= 0:
            return

        # Find any enemy occupying the same position as the player
        for e, (_, pos) in esper.get_components(Enemy, Position):
            if pos.x == player_pos.x and pos.y == player_pos.y:
                # Combat exchange
                player.hp = max(0, player.hp - 1)
                player.steps_since_hit = 0
                player.just_hit = True
                
                # Play corresponding sound effect based on remaining HP
                if player.hp <= 0:
                    if self.die_sound:
                        self.die_sound.play()
                else:
                    if self.hit_sounds:
                        random.choice(self.hit_sounds).play()
                    
                esper.delete_entity(e)
