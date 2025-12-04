from __future__ import annotations

import tcod.console
import tcod.context
import tcod.event
import tcod.tileset
from dataclasses import dataclass as component
import esper

@component
class Position:
    x: int
    y: int

@component
class Graphic:
    g: str

@component
class Draw(esper.Processor):
    
    def process(self):
        _, console = esper.get_component(tcod.console.Console)[0]
        for e, (pos, graphic) in esper.get_components(Position, Graphic):
            console.print(pos.x, pos.y, graphic.g)
        
def on_event(event: tcod.event.Event) -> None:
    """Move the player on events and handle exiting. Movement is hard-coded."""
    _, pos = esper.get_component(Position)[0]
    match event:
        case tcod.event.Quit():
            raise SystemExit
        case tcod.event.KeyDown(sym=tcod.event.KeySym.LEFT):
            pos.x -= 1
        case tcod.event.KeyDown(sym=tcod.event.KeySym.RIGHT):
            pos.x += 1
        case tcod.event.KeyDown(sym=tcod.event.KeySym.UP):
            pos.x -= 1
        case tcod.event.KeyDown(sym=tcod.event.KeySym.DOWN):
            pos.y += 1

def main() -> None:
    tileset = tcod.tileset.load_tilesheet(
        "Oddball_16x16.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    console = tcod.console.Console(80, 50)
    esper.create_entity(console)
    player = esper.create_entity(Position(console.width // 2, console.height // 2), Graphic("@"))
    esper.add_processor(Draw())
    esper.set_handler('tcod_event', on_event)

    with tcod.context.new(console=console, tileset=tileset) as context:
        while True:  # Main loop
            console.clear()  # Clear the console before any drawing
            esper.process()
            context.present(console)  # Display the console on the window
            for event in tcod.event.wait():  # Event loop, blocks until pending events exist
                esper.dispatch_event('tcod_event', event)  # Pass events to the state


if __name__ == "__main__":
    main()