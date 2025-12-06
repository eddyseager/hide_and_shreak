from dataclasses import dataclass as component

MAP_WIDTH = 60
MAP_HEIGHT = 24

class Player:
    pass

class Gold:
    pass

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