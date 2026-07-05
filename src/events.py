import esper
import pygame
from move import move_map, check_and_open_door
from components import *
from entities import create_player
from level_setup import init_level_world
from constants import TOGGLE_DISPLAY_EVENT, HEAL_STEPS
from processors.draw import Draw

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

def _change_level(next_level: int, spawn_on_stairs_type: type) -> None:
    player_query = esper.get_components(Player, Position)
    assert player_query, "Player not found before level transition!"
    player_ent, (player_comp, player_pos) = player_query[0]
    
    current_hp = player_comp.hp
    current_max_hp = player_comp.max_hp
    current_steps = player_comp.steps_since_hit
    current_just_hit = player_comp.just_hit

    _, counter = esper.get_component(Counter)[0]
    current_turn = counter.val

    draw_proc = esper.get_processor(Draw)
    screen = draw_proc.screen

    world_name = f"level_{next_level}"
    is_new_world = world_name not in esper.list_worlds()
    esper.switch_world(world_name)

    if is_new_world:
        init_level_world(next_level, screen, current_turn)

        _, (_, stair_pos) = esper.get_components(spawn_on_stairs_type, Position)[0]
        create_player(stair_pos.x, stair_pos.y)
    else:
        _, counter = esper.get_component(Counter)[0]
        counter.val = current_turn

        _, (_, p_pos) = esper.get_components(Player, Position)[0]
        _, (_, stair_pos) = esper.get_components(spawn_on_stairs_type, Position)[0]
        p_pos.x, p_pos.y = stair_pos.x, stair_pos.y

    # Sync player stats in the active world context
    _, p_comp = esper.get_component(Player)[0]
    p_comp.hp = current_hp
    p_comp.max_hp = current_max_hp
    p_comp.steps_since_hit = current_steps
    p_comp.just_hit = current_just_hit

def _change_level_down() -> None:
    try:
        _, (_, stair_pos) = esper.get_components(StairsDown, Position)[0]
    except IndexError:
        return

    _, (_, player_pos) = esper.get_components(Player, Position)[0]
    if stair_pos == player_pos:
        _, level_map = esper.get_component(LevelMap)[0]
        next_level = level_map.index + 1
        _change_level(next_level, StairsUp)

def _change_level_up() -> None:
    try:
        _, (_, stair_pos) = esper.get_components(StairsUp, Position)[0]
    except IndexError:
        return

    _, (_, player_pos) = esper.get_components(Player, Position)[0]
    if stair_pos == player_pos:
        _, level_map = esper.get_component(LevelMap)[0]
        current_level = level_map.index
        if current_level == 0:
            print("You go home for tea and biscuits.")
            raise SystemExit

        next_level = current_level - 1
        _change_level(next_level, StairsDown)
