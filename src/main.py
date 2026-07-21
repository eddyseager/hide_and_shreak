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
from rendering.ui_renderer import UIRenderer

def main() -> None:
    # Pre-initialize the mixer with a low buffer size (512 bytes) to eliminate SFX latency
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()
    pygame.key.set_repeat(250, 130)

    # Play title music initially
    pygame.mixer.music.load("music/title.mp3")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)

    # Initialize standard window size with RESIZABLE and SCALED flags.
    screen = pygame.display.set_mode((VIEW_WIDTH * TILE_SIZE, VIEW_HEIGHT * TILE_SIZE), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("Hide and Shreak")
    clock = pygame.time.Clock()

    state = "TITLE"
    game_initialized = False
    ui_renderer = UIRenderer(screen, VIEW_WIDTH, VIEW_HEIGHT, TILE_SIZE)

    running = True
    while running:
        if state == "TITLE":
            ui_renderer.render_title_screen()
            pygame.display.flip()
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == TOGGLE_DISPLAY_EVENT:
                    pygame.display.toggle_fullscreen()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Switch to gameplay state & start gameplay music
                        state = "PLAYING"
                        pygame.mixer.music.load("music/gameplay.mp3")
                        pygame.mixer.music.set_volume(0.4)
                        pygame.mixer.music.play(-1)

                        if not game_initialized:
                            level = 0
                            esper.switch_world(f"level_{level}")
                            init_level_world(level, screen, 0)

                            _, (_, start_pos) = esper.get_components(StartPoint, Position)[0]
                            create_player(start_pos.x, start_pos.y)
                            game_initialized = True
                    elif event.key == pygame.K_ESCAPE:
                        running = False
        elif state == "PLAYING":
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