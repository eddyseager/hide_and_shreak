from dataclasses import dataclass as component
import numpy as np
import esper
from constants import MAP_WIDTH, MAP_HEIGHT, SPAWN_COUNT


#A visible object on the map (not a floor)
class Map_Object:
    pass

class Blocks_FOV:
    pass

class Blocks_Movement(Blocks_FOV):
    pass

@component
class Player:
    hp: int = 3
    max_hp: int = 3
    steps_since_hit: int = 0
    just_hit: bool = False

class Wall:
    pass

@component
class ClosedDoor:
    pass

@component
class OpenDoor:
    pass

@component
class MovementAnim:
    start_x: int
    start_y: int
    target_x: int
    target_y: int
    start_time: int
    duration: int = 150

@component
class EnemyAI:
    state: str = "explore"
    explored: np.ndarray = None
    fov_radius: int = 5

class Floor:
    pass

class StairsDown:
    pass

class StairsUp:
    pass

class Enemy:
    pass

class SpawnPoint:
    pass

class PlayerMover:
    pass

@component
class Position:
    x: int
    y: int

@component
class Graphic:
    g: str
    fg: tuple[int, int, int]
    sheet: str = ""
    col: int = 0
    row: int = 0

@component
class MapDimension:
    height: int
    width: int

    def in_bounds(self, x: int, y: int) -> bool:
        return x >= 0 and x < self.width and y >= 0 and y < self.height

@component
class LevelMap:
    transparent: np.ndarray
    explored: np.ndarray
    visible: np.ndarray
    walkable: np.ndarray = None
    index: int = 0



@component
class Counter:
    val: int

def get_singleton(comp_type):
    query = esper.get_component(comp_type)
    assert query, f"Required singleton {comp_type.__name__} not found in ECS world!"
    return query[0][1]

def get_singleton_entity(comp_type):
    query = esper.get_component(comp_type)
    assert query, f"Required singleton {comp_type.__name__} not found in ECS world!"
    return query[0]

def get_singleton_by_components(*comp_types):
    query = esper.get_components(*comp_types)
    assert query, f"Required singleton with components {[c.__name__ for c in comp_types]} not found in ECS world!"
    return query[0]