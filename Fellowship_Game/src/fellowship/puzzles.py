#Trap-door puzzle logic: visit tracking and the binary-search lockpick.
#This module is pure logic only - no input()/print(). The interactive guessing
#loop lives in cli.py and calls evaluate_guess for its comparison logic.

from __future__ import annotations

import random

# imports Player and Item only for type annotations. 
from fellowship.player import Player
from fellowship.world import Item

TRAP_TRIGGER_VISIT = 3      # the trap door opens on the 3rd entry into a room
LOCKPICK_MIN = 1            # the minimum possible secret number for the lockpick puzzle   
LOCKPICK_MAX = 100          # the maximum possible secret number for the lockpick puzzle

# The number of lockpick attempts the player gets to guess the secret number. This
# is a fixed number, not a function of the range, to give the player a reasonable
# chance of success.
LOCKPICK_ATTEMPTS = 7

CORRECT = "correct"
HIGHER = "higher"
LOWER = "lower"

# Record an entry into room_name for the player.
# Returns True if this entry should trigger the trap door, False otherwise.
def on_room_entry(player: Player, room_name: str) -> bool:
    count = player.visit_counts.get(room_name, 0) + 1
    player.visit_counts[room_name] = count
    return count == TRAP_TRIGGER_VISIT

# Compare a guess to the secret number for the lockpick puzzle.
def evaluate_guess(secret: int, guess: int) -> str:
    if guess == secret:
        return CORRECT
    return HIGHER if secret > guess else LOWER

# Remove and return a random item from the player's inventory, or None if the inventory is empty.
def drop_random_item(player: Player, rng: random.Random) -> Item | None:
    if not player.inventory:
        return None
    index = rng.randrange(len(player.inventory))
    return player.inventory.pop(index)
