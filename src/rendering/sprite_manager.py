import pygame

class SpriteManager:
    def __init__(self, tile_size: int, assets_prefix: str = "assets/hexanys_roguelike_tiles_0.3.0/Tilesheets/Transparent"):
        self.tile_size = tile_size
        self.creatures_sheet = pygame.image.load(f"{assets_prefix}/creatures_transparent.png").convert_alpha()
        self.autotile_sheet = pygame.image.load(f"{assets_prefix}/autotile_transparent.png").convert_alpha()
        self.general_sheet = pygame.image.load(f"{assets_prefix}/general_transparent.png").convert_alpha()
        self.sprite_cache = {}

    def get_sprite(self, sheet_name: str, col: int, row: int, color: tuple) -> pygame.Surface:
        key = (sheet_name, col, row, color)
        if key in self.sprite_cache:
            return self.sprite_cache[key]

        # Crop tile out of spritesheet
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
