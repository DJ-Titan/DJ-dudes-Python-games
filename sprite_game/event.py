# event.py

from enum import Enum

# --- Enums for common event types and game state ---

class GameState(Enum):
    """Defines the current state of the game."""
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

class EventType(Enum):
    """Defines specific types of in-game events."""
    PLAYER_MOVED = 0
    OBJECTIVE_COMPLETED = 1
    ITEM_PICKUP = 2
    STATE_CHANGE = 3

# --- Core Event Class ---

class GameEvent:
    """Base class for all game events."""
    def __init__(self, type: EventType, data: dict = None):
        self.type = type
        self.data = data if data is not None else {}

    def __repr__(self):
        return f"GameEvent(type={self.type.name}, data={self.data})"

# --- Event Manager ---

class EventManager:
    """
    Manages the subscription and notification of events.
    This pattern allows components to communicate without direct references.
    """
    def __init__(self):
        # A dictionary mapping EventType to a list of subscriber functions/methods
        self._listeners = {}

    def subscribe(self, event_type: EventType, listener):
        """Register a listener (a callable) for a specific event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
        print(f"[EventManager] Registered listener for {event_type.name}")

    def post(self, event: GameEvent):
        """Notify all subscribers for the given event's type."""
        print(f"[EventManager] Posting event: {event}")
        if event.type in self._listeners:
            for listener in self._listeners[event.type]:
                listener(event)

# Example Event:
class StateChangeEvent(GameEvent):
    def __init__(self, new_state: GameState):
        super().__init__(EventType.STATE_CHANGE, {'new_state': new_state})

# This file is critical for decoupling components (e.g., Player posts a MOVE event, 
# and the Game or Renderer listens for it, but they don't know each other).