import esper
import pygame
from components import *

class Draw(esper.Processor):
    def __init__(self, screen, tile_size=22):
        super().__init__()
        self.screen = screen
        self.tile_size = tile_size
        
        # Load the monochrome transparent sheets
        prefix = "assets/hexanys_roguelike_tiles_0.3.0/Tilesheets/Transparent"
        self.creatures_sheet = pygame.image.load(f"{prefix}/creatures_transparent.png").convert_alpha()
        self.autotile_sheet = pygame.image.load(f"{prefix}/autotile_transparent.png").convert_alpha()
        self.general_sheet = pygame.image.load(f"{prefix}/general_transparent.png").convert_alpha()
        
        # Sprite cache: (sheet, col, row, color) -> Surface
        self.sprite_cache = {}

    def get_sprite(self, sheet_name, col, row, color):
        key = (sheet_name, col, row, color)
        if key in self.sprite_cache:
            return self.sprite_cache[key]

        # Crops tile out of spritesheet    
        rect = pygame.Rect(col * 16, row * 16, 16, 16)
        if sheet_name == "creatures":
            raw_sprite = self.creatures_sheet.subsurface(rect)
        elif sheet_name == "autotile":
            raw_sprite = self.autotile_sheet.subsurface(rect)
        else:
            raw_sprite = self.general_sheet.subsurface(rect)
            
        # Scale to game tile size
        scaled = pygame.transform.scale(raw_sprite, (self.tile_size, self.tile_size))
        
        # Tint monochrome sprite
        tinted = scaled.copy()
        color_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        color_surf.fill(color)
        tinted.blit(color_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.sprite_cache[key] = tinted
        return tinted

    def process(self):
        self.screen.fill((0, 0, 0))

        # Get player level & details
        player_query = esper.get_components(Player, Position, Graphic, Level)
        assert player_query, "Active player entity not found in ECS world!"
        _, (_, player_pos, player_graphic, player_level) = player_query[0]

        # Get active FOV for the player's current level
        active_fov = None
        for _, (fov, level) in esper.get_components(FOV, Level):
            if level.val == player_level.val:
                active_fov = fov
                break

        assert active_fov is not None, f"Active FOV map not found for level {player_level.val}!"

        # Draw map & entities
        for ent, (pos, graphic) in esper.get_components(Position, Graphic):
            # Check visibility
            if active_fov.visible[pos.x, pos.y]:
                visible = True
            elif active_fov.explored[pos.x, pos.y] and not esper.has_component(ent, Enemy):
                visible = False
            else:
                # Not explored / hidden enemy
                continue

            # Render the pre-configured sprite details directly
            color = graphic.fg
            if not visible:
                color = (int(color[0] * 0.4), int(color[1] * 0.4), int(color[2] * 0.4))

            sprite = self.get_sprite(graphic.sheet, graphic.col, graphic.row, color)
            rect = pygame.Rect(pos.x * self.tile_size, pos.y * self.tile_size, self.tile_size, self.tile_size)
            self.screen.blit(sprite, rect)

        # Draw player last
        player_color = player_graphic.fg
        player_sprite = self.get_sprite(player_graphic.sheet, player_graphic.col, player_graphic.row, player_color)
        player_rect = pygame.Rect(player_pos.x * self.tile_size, player_pos.y * self.tile_size, self.tile_size, self.tile_size)
        self.screen.blit(player_sprite, player_rect)