from __future__ import annotations

import os
import esper
import pygame
from random import Random
from components import *
from events import on_event
from entities import create_player
from level_setup import init_level_world
from constants import *

def main() -> None:
    # Pre-initialize the mixer with a low buffer size (512 bytes) to eliminate SFX latency
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("music/gameplay.mp3")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)

    # Initialize standard window size with RESIZABLE and SCALED flags.
    # This creates a virtual 1280x640 canvas that scales dynamically to fill any window or fullscreen Space.
    screen = pygame.display.set_mode((VIEW_WIDTH * TILE_SIZE, VIEW_HEIGHT * TILE_SIZE), pygame.RESIZABLE | pygame.SCALED)

    pygame.display.set_caption("Hide and Shreak")
    clock = pygame.time.Clock()

    level = 0
    esper.switch_world(f"level_{level}")
    init_level_world(level, screen, 0)

    _, (_, stair_up) = esper.get_components(StairsUp, Position)[0]
    create_player(stair_up.x, stair_up.y)

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