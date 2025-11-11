# renderer.py

import pygame
import os
from typing import List, Tuple

class Renderer:
    """
    Handles all visual aspects: window setup, asset loading, and drawing layers.
    This is where Aseprite tilemap loading logic would be fully implemented.
    """
    def __init__(self, screen_width: int, screen_height: int, title: str = "Pygame Engine"):
        pygame.display.set_caption(title)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Game camera offset (used to follow the player)
        self.camera_offset = pygame.math.Vector2(0, 0)
        
        # Mock asset storage (would store loaded Pygame Surfaces)
        self.assets = {}

        # Mock Map Data (Replace with Tiled/Aseprite map data loading)
        # 10x10 map with mock tile IDs
        self.tile_size = 32
        self.map_data = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 2, 2, 0, 0, 2, 2, 0, 1],
            [1, 0, 2, 2, 0, 0, 2, 2, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 2, 2, 0, 0, 2, 2, 0, 1],
            [1, 0, 2, 2, 0, 0, 2, 2, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        
        # Color mapping for mock tiles
        self.tile_colors = {
            0: (100, 150, 50), # Grass (Walkable)
            1: (50, 50, 50),   # Wall (Solid)
            2: (0, 0, 150)     # Water (Unwalkable)
        }

    def load_assets(self, asset_dir: str = 'assets'):
        """
        Mocks asset loading. In a real game, this would load spritesheets,
        split them, and store Pygame Surfaces.
        """
        print(f"[Renderer] Loading assets from: {asset_dir} (Mocking)")
        # Example: self.assets['player'] = pygame.image.load(os.path.join(asset_dir, 'player.png'))
        # Using a simple surface for the player placeholder
        self.assets['player'] = pygame.Surface((self.tile_size, self.tile_size))
        self.assets['player'].fill((255, 0, 0)) # Red player square

    def set_camera_target(self, target_rect: pygame.Rect):
        """
        Updates the camera offset to center on a target (e.g., the player).
        """
        # Calculate the required offset to center the target
        self.camera_offset.x = target_rect.centerx - self.screen_width // 2
        self.camera_offset.y = target_rect.centery - self.screen_height // 2

    def render_map_layer(self):
        """
        Renders the background tilemap layer.
        """
        for y, row in enumerate(self.map_data):
            for x, tile_id in enumerate(row):
                # Calculate the screen position with camera offset
                pos_x = x * self.tile_size - self.camera_offset.x
                pos_y = y * self.tile_size - self.camera_offset.y

                # Only draw if the tile is on screen (simple culling)
                if -self.tile_size < pos_x < self.screen_width and \
                   -self.tile_size < pos_y < self.screen_height:
                    
                    color = self.tile_colors.get(tile_id, (0, 0, 0))
                    
                    # Draw the tile rectangle
                    pygame.draw.rect(
                        self.screen,
                        color,
                        (pos_x, pos_y, self.tile_size, self.tile_size)
                    )

    def render_sprites(self, sprites: List[pygame.sprite.Sprite]):
        """
        Renders active game entities (sprites) over the map layers.
        In a real game, sprites would be sorted by y-position for depth effect.
        """
        for sprite in sprites:
            # Apply camera offset to the sprite's position
            render_pos = sprite.rect.topleft - self.camera_offset
            self.screen.blit(sprite.image, render_pos)


    def update_display(self, sprites_to_render: List[pygame.sprite.Sprite]):
        """
        Main rendering call, manages the drawing order and screen refresh.
        """
        self.screen.fill((0, 0, 0)) # Black background for safety
        
        # 1. Render Map Layers (e.g., floor, objects below player)
        self.render_map_layer()

        # 2. Render Sprites (e.g., player, enemies, NPCs)
        self.render_sprites(sprites_to_render)

        # 3. Render UI/HUD (Health bars, inventory - without camera offset)

        pygame.display.flip()
        self.clock.tick(self.fps)
        return self.clock.get_time() # Returns time since last frame in milliseconds