#Tests for placement.py: seeded, reproducible item placement.
from __future__ import annotations

# importing pytest for testing framework
import pytest

# impoting the placement module and relevant classes and exceptions from the fellowship package
from fellowship import placement
from fellowship.exceptions import PlacementError
from fellowship.world import Item, World

# function to collect items in the world's rooms, returning a list of Item objects. 
def _items(world: World) -> list[Item]:
    return [room.item for room in world.rooms.values() if room.item is not None]

# function to create a map of room names to the name of the item thats in them. 
def _layout(world: World) -> dict[str, str | None]:
    return {
        name: (room.item.name if room.item is not None else None)
        for name, room in world.rooms.items()
    }

# function that same seed produces the same layout. 
def test_same_seed_produces_identical_layout(full_world: World) -> None:
    items = _items(full_world)
    placement.place_items(full_world, items, 1234)
    first = _layout(full_world)
    placement.place_items(full_world, items, 1234)
    assert _layout(full_world) == first

# function that different seeds produce different layouts.
def test_all_items_placed_in_eligible_rooms_only(full_world: World) -> None:
    items = _items(full_world)
    eligible = placement.eligible_rooms(full_world)
    placement.place_items(full_world, items, 99)

    placed = {name for name, item in _layout(full_world).items() if item is not None}
    assert placed == set(eligible)
    # The win room never held an item and must stay empty.
    assert full_world.rooms[full_world.win_room].item is None
    # Every item is still present somewhere.
    assert {item.name for item in items} == {
        room.item.name for room in full_world.rooms.values() if room.item is not None
    }

# function that wrong items count raises an error 
def test_mismatched_counts_raise_placement_error(full_world: World) -> None:
    items = _items(full_world)
    with pytest.raises(PlacementError):
        placement.place_items(full_world, items[:-1], 7)  # one item short
