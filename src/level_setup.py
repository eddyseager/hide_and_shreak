import esper
import pygame
from components import Counter
from constants import TILE_SIZE, VIEW_WIDTH, VIEW_HEIGHT
from entities import create_map_dimension, create_level
from processors.move_enemy import Move_Enemy
from processors.update_fov import Update_FOV
from processors.combat import Combat
from processors.spawn_enemy import Spawn_Enemy
from processors.draw import Draw

def init_level_world(level: int, screen: pygame.Surface, turn_counter_val: int = 0) -> None:
    # Register processors on the active world context
    esper.add_processor(Move_Enemy(), 6)
    esper.add_processor(Update_FOV(), 5)
    esper.add_processor(Combat(), 4)
    esper.add_processor(Spawn_Enemy(), 3)
    esper.add_processor(Draw(screen, TILE_SIZE, VIEW_WIDTH, VIEW_HEIGHT), 1)

    create_map_dimension()
    esper.create_entity(Counter(turn_counter_val))
    create_level(level)
