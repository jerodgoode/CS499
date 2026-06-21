#Tests for puzzles.py: trap visit counter, lockpick comparison, item drop.
from __future__ import annotations

import random

# import player and puzzle functions to test
from fellowship.player import Player
from fellowship.puzzles import (
    CORRECT,
    HIGHER,
    LOCKPICK_ATTEMPTS,
    LOCKPICK_MAX,
    LOCKPICK_MIN,
    LOWER,
    TRAP_TRIGGER_VISIT,
    drop_random_item,
    evaluate_guess,
    on_room_entry,
)
from fellowship.world import Item

# entering the same room three times should trigger the trap on the third visit, and the visit count should be correct
def test_on_room_entry_fires_only_on_third_visit() -> None:
    player = Player(name="Gandalf", current_room="Start")
    # "Cave" is not the start room, so its count begins at zero.
    assert on_room_entry(player, "Cave") is False  # 1st
    assert on_room_entry(player, "Cave") is False  # 2nd
    assert on_room_entry(player, "Cave") is True   # 3rd -> trap fires
    assert player.visit_counts["Cave"] == TRAP_TRIGGER_VISIT

# check that guessing the correct number returns CORRECT, and that guessing too low or too high returns the appropriate hints.
# Those answers let you find any number between 1 and 100 in at most 7 guesses.
def test_binary_search_solves_within_attempt_budget() -> None:
    assert evaluate_guess(50, 50) == CORRECT
    assert evaluate_guess(50, 40) == HIGHER  # secret higher than guess
    assert evaluate_guess(50, 60) == LOWER   # secret lower than guess

    # Try every secret number and count how many guesses it takes.
    # Each guess checks the middle of the current range, so it should find the secret in at most 7 guesses. 
    for secret in range(LOCKPICK_MIN, LOCKPICK_MAX + 1):
        lo, hi, guesses = LOCKPICK_MIN, LOCKPICK_MAX, 0
        while lo <= hi:
            mid = (lo + hi) // 2
            guesses += 1
            result = evaluate_guess(secret, mid)
            if result == CORRECT:
                break
            if result == HIGHER:
                lo = mid + 1    # secret is higher than guess
            else:
                hi = mid - 1    # secret is lower than guess    
        # no matter what the secret number is, it should be found in at most 7 guesses.        
        assert guesses <= LOCKPICK_ATTEMPTS

# Function to test that same seed drops the same item and that the item is actually removed from the player's inventory
# Empty inventory should yield None when trying to drop a random item.
def test_drop_random_item_is_deterministic_and_handles_empty() -> None:
    def loaded_player() -> Player:
        player = Player(name="Gandalf", current_room="Start")
        for name in ("A", "B", "C"):
            player.pick_up(Item(name=name, description=""))
        return player

    # Two identical players with the same seed should drop the same item, and that item should be removed from the first player's inventory.
    first, second = loaded_player(), loaded_player()
    dropped = drop_random_item(first, random.Random(123))
    assert dropped is not None
    assert dropped.name == drop_random_item(second, random.Random(123)).name
    assert dropped not in first.inventory

    # Empty inventory yields None.
    empty = Player(name="Gandalf", current_room="Start")
    assert drop_random_item(empty, random.Random(0)) is None
