# input.py

import pygame
from typing import Dict, Any

class InputHandler:
    """
    Handles raw keyboard and event input, translating it into game actions.
    This separates the logic of 'which key is pressed' from 'what that key does'.
    """
    def __init__(self):
        # Maps game actions to their current state (e.g., {'move_up': False})
        self.actions: Dict[str, Any] = {
            'move_up': False,
            'move_down': False,
            'move_left': False,
            'move_right': False,
            'action': False, # E.g., for attacking or interacting
            'quit': False
        }

        # Maps Pygame key constants to game actions
        self.key_map: Dict[int, str] = {
            pygame.K_w: 'move_up',
            pygame.K_s: 'move_down',
            pygame.K_a: 'move_left',
            pygame.K_d: 'move_right',
            pygame.K_SPACE: 'action',
            pygame.K_ESCAPE: 'quit'
        }

    def handle_input(self, event: pygame.event.Event):
        """
        Processes a single Pygame event and updates the internal action state.
        This should be called for every event in the main game loop.
        """
        if event.type == pygame.QUIT:
            self.actions['quit'] = True
            return

        # --- Key Down/Up Events ---
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            action = self.key_map.get(event.key)

            if action:
                is_down = (event.type == pygame.KEYDOWN)

                # Special handling for 'action' to only trigger once per press
                if action == 'action' and event.type == pygame.KEYDOWN:
                    # 'action' is True only on the frame of KEYDOWN
                    self.actions[action] = True
                elif action == 'action' and event.type == pygame.KEYUP:
                    # Reset 'action' on KEYUP
                    self.actions[action] = False
                else:
                    # For continuous movement
                    self.actions[action] = is_down
    
    def get_actions(self) -> Dict[str, Any]:
        """Returns the current state of all high-level game actions."""
        return self.actions

    def reset_single_frame_actions(self):
        """Resets actions that should only last one frame (like 'action')."""
        if self.actions['action']:
            self.actions['action'] = False