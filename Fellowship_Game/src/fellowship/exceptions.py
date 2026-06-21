# Created custom exceptions for the game. 
# Each exception inherits from FellowshipError, which is the base class for all game-related errors. 
# This allows us to catch specific errors when they occur and provide informative messages 
# to the player or handle them gracefully in the game loop.
from __future__ import annotations


class FellowshipError(Exception):
    """Base exception for all Fellowship game errors."""


class InvalidMoveError(FellowshipError):
    """Player attempted to move in an invalid direction."""


class ItemNotFoundError(FellowshipError):
    """Requested item does not exist in this current room."""


class ConfigError(FellowshipError):
    """World configuration is invalid or malformed."""


class SaveLoadError(FellowshipError):
    """Save cannot be written/save ID cannot be loaded."""


class PlacementError(FellowshipError):
    """Raised when items cannot be placed (e.g. item/room count mismatch)."""
