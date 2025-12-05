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
    fg: tuple[int, int, int]

@component
class MapDimension:
    height: int
    width: int

    def in_bounds(self, x: int, y: int) -> bool:
        return x >= 0 and x < self.width and y >= 0 and y < self.height

class Draw(esper.Processor):
    
    def process(self):
        _, console = esper.get_component(tcod.console.Console)[0]
        for e, (pos, graphic) in esper.get_components(Position, Graphic):
            console.print(x=pos.x, y=pos.y, text=graphic.g, fg=graphic.fg)
        
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
    _, pos = esper.get_component(Position)[0]
    _, dim = esper.get_component(MapDimension)[0]
    x = pos.x + dx
    y = pos.y + dy

    if dim.in_bounds(x, y):
        pos.x = x
        pos.y = y

def main() -> None:
    map_width = 80
    map_height = 50

    tileset = tcod.tileset.load_tilesheet(
        "Oddball_16x16.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    console = tcod.console.Console(map_width, map_height, order="F")
    esper.create_entity(MapDimension(map_height, map_width))
    esper.create_entity(console)
    player = esper.create_entity(Position(console.width // 2, console.height // 2), Graphic("@", (255, 0, 0)))
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