import math
import esper
import pygame
from components import *
from rendering.sprite_manager import SpriteManager
from rendering.vignette import VignetteRenderer
from rendering.camera import Camera
from rendering.blood_renderer import BloodRenderer
from rendering.ui_renderer import UIRenderer

class Draw(esper.Processor):
    def __init__(self, screen, tile_size, view_width, view_height):
        super().__init__()
        self.screen = screen
        self.tile_size = tile_size
        self.view_width = view_width
        self.view_height = view_height

        self.sprite_manager = SpriteManager(tile_size)
        self.sprite_cache = self.sprite_manager.sprite_cache
        self.vignette_renderer = VignetteRenderer(tile_size, self.sprite_cache)
        self.camera = Camera(view_width, view_height)
        self.blood_renderer = BloodRenderer(screen, tile_size)
        self.ui_renderer = UIRenderer(screen, view_width, view_height, tile_size)

    def get_vignette(self, w, h, hp, player_screen_x, player_screen_y):
        return self.vignette_renderer.get_vignette(w, h, hp, player_screen_x, player_screen_y)

    def get_sprite(self, sheet_name, col, row, color):
        return self.sprite_manager.get_sprite(sheet_name, col, row, color)

    def process(self):
        self.screen.fill((0, 0, 0))

        # Get player level & details (enforced via key singleton helper)
        player_ent, (player, player_pos, player_graphic) = get_singleton_by_components(Player, Position, Graphic)

        # Trigger screen shake if player was hit this frame
        if player.just_hit:
            self.camera.trigger_shake(pygame.time.get_ticks())
            player.just_hit = False

        time = pygame.time.get_ticks()
        shake_x = self.camera.get_shake_offset(time)
        active_level_map = get_singleton(LevelMap)
        removals = []

        # Get visual position for camera tracking
        player_visual_x, player_visual_y = player_pos.x, player_pos.y
        player_hop_y = 0
        if esper.has_component(player_ent, MovementAnim):
            anim = esper.component_for_entity(player_ent, MovementAnim)
            elapsed = time - anim.start_time
            t = elapsed / anim.duration
            if t >= 1.0:
                removals.append((player_ent, MovementAnim))
            else:
                t_eased = math.sin(t * math.pi / 2)
                player_visual_x = anim.start_x + (anim.target_x - anim.start_x) * t_eased
                player_visual_y = anim.start_y + (anim.target_y - anim.start_y) * t_eased
                player_hop_y = -int(math.sin(t * math.pi) * 7)

        # Calculate camera offset to center on player's visual path
        camera_x, camera_y = self.camera.get_camera_offset(player_visual_x, player_visual_y)

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
            visual_x, visual_y = pos.x, pos.y
            hop_y = 0

            if esper.has_component(ent, MovementAnim):
                anim = esper.component_for_entity(ent, MovementAnim)
                elapsed = time - anim.start_time
                t = elapsed / anim.duration
                if t >= 1.0:
                    removals.append((ent, MovementAnim))
                else:
                    t_eased = math.sin(t * math.pi / 2)
                    visual_x = anim.start_x + (anim.target_x - anim.start_x) * t_eased
                    visual_y = anim.start_y + (anim.target_y - anim.start_y) * t_eased
                    hop_y = -int(math.sin(t * math.pi) * 5)

            screen_x = visual_x - camera_x
            screen_y = visual_y - camera_y

            # Clip rendering to the viewport
            if not (-1 <= screen_x < self.view_width + 1 and -1 <= screen_y < self.view_height + 1):
                continue

            # Check visibility at the logical tile position
            if active_level_map.visible[pos.x, pos.y]:
                visible = True
            elif active_level_map.explored[pos.x, pos.y] and not esper.has_component(ent, Enemy):
                visible = False
            else:
                continue

            rect = pygame.Rect(
                screen_x * self.tile_size + shake_x,
                screen_y * self.tile_size + hop_y,
                self.tile_size,
                self.tile_size
            )

            # Custom rendering for procedural circle blood splatters
            if esper.has_component(ent, Blood):
                blood = esper.component_for_entity(ent, Blood)
                self.blood_renderer.render(blood, rect, visible)
                continue

            # Render corpse rotated 90 degrees clockwise
            if esper.has_component(ent, Corpse):
                color = graphic.fg
                if not visible:
                    color = (int(color[0] * 0.4), int(color[1] * 0.4), int(color[2] * 0.4))
                sprite = self.get_sprite(graphic.sheet, graphic.col, graphic.row, color)
                sprite = pygame.transform.rotate(sprite, -90)
                self.screen.blit(sprite, rect)
                continue

            # Render pre-configured sprite
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
        if player.hp <= 0:
            player_sprite = pygame.transform.rotate(player_sprite, -90)
        player_rect = pygame.Rect(
            player_screen_x * self.tile_size + shake_x,
            player_screen_y * self.tile_size + player_hop_y,
            self.tile_size,
            self.tile_size
        )
        self.screen.blit(player_sprite, player_rect)

        # Draw smooth radial vignette overlay centered on the player's screen position
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
            self.ui_renderer.render_game_over()

        # Render Story Overlay if active on the active world context
        story_query = esper.get_component(StoryOverlay)
        if story_query:
            _, story = story_query[0]
            self.ui_renderer.render_story_overlay(story.line1, story.line2)

        # Clean up finished animations
        for ent, comp_class in removals:
            if esper.has_component(ent, comp_class):
                esper.remove_component(ent, comp_class)