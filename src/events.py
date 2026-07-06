import esper
import pygame
from constants import TOGGLE_DISPLAY_EVENT
from components import Player
import player_events

def on_event(event: pygame.event.Event) -> None:
    if event.type == pygame.KEYDOWN:
        # Check player health for Game Over
        try:
            _, player = esper.get_component(Player)[0]
            is_dead = player.hp <= 0
        except IndexError:
            is_dead = False

        if is_dead:
            if event.key == pygame.K_ESCAPE:
                raise SystemExit
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            player_events.move_player(0, -1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            player_events.move_player(0, 1)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            player_events.move_player(-1, 0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            player_events.move_player(1, 0)
        elif event.key == pygame.K_PERIOD:
            player_events.change_level_down()
        elif event.key == pygame.K_COMMA:
            player_events.change_level_up()
        elif event.key == pygame.K_ESCAPE:
            raise SystemExit
        elif event.key == pygame.K_f:
            pygame.event.post(pygame.event.Event(TOGGLE_DISPLAY_EVENT))
