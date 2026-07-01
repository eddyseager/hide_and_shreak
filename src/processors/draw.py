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

        # Screen shake configurations
        self.shake_trigger_time = 0
        self.shake_duration = 600    # Duration of shake in milliseconds
        self.shake_intensity = 80   # Max pixel amplitude of shake

    def get_vignette(self, w, h, hp, player_screen_x, player_screen_y):
        key = (w, h, hp, player_screen_x, player_screen_y)
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
            
        # Center the spotlight on the player's screen tile position (scaled down for low-res surface)
        px_ratio = (player_screen_x * self.tile_size + self.tile_size // 2) / w
        py_ratio = (player_screen_y * self.tile_size + self.tile_size // 2) / h
        cx = int(low_w * px_ratio)
        cy = int(low_h * py_ratio)
        
        # Calculate dynamic max_factor to ensure vignette covers the farthest corner when spotlight moves
        x_offset_ratio = abs(px_ratio - 0.5) / 0.5
        y_offset_ratio = abs(py_ratio - 0.5) / 0.5
        max_factor = 1.414 * (1.0 + max(x_offset_ratio, y_offset_ratio))
        
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
                # Scale up norm_factor so it reaches maximum darkness (250) closer to the center,
                # shrinking the light pool radius by ~20% (balanced middle ground) while preserving the soft exponent curve.
                clamped_factor = min(1.0, norm_factor * 1.25)
                alpha = int(250 * (clamped_factor ** 0.65))
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
        player_ent, (player, player_pos, player_graphic, player_level) = player_query[0]

        # Trigger screen shake if player was hit this frame (even if they healed on the same turn)
        if player.just_hit:
            self.shake_trigger_time = pygame.time.get_ticks()
            player.just_hit = False

        # Calculate active screen shake offset
        shake_x = 0
        time_since_hit = pygame.time.get_ticks() - self.shake_trigger_time
        if time_since_hit < self.shake_duration:
            progress = time_since_hit / self.shake_duration
            decay = 1.0 - progress
            # Fast horizontal vibration frequency
            shake_x = int(math.sin(time_since_hit * 0.08) * self.shake_intensity * decay)

        # Get active FOV for the player's current level
        active_fov = None
        for _, (fov, level) in esper.get_components(FOV, Level):
            if level.val == player_level.val:
                active_fov = fov
                break

        assert active_fov is not None, f"Active FOV map not found for level {player_level.val}!"

        # Fetch current time for animation progress
        time = pygame.time.get_ticks()
        removals = []

        # Get visual position for camera tracking
        player_visual_x = player_pos.x
        player_visual_y = player_pos.y
        player_hop_y = 0
        if esper.has_component(player_ent, MovementAnim):
            anim = esper.component_for_entity(player_ent, MovementAnim)
            elapsed = time - anim.start_time
            t = elapsed / anim.duration
            if t >= 1.0:
                removals.append((player_ent, MovementAnim))
            else:
                player_visual_x = anim.start_x + (anim.target_x - anim.start_x) * t
                player_visual_y = anim.start_y + (anim.target_y - anim.start_y) * t
                player_hop_y = -int(math.sin(t * math.pi) * (self.tile_size // 4))

        # Calculate camera offset to center on player's visual path
        camera_x = player_visual_x - self.view_width // 2
        camera_y = player_visual_y - self.view_height // 2

        # Clamp camera to map boundaries to avoid showing out-of-bounds void
        camera_x = max(0, min(camera_x, MAP_WIDTH - self.view_width))
        camera_y = max(0, min(camera_y, MAP_HEIGHT - self.view_height))

        # Draw map & entities
        for ent, (pos, graphic) in esper.get_components(Position, Graphic):
            # Skip player since they are drawn last explicitly
            if esper.has_component(ent, Player):
                continue
                
            # Determine visual positions (interpolated if animating)
            visual_x = pos.x
            visual_y = pos.y
            hop_y = 0
            
            if esper.has_component(ent, MovementAnim):
                anim = esper.component_for_entity(ent, MovementAnim)
                elapsed = time - anim.start_time
                t = elapsed / anim.duration
                if t >= 1.0:
                    removals.append((ent, MovementAnim))
                else:
                    visual_x = anim.start_x + (anim.target_x - anim.start_x) * t
                    visual_y = anim.start_y + (anim.target_y - anim.start_y) * t
                    
                    # Apply a lively hop to the player, and a heavy, low-profile hop to enemies
                    if not esper.has_component(ent, Enemy):
                        hop_y = -int(math.sin(t * math.pi) * (self.tile_size // 4))
                    else:
                        hop_y = -int(math.sin(t * math.pi) * (self.tile_size // 8))  # Slow, heavy shuffle

            # Calculate screen-space position
            screen_x = visual_x - camera_x
            screen_y = visual_y - camera_y

            # Clip rendering to the viewport (with 1-tile padding for smooth entry/exit)
            if not (-1 <= screen_x < self.view_width + 1 and -1 <= screen_y < self.view_height + 1):
                continue

            # Check visibility at the logical tile position
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
            rect = pygame.Rect(screen_x * self.tile_size + shake_x, screen_y * self.tile_size + hop_y, self.tile_size, self.tile_size)
            self.screen.blit(sprite, rect)

        # Draw player last at visual coordinates
        player_screen_x = player_visual_x - camera_x
        player_screen_y = player_visual_y - camera_y
        player_color = player_graphic.fg
        player_sprite = self.get_sprite(player_graphic.sheet, player_graphic.col, player_graphic.row, player_color)
        player_rect = pygame.Rect(player_screen_x * self.tile_size + shake_x, player_screen_y * self.tile_size + player_hop_y, self.tile_size, self.tile_size)
        self.screen.blit(player_sprite, player_rect)

        # Draw smooth radial vignette overlay centered on the player's screen position based on health state
        vignette = self.get_vignette(
            self.view_width * self.tile_size, 
            self.view_height * self.tile_size, 
            player.hp,
            int(player_screen_x),
            int(player_screen_y)
        )
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

        # Clean up finished animations
        for ent, comp_class in removals:
            if esper.has_component(ent, comp_class):
                esper.remove_component(ent, comp_class)