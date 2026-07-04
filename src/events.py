import esper
import pygame
from move import move_map, check_and_open_door
from components import *
from entities import create_level, remove_level, load_level, create_player
from constants import TOGGLE_DISPLAY_EVENT, HEAL_STEPS

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

        if event.key == pygame.K_LEFT:
            _move_player(-1, 0)
        elif event.key == pygame.K_RIGHT:
            _move_player(1, 0)
        elif event.key == pygame.K_UP:
            _move_player(0, -1)
        elif event.key == pygame.K_DOWN:
            _move_player(0, 1)
        elif event.key == pygame.K_PERIOD:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_SHIFT:
                _change_level_down()
        elif event.key == pygame.K_COMMA:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_SHIFT:
                _change_level_up()
        elif event.key == pygame.K_ESCAPE:
            raise SystemExit
        elif event.key == pygame.K_f:
            pygame.event.post(pygame.event.Event(TOGGLE_DISPLAY_EVENT))

def _move_player(dx: int, dy: int) -> None:
    _, (player, pos) = esper.get_components(Player, Position)[0]
    
    if move_map(dx, dy, pos):
        # Open door if player stepped on one
        check_and_open_door(pos.x, pos.y)
        
        # Attach movement animation component to the player
        player_ent = esper.get_components(Player, Position)[0][0]
        esper.add_component(player_ent, MovementAnim(
            start_x=pos.x - dx,
            start_y=pos.y - dy,
            target_x=pos.x,
            target_y=pos.y,
            start_time=pygame.time.get_ticks()
        ))
        
        # Successful step: increment general turn counter
        e, counter = esper.get_component(Counter)[0]
        counter.val += 1

        # Healing logic: heals 1 HP every HEAL_STEPS steps if damaged (and not dead)
        if player.hp < player.max_hp and player.hp > 0:
            player.steps_since_hit += 1
            if player.steps_since_hit >= HEAL_STEPS:
                player.hp = min(player.max_hp, player.hp + 1)
                player.steps_since_hit = 0
        else:
            player.steps_since_hit = 0

def _change_level_down() -> None:
    #there might not be any stairs down
    try:
        _, (_, stair_pos) = esper.get_components(StairsDown, Position)[0]
    except IndexError:
        return

    _, game_maps = esper.get_component(GameMaps)[0]
    _, (_, player_pos) = esper.get_components(Player, Position)[0]
    if stair_pos == player_pos:
        remove_level()
        level = game_maps.active_level + 1
        create_level(level)
        _, (_, stair_up) = esper.get_components(StairsUp, Position)[0]
        create_player(stair_up.x, stair_up.y)

def _change_level_up() -> None:
    _, (_, stair_pos) = esper.get_components(StairsUp, Position)[0]
    _, game_maps = esper.get_component(GameMaps)[0]
    _, (_, player_pos) = esper.get_components(Player, Position)[0]
    if stair_pos == player_pos:
        # End the game if you leave the dungeon on level 0
        if game_maps.active_level == 0:
            print("You go home for tea and biscuits.")
            raise SystemExit

        remove_level()
        level = game_maps.active_level - 1
        create_level(level)
        _, (_, stair_down) = esper.get_components(StairsDown, Position)[0]
        create_player(stair_down.x, stair_down.y)
