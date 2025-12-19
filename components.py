from dataclasses import dataclass as component
import numpy as np

MAP_WIDTH = 60
MAP_HEIGHT = 24
SPAWN_COUNT = 20

CHAR_PLAYER = "@"
CHAR_ENEMY = "&"
CHAR_SPAWN_POINT = "§"
CHAR_UP_STAIR = "<"
CHAR_DOWN_STAIR = ">"

#A visible object on the map (not a floor)
class Map_Object:
    pass

class Blocks_Movement:
    pass

class Player:
    pass

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
class Dijkstra:
    #Not sure if this is needed or if will be recomputed each time
    distance: np.ndarray

@component
class Counter:
    val: int