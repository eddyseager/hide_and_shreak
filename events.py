import esper
import tcod.event
from components import *
import tcod.console
from entities import create_level, remove_level, load_level, create_player


def on_event(event: tcod.event.Event) -> None:

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
        case tcod.event.KeyDown(sym=tcod.event.KeySym.PERIOD, mod=tcod.event.Modifier.LSHIFT):
            change_level_down()
        case tcod.event.KeyDown(sym=tcod.event.KeySym.PERIOD, mod=tcod.event.Modifier.RSHIFT):
            change_level_down()
        case tcod.event.KeyDown(sym=tcod.event.KeySym.COMMA, mod=tcod.event.Modifier.LSHIFT):
            change_level_up()
        case tcod.event.KeyDown(sym=tcod.event.KeySym.COMMA, mod=tcod.event.Modifier.RSHIFT):
            change_level_up()

def move_map(dx: int, dy: int) -> None:
    _, (_, pos) = esper.get_components(Player, Position)[0]
    _, dim = esper.get_component(MapDimension)[0]
    x = pos.x + dx
    y = pos.y + dy

    if dim.in_bounds(x, y) and not is_wall(x, y):
        pos.x = x
        pos.y = y

def is_wall(x: int, y: int):
    for e, (_, pos) in esper.get_components(Wall, Position):
        if pos.x == x and pos.y == y:
            return True
    return False

def change_level_down() -> None:
    #there might not be any stairs down
    try:
        _, (_, stair_pos) = esper.get_components(StairsDown, Position)[0]
    except IndexError:
        return

    _, (_, player_pos, player_level) = esper.get_components(Player, Position, Level)[0]
    if stair_pos == player_pos:
        remove_level()
        level = player_level.val + 1
        create_level(level)
        _, (_, stair_up) = esper.get_components(StairsUp, Position)[0]
        create_player(stair_up.x, stair_up.y, level)

def change_level_up() -> None:
    _, (_, stair_pos) = esper.get_components(StairsUp, Position)[0]
    _, (_, player_pos, player_level) = esper.get_components(Player, Position, Level)[0]
    if stair_pos == player_pos:
        #End the game if you leave the dungeon on level 0
        if player_level.val == 0:
            print("You go home for tea and biscuits.")
            raise SystemExit

        remove_level()
        level = player_level.val - 1
        load_level(level) #Assume moving up, levels are already created
        _, (_, stair_down) = esper.get_components(StairsDown, Position)[0]
        create_player(stair_down.x, stair_down.y, level)
