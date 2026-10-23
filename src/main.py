from __future__ import annotations

import esper
import pygame

# Initialize audio before importing game modules that load sound files.
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

from .components import Position, StartPoint
from .events import on_event
from .entities import create_player
from .level_setup import init_level_world
from .constants import *
from .rendering.ui_renderer import UIRenderer
from .resources import resource_path

def main() -> None:
    pygame.init()
    pygame.key.set_repeat(250, 130)

    # Play title music initially
    pygame.mixer.music.load(resource_path("music", "title.mp3"))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)

    # Initialize standard window size with RESIZABLE and SCALED flags.
    screen = pygame.display.set_mode((VIEW_WIDTH * TILE_SIZE, VIEW_HEIGHT * TILE_SIZE), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("Hide and shriek")
    clock = pygame.time.Clock()

    state = "TITLE"
    game_initialized = False
    ui_renderer = UIRenderer(screen, VIEW_WIDTH, VIEW_HEIGHT, TILE_SIZE)

    def start_game() -> None:
        nonlocal state, game_initialized
        state = "PLAYING"
        pygame.mixer.music.load(resource_path("music", "gameplay.mp3"))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

        if not game_initialized:
            level = 0
            esper.switch_world(f"level_{level}")
            init_level_world(level, screen, 0)

            _, (_, start_pos) = esper.get_components(StartPoint, Position)[0]
            create_player(start_pos.x, start_pos.y)
            game_initialized = True

    running = True
    while running:
        if state == "TITLE":
            title_action = ui_renderer.render_title_screen()
            if title_action == "play":
                start_game()
                ui_renderer.start_game_fade_in()
            elif title_action == "quit":
                running = False

            pygame.display.flip()
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == TOGGLE_DISPLAY_EVENT:
                    pygame.display.toggle_fullscreen()
                elif state == "TITLE":
                    ui_renderer.handle_title_event(event)
        elif state == "PLAYING":
            # Run ECS processing
            esper.process()

            # Fade in from the title screen after starting a new game.
            ui_renderer.render_game_fade_in()
            
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
