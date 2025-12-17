from __future__ import annotations

import tcod.console
import tcod.context
import tcod.event
import tcod.tileset
import esper
from random import Random
from components import *
from events import on_event
from processors import *
from entities import *

def main() -> None:

    tileset = tcod.tileset.load_tilesheet(
        "fonts/Redjack17.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    console = tcod.console.Console(MAP_WIDTH, MAP_HEIGHT, order="F")
    esper.create_entity(console)

    level = 0
    create_map_dimension()
    create_level(level)
    _, (_, stair_up) = esper.get_components(StairsUp, Position)[0]
    create_player(stair_up.x, stair_up.y, level)
    create_counter()
    esper.add_processor(Draw(), 5)
    esper.add_processor(Update_FOV(), 3)
    esper.add_processor(Monster_Spawn(), 2)
    esper.set_handler('tcod_event', on_event)

    with tcod.context.new(tileset=tileset, sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED) as context:

        while True:  # Main loop
            console.clear()  # Clear the console before any drawing
            esper.process()
            context.present(console, keep_aspect=True, integer_scaling=False)  # Display the console on the window
            for event in tcod.event.wait():  # Event loop, blocks until pending events exist
                esper.dispatch_event('tcod_event', event)  # Pass events to the state


if __name__ == "__main__":
    main()