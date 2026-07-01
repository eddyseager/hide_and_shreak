from dataclasses import dataclass as component
import numpy as np
from constants import MAP_WIDTH, MAP_HEIGHT, SPAWN_COUNT


#A visible object on the map (not a floor)
class Map_Object:
    pass

class Blocks_Movement:
    pass

@component
class Player:
    hp: int = 3
    max_hp: int = 3
    steps_since_hit: int = 0
    just_hit: bool = False

class Wall:
    pass

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
class Level:
    val: int

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
class FOV:
    transparent: np.ndarray
    explored: np.ndarray
    visible: np.ndarray

@component
class Counter:
    val: int