# Tests for player.py: movement, inventory, and has_all_items. 
from __future__ import annotations

# pytest gives us tools for running tests and checking for exceptions, among other things.
import pytest

# import the custom error that a player riases when a move is invalid
from fellowship.exceptions import InvalidMoveError

#import the Player, Item, and World classes that we will be testing
from fellowship.player import Player
from fellowship.world import Item, World

# test that moving in a valid direction updates the player's current room correctly
def test_move_updates_current_room(minimal_world: World) -> None:
    player = Player(name="Gandalf", current_room="Start")
    player.move("north", minimal_world)
    assert player.current_room == "End"

# test that moving in an invalid direction raises a InvalidMoveError instead of doing nothing
def test_move_raises_on_invalid_direction(minimal_world: World) -> None:
    player = Player(name="Gandalf", current_room="Start")
    with pytest.raises(InvalidMoveError):
        player.move("south", minimal_world)

# test that picking up an item actually adds it to the inventory; checks if item is the correct name
def test_pick_up_adds_item_to_inventory() -> None:
    player = Player(name="Gandalf", current_room="Start")
    item = Item(name="Ring", description="One ring to rule them all.")
    player.pick_up(item)
    assert len(player.inventory) == 1
    assert player.inventory[0].name == "Ring"

# Test that picking up the same item twice doesnt duplicate it in inventory
def test_pick_up_prevents_duplicates() -> None:
    player = Player(name="Gandalf", current_room="Start")
    item = Item(name="Ring", description="Precious.")
    player.pick_up(item)
    player.pick_up(item)
    assert len(player.inventory) == 1

# test that has_all_items only returns true when the player has at least the specified number of items in their inventory
def test_has_all_items_returns_true_only_when_count_met() -> None:
    player = Player(name="Gandalf", current_room="Start")
    assert player.has_all_items(1) is False
    player.pick_up(Item(name="A", description=""))
    assert player.has_all_items(1) is True
