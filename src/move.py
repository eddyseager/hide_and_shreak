import esper
import pygame
import tcod.path
import numpy as np
from tcod.map import compute_fov
from .components import *
from .resources import resource_path

door_sound = pygame.mixer.Sound(resource_path("sounds", "door.wav"))
door_sound.set_volume(0.3)

def move_map(dx: int, dy: int, pos: Position) -> bool:
    dim = get_singleton(MapDimension)
    x = pos.x + dx
    y = pos.y + dy

    if dim.in_bounds(x, y) and not blocks_movement(x, y):
        pos.x = x
        pos.y = y
        return True
    return False

def blocks_movement(x: int, y: int):
    level_map = get_singleton(LevelMap)
    return not level_map.walkable[x, y]

def check_and_open_door(x: int, y: int, player_opened: bool = False) -> None:
    for e, (pos, graphic) in esper.get_components(Position, Graphic):
        if pos.x == x and pos.y == y:
            if esper.has_component(e, ClosedDoor):
                # Swap component ClosedDoor -> OpenDoor
                esper.remove_component(e, ClosedDoor)
                esper.add_component(e, OpenDoor())
                graphic.col = 5  # Open door column (c5 r0)

                # Mark the door tile as transparent for the active level FOV
                level_map = get_singleton(LevelMap)
                level_map.transparent[x, y] = True

                # Only sound a newly opened door. Use a fresh FOV for enemies,
                # since the regular FOV processor may not have run this turn yet.
                _, (_, player_pos) = get_singleton_by_components(Player, Position)
                in_player_view = player_opened or compute_fov(
                    level_map.transparent, (player_pos.x, player_pos.y), radius=10
                )[x, y]
                if door_sound and in_player_view:
                    door_sound.play()
