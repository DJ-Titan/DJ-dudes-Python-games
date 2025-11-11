# game.py

import pygame
import sys
import os

# Import modules
from event import EventManager, GameState, GameEvent, EventType, StateChangeEvent
from input import InputHandler
from renderer import Renderer

# --- Entity/Sprite Class (Player) ---

class Player(pygame.sprite.Sprite):
    """A basic player sprite controlled by input."""
    def __init__(self, renderer: Renderer, event_manager: EventManager, x: int, y: int):
        super().__init__()
        self.renderer = renderer
        self.event_manager = event_manager
        
        # Graphics and Position
        self.image = self.renderer.assets.get('player')
        if not self.image:
             # Fallback if asset loading failed
            self.image = pygame.Surface((renderer.tile_size, renderer.tile_size))
            self.image.fill((255, 0, 0)) # Red square
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5
        self.current_state = GameState.PLAYING

    def update_state(self, event: StateChangeEvent):
        """Listener method to change the player's state based on global events."""
        self.current_state = event.data['new_state']
        print(f"[Player] New state set: {self.current_state.name}")

    def update(self, actions: dict, delta_time: float):
        """
        Updates the player's position based on input actions.
        delta_time is used for frame-rate independent movement.
        """
        if self.current_state != GameState.PLAYING:
            return

        dx, dy = 0, 0
        speed = self.speed * (delta_time / 1000) * 60 # Normalize speed to 60 FPS baseline

        if actions['move_up']:
            dy -= speed
        if actions['move_down']:
            dy += speed
        if actions['move_left']:
            dx -= speed
        if actions['move_right']:
            dx += speed
        
        # Normalize diagonal movement (prevents faster movement diagonally)
        if dx != 0 and dy != 0:
            norm = (dx**2 + dy**2)**0.5
            dx = dx / norm * speed
            dy = dy / norm * speed

        # Simple collision check with world bounds (mocking)
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        # Clamp position to a mock boundary (e.g., 32x32 * 10 tiles)
        map_width = 10 * self.renderer.tile_size
        map_height = 10 * self.renderer.tile_size

        self.rect.x = max(0, min(new_x, map_width - self.rect.width))
        self.rect.y = max(0, min(new_y, map_height - self.rect.height))
        
        # Post a MOVED event for other systems to track
        if dx != 0 or dy != 0:
             self.event_manager.post(
                GameEvent(EventType.PLAYER_MOVED, {'position': self.rect.center})
             )


# --- Main Game Engine Class ---

class GameEngine:
    """
    The main orchestrator of the game engine. Initializes subsystems and runs the loop.
    """
    def __init__(self, width: int = 800, height: int = 600):
        # 1. Initialize Pygame
        pygame.init()
        
        # 2. Initialize Subsystems
        self.event_manager = EventManager()
        self.input_handler = InputHandler()
        self.renderer = Renderer(width, height, "Basic 2D Sprite Engine")
        
        # 3. Load Resources
        self.renderer.load_assets()

        # 4. Game State and Loop control
        self.running = True
        self.current_state = GameState.PLAYING
        
        # 5. Entities and Groups
        self.all_sprites = pygame.sprite.Group()
        
        # Create the Player
        self.player = Player(self.renderer, self.event_manager, 
                             x=self.renderer.tile_size * 2, 
                             y=self.renderer.tile_size * 2)
        self.all_sprites.add(self.player)

        # 6. Set up Event Listeners
        # The Player listens for state changes
        self.event_manager.subscribe(EventType.STATE_CHANGE, self.player.update_state)
        # The GameEngine listens for player movement to update the camera
        self.event_manager.subscribe(EventType.PLAYER_MOVED, self._on_player_moved)


    def _on_player_moved(self, event: GameEvent):
        """Listener function to update the camera when the player moves."""
        self.renderer.set_camera_target(self.player.rect)
        
    def _handle_game_events(self, event: pygame.event.Event):
        """Processes events specific to the main engine (like quitting or pausing)."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            new_state = GameState.PAUSED if self.current_state == GameState.PLAYING else GameState.PLAYING
            self.set_game_state(new_state)

    def set_game_state(self, new_state: GameState):
        """Changes the game state and notifies all listeners."""
        if self.current_state != new_state:
            self.current_state = new_state
            # Post a state change event
            state_event = StateChangeEvent(new_state)
            self.event_manager.post(state_event)
            print(f"--- Game State Changed to: {new_state.name} ---")


    def run(self):
        """The main game loop."""
        while self.running:
            # 1. INPUT HANDLING
            # Process all pending Pygame events
            for event in pygame.event.get():
                # Handle engine-specific events (e.g., ESC, closing the window)
                self.input_handler.handle_input(event)
                self._handle_game_events(event)
                
            # Check for quit action
            if self.input_handler.actions['quit']:
                self.running = False
                continue

            # 2. GAME LOGIC / UPDATE
            # Only update logic if the game is not paused
            if self.current_state == GameState.PLAYING:
                # Update all sprites based on current input and delta time
                self.all_sprites.update(self.input_handler.get_actions(), self.renderer.clock.get_time())

            # Reset single-frame actions (like 'action')
            self.input_handler.reset_single_frame_actions()

            # 3. RENDERING
            # Render all components and calculate delta time (time since last frame)
            delta_time = self.renderer.update_display(self.all_sprites.sprites())
            
        # 4. SHUTDOWN
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    # Set the game window size
    game = GameEngine(width=800, height=600)
    game.run()