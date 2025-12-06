import esper
import tcod.event
from components import *
import tcod.console


def on_event(event: tcod.event.Event) -> None:
    """Move the player on events and handle exiting. Movement is hard-coded."""

    match event:
        case tcod.event.Quit():
            raise SystemExit
        case tcod.event.KeyDown(sym=tcod.event.KeySym.LEFT):
            move_map(-1, 0)
        case tcod.event.KeyDown(sym=tcod.event.KeySym.RIGHT):
            move_map(1, 0)
        case tcod.event.KeyDown(sym=tcod.event.KeySym.UP):
            move_map(0, -1)
        case tcod.event.KeyDown(sym=tcod.event.KeySym.DOWN):
            move_map(0, 1)

def move_map(dx: int, dy: int) -> None:
    _, (_, pos) = esper.get_components(Player, Position)[0]
    _, dim = esper.get_component(MapDimension)[0]
    x = pos.x + dx
    y = pos.y + dy

    if dim.in_bounds(x, y):
        pos.x = x
        pos.y = y