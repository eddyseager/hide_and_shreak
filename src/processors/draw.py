import math
import esper
import pygame
from components import *

class Draw(esper.Processor):
    def __init__(self, screen, tile_size, view_width, view_height):
        super().__init__()
        self.screen = screen
        self.tile_size = tile_size
        self.view_width = view_width
        self.view_height = view_height
        
        # Load the monochrome transparent sheets
        prefix = "assets/hexanys_roguelike_tiles_0.3.0/Tilesheets/Transparent"
        self.creatures_sheet = pygame.image.load(f"{prefix}/creatures_transparent.png").convert_alpha()
        self.autotile_sheet = pygame.image.load(f"{prefix}/autotile_transparent.png").convert_alpha()
        self.general_sheet = pygame.image.load(f"{prefix}/general_transparent.png").convert_alpha()
        
        # Sprite cache: (sheet, col, row, color) -> Surface
        self.sprite_cache = {}
        self.vignette_surf = None

    def get_vignette(self, w, h, hp):
        key = (w, h, hp)
        if key in self.sprite_cache:
            return self.sprite_cache[key]

        # Generate a high-resolution, perfectly smooth gradient vignette ONCE per health state
        # We draw it at 1/2 resolution and smoothscale it for a soft, blurry look
        low_w = w // 2
        low_h = h // 2
        vignette_low = pygame.Surface((low_w, low_h), pygame.SRCALPHA)
        vignette_low.fill((0, 0, 0, 0))
        
        # Determine vignette color based on player hp
        if hp == 3:
            vignette_color = (0, 0, 0)       # Normal: Black
        elif hp == 2:
            vignette_color = (130, 0, 0)     # 1 hit taken: Dark red
        elif hp == 1:
            vignette_color = (255, 0, 0)     # 2 hits taken: Bright red
        else:
            vignette_color = (255, 0, 0)     # 3 hits taken (Dead): Solid red base
            vignette_low.fill((255, 0, 0, 180)) # Fill screen with transparent red on game over
            
        cx, cy = low_w // 2, low_h // 2
        max_factor = 1.414  # Covers corners of the rectangle
        
        # Draw 100 concentric ellipses for an extremely smooth, glitch-free gradient
        for step in range(100, 0, -1):
            factor = (step / 100.0) * max_factor
            
            ellipse_w = int(low_w * factor)
            ellipse_h = int(low_h * factor)
            
            rx = cx - ellipse_w // 2
            ry = cy - ellipse_h // 2
            
            norm_factor = factor / max_factor
            if hp == 0:
                # Dense red shadow closing in fully
                alpha = int(255 * (norm_factor ** 0.45))
            else:
                alpha = int(250 * (norm_factor ** 0.65))  # Tight spotlight
            alpha = max(0, min(alpha, 250))
            
            if alpha > 0:
                rect = pygame.Rect(rx, ry, ellipse_w, ellipse_h)
                pygame.draw.ellipse(vignette_low, (*vignette_color, alpha), rect)
                
        self.sprite_cache[key] = pygame.transform.smoothscale(vignette_low, (w, h))
        return self.sprite_cache[key]

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
        _, (player, player_pos, player_graphic, player_level) = player_query[0]

        # Get active FOV for the player's current level
        active_fov = None
        for _, (fov, level) in esper.get_components(FOV, Level):
            if level.val == player_level.val:
                active_fov = fov
                break

        assert active_fov is not None, f"Active FOV map not found for level {player_level.val}!"

        # Calculate camera offset to center on player
        camera_x = player_pos.x - self.view_width // 2
        camera_y = player_pos.y - self.view_height // 2

        # Clamp camera to map boundaries to avoid showing out-of-bounds void
        camera_x = max(0, min(camera_x, MAP_WIDTH - self.view_width))
        camera_y = max(0, min(camera_y, MAP_HEIGHT - self.view_height))

        # Draw map & entities
        for ent, (pos, graphic) in esper.get_components(Position, Graphic):
            # Calculate screen-space position
            screen_x = pos.x - camera_x
            screen_y = pos.y - camera_y

            # Clip rendering to the viewport
            if not (0 <= screen_x < self.view_width and 0 <= screen_y < self.view_height):
                continue

            # Check visibility
            if active_fov.visible[pos.x, pos.y]:
                visible = True
            elif active_fov.explored[pos.x, pos.y] and not esper.has_component(ent, Enemy):
                visible = False
            else:
                continue

            # Render the pre-configured sprite details directly
            color = graphic.fg
            if not visible:
                color = (int(color[0] * 0.4), int(color[1] * 0.4), int(color[2] * 0.4))

            sprite = self.get_sprite(graphic.sheet, graphic.col, graphic.row, color)
            rect = pygame.Rect(screen_x * self.tile_size, screen_y * self.tile_size, self.tile_size, self.tile_size)
            self.screen.blit(sprite, rect)

        # Draw player last
        player_screen_x = player_pos.x - camera_x
        player_screen_y = player_pos.y - camera_y
        player_color = player_graphic.fg
        player_sprite = self.get_sprite(player_graphic.sheet, player_graphic.col, player_graphic.row, player_color)
        player_rect = pygame.Rect(player_screen_x * self.tile_size, player_screen_y * self.tile_size, self.tile_size, self.tile_size)
        self.screen.blit(player_sprite, player_rect)

        # Draw smooth radial vignette overlay centered on the viewport based on health state
        vignette = self.get_vignette(self.view_width * self.tile_size, self.view_height * self.tile_size, player.hp)
        self.screen.blit(vignette, (0, 0))

        # Render Game Over text if player health is 0
        if player.hp <= 0:
            font = pygame.font.Font(None, 72)
            go_text = font.render("GAME OVER", True, (255, 255, 255))
            go_rect = go_text.get_rect(center=(self.view_width * self.tile_size // 2, self.view_height * self.tile_size // 2 - 25))
            self.screen.blit(go_text, go_rect)
            
            sub_font = pygame.font.Font(None, 36)
            sub_text = sub_font.render("Press ESC to Quit", True, (200, 200, 200))
            sub_rect = sub_text.get_rect(center=(self.view_width * self.tile_size // 2, self.view_height * self.tile_size // 2 + 30))
            self.screen.blit(sub_text, sub_rect)