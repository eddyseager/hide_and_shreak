import esper
import pygame
import random
from move import move_map, check_and_open_door
from components import *
from entities import create_player
from level_setup import init_level_world
from constants import TOGGLE_DISPLAY_EVENT
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
    player_ent, (player, pos) = get_singleton_by_components(Player, Position)
    old_x, old_y = pos.x, pos.y
    
    if move_map(dx, dy, pos):
        # Open door if player stepped on one
        check_and_open_door(pos.x, pos.y)
        
        # Drop blood on the previous tile if player is injured
        if player.hp < player.max_hp:
            hp_lost = player.max_hp - player.hp
            intensity = 1 if hp_lost == 1 else 2
                
            blood_graphic = Graphic(g=' ', fg=(150, 10, 10))
            seed = random.randint(0, 1000000)
            
            esper.create_entity(
                Blood(intensity=intensity, seed=seed),
                Position(x=old_x, y=old_y),
                blood_graphic
            )
        
        # Attach movement animation component to the player
        esper.add_component(player_ent, MovementAnim(
            start_x=pos.x - dx,
            start_y=pos.y - dy,
            target_x=pos.x,
            target_y=pos.y,
            start_time=pygame.time.get_ticks()
        ))
        
        # Successful step: increment general turn counter
        counter = get_singleton(Counter)
        counter.val += 1

def _change_level(next_level: int, spawn_on_stairs_type: type) -> None:
    player_ent, (player_comp, player_pos) = get_singleton_by_components(Player, Position)
    
    current_hp = player_comp.hp
    current_max_hp = player_comp.max_hp
    current_steps = player_comp.steps_since_hit
    current_just_hit = player_comp.just_hit

    counter = get_singleton(Counter)
    current_turn = counter.val

    draw_proc = esper.get_processor(Draw)
    screen = draw_proc.screen

    world_name = f"level_{next_level}"
    is_new_world = world_name not in esper.list_worlds()
    esper.switch_world(world_name)

    if is_new_world:
        init_level_world(next_level, screen, current_turn)

        _, (_, stair_pos) = get_singleton_by_components(spawn_on_stairs_type, Position)
        create_player(stair_pos.x, stair_pos.y)
    else:
        counter = get_singleton(Counter)
        counter.val = current_turn

        _, (_, p_pos) = get_singleton_by_components(Player, Position)
        _, (_, stair_pos) = get_singleton_by_components(spawn_on_stairs_type, Position)
        p_pos.x, p_pos.y = stair_pos.x, stair_pos.y

    # Sync player stats in the active world context
    p_comp = get_singleton(Player)
    p_comp.hp = current_hp
    p_comp.max_hp = current_max_hp
    p_comp.steps_since_hit = current_steps
    p_comp.just_hit = current_just_hit

def _change_level_down() -> None:
    try:
        _, (_, stair_pos) = esper.get_components(StairsDown, Position)[0]
    except IndexError:
        return

    _, (_, player_pos) = get_singleton_by_components(Player, Position)

    if stair_pos == player_pos:
        level_map = get_singleton(LevelMap)
        next_level = level_map.index + 1
        _change_level(next_level, StairsUp)

def _change_level_up() -> None:
    try:
        _, (_, stair_pos) = esper.get_components(StairsUp, Position)[0]
    except IndexError:
        return

    _, (_, player_pos) = get_singleton_by_components(Player, Position)

    if stair_pos == player_pos:
        level_map = get_singleton(LevelMap)
        current_level = level_map.index
        if current_level == 0:
            print("You go home for tea and biscuits.")
            raise SystemExit

        next_level = current_level - 1
        _change_level(next_level, StairsDown)
