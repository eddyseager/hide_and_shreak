from __future__ import annotations

import os
import esper
import pygame
from random import Random
from components import *
from events import on_event
from entities import *
from processors.draw import Draw
from processors.update_fov import Update_FOV
from processors.spawn_enemy import Spawn_Enemy
from processors.move_enemy import Move_Enemy
from processors.combat import Combat
from constants import *

def main() -> None:
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("music/gameplay.mp3")
    pygame.mixer.music.play(-1)

    # Initialize standard window size with RESIZABLE and SCALED flags.
    # This creates a virtual 1280x640 canvas that scales dynamically to fill any window or fullscreen Space.
    screen = pygame.display.set_mode((VIEW_WIDTH * TILE_SIZE, VIEW_HEIGHT * TILE_SIZE), pygame.RESIZABLE | pygame.SCALED)

    pygame.display.set_caption("Hide and Shreak")
    clock = pygame.time.Clock()

    level = 0
    create_map_dimension()
    create_level(level)
    _, (_, stair_up) = esper.get_components(StairsUp, Position)[0]
    create_player(stair_up.x, stair_up.y, level)
    create_counter()
    
    esper.add_processor(Move_Enemy(), 6)
    esper.add_processor(Update_FOV(), 5)
    esper.add_processor(Combat(), 4)
    esper.add_processor(Spawn_Enemy(), 3)
    esper.add_processor(Draw(screen, TILE_SIZE, VIEW_WIDTH, VIEW_HEIGHT), 1)

    running = True
    while running:
        # Run ECS processing
        esper.process()
        
        # Present screen
        pygame.display.flip()
        
        # Limit frame rate
        clock.tick(30)

        # Handle inputs and events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == TOGGLE_DISPLAY_EVENT:
                pygame.display.toggle_fullscreen()
                
            elif event.type == pygame.KEYDOWN:
                on_event(event)

    pygame.quit()

if __name__ == "__main__":
    main()