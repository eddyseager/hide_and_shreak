import esper
import tcod.event
from move import move_map
from components import *
import tcod.console
from entities import create_level, remove_level, load_level, create_player


def on_event(event: tcod.event.Event) -> None:

    match event:
        case tcod.event.Quit():
            raise SystemExit
        case tcod.event.KeyDown(sym=tcod.event.KeySym.LEFT):
            _move_player(-1, 0)
        case tcod.event.KeyDown(sym=tcod.event.KeySym.RIGHT):
            _move_player(1, 0)
        case tcod.event.KeyDown(sym=tcod.event.KeySym.UP):
            _move_player(0, -1)
        case tcod.event.KeyDown(sym=tcod.event.KeySym.DOWN):
            _move_player(0, 1)
        case tcod.event.KeyDown(sym=tcod.event.KeySym.PERIOD, mod=tcod.event.Modifier.LSHIFT):
            _change_level_down()
        case tcod.event.KeyDown(sym=tcod.event.KeySym.PERIOD, mod=tcod.event.Modifier.RSHIFT):
            _change_level_down()
        case tcod.event.KeyDown(sym=tcod.event.KeySym.COMMA, mod=tcod.event.Modifier.LSHIFT):
            _change_level_up()
        case tcod.event.KeyDown(sym=tcod.event.KeySym.COMMA, mod=tcod.event.Modifier.RSHIFT):
            _change_level_up()

def _move_player(dx: int, dy: int) -> None:
    _, (_, pos) = esper.get_components(Player, Position)[0]
    move_map(dx, dy, pos)

    e, counter = esper.get_component(Counter)[0]
    counter.val += 1

def _change_level_down() -> None:
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

def _change_level_up() -> None:
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
