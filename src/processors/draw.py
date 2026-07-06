import math
import random
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
        if hp == 1:
            vignette_color = (120, 0, 0)       # Critical low health: Darker Crimson
        elif hp <= 0:
            vignette_color = (255, 0, 0)       # Dead: Bright Red
            vignette_low.fill((255, 0, 0, 180)) # Fill screen with transparent red on game over
        else:
            vignette_color = (0, 0, 0)         # Healthy (2+ HP): Black
            
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
                alpha = max(0, min(alpha, 255))
            elif hp == 1:
                # Soft translucent crimson shadow around edges
                clamped_factor = min(1.0, norm_factor * 1.25)
                alpha = int(140 * (clamped_factor ** 0.65))
                alpha = max(0, min(alpha, 140))
            else:
                # Standard black shadow around edges
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
        player_ent, (player, player_pos, player_graphic) = get_singleton_by_components(Player, Position, Graphic)

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

        # Retrieve the map overlay grid for the active level
        active_level_map = get_singleton(LevelMap)

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
        # Categorize renderables into layers so environment/blood sits below creatures
        static_renderables = []
        creature_renderables = []
        
        for ent, (pos, graphic) in esper.get_components(Position, Graphic):
            if esper.has_component(ent, Player):
                continue
            if esper.has_component(ent, Enemy):
                creature_renderables.append((ent, pos, graphic))
            else:
                static_renderables.append((ent, pos, graphic))

        # Render static layers first, then active creatures
        for ent, pos, graphic in (static_renderables + creature_renderables):
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
            if active_level_map.visible[pos.x, pos.y]:
                visible = True
            elif active_level_map.explored[pos.x, pos.y] and not esper.has_component(ent, Enemy):
                visible = False
            else:
                continue

            rect = pygame.Rect(screen_x * self.tile_size + shake_x, screen_y * self.tile_size + hop_y, self.tile_size, self.tile_size)

            # Custom rendering for procedural circle blood splatters
            if esper.has_component(ent, Blood):
                blood = esper.component_for_entity(ent, Blood)
                rng = random.Random(blood.seed)
                
                # Base blood color (dark red)
                base_color = (150, 10, 10)
                if not visible:
                    # Apply 40% tint for fog of war
                    base_color = (60, 4, 4)

                cx = rect.x + self.tile_size // 2
                cy = rect.y + self.tile_size // 2

                # Determine sizes based on intensity level
                if blood.intensity == 1:
                    main_r = rng.randint(4, 5)
                    num_drops = rng.randint(3, 4)
                else:
                    main_r = rng.randint(6, 8)
                    num_drops = rng.randint(5, 7)

                # Draw main center splatter
                pygame.draw.circle(self.screen, base_color, (cx + rng.randint(-2, 2), cy + rng.randint(-2, 2)), main_r)

                # Draw satellite droplets
                for _ in range(num_drops):
                    off_x = rng.randint(-self.tile_size // 3, self.tile_size // 3)
                    off_y = rng.randint(-self.tile_size // 3, self.tile_size // 3)
                    drop_r = rng.randint(1, 2)
                    drop_color = (
                        max(0, min(255, base_color[0] + rng.randint(-15, 15))),
                        max(0, min(255, base_color[1] + rng.randint(-2, 2))),
                        max(0, min(255, base_color[2] + rng.randint(-2, 2)))
                    )
                    pygame.draw.circle(self.screen, drop_color, (cx + off_x, cy + off_y), drop_r)
                continue

            # Render the pre-configured sprite details directly
            color = graphic.fg
            if not visible:
                color = (int(color[0] * 0.4), int(color[1] * 0.4), int(color[2] * 0.4))

            sprite = self.get_sprite(graphic.sheet, graphic.col, graphic.row, color)
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