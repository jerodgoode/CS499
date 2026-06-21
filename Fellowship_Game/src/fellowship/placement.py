#Seeded random placement of items into the world's rooms.
from __future__ import annotations

# import random for shuffling and generating seeds, and typing.Sequence for type annotations.
import random

# import custom error type and the main classes for the game.
from typing import Sequence
from fellowship.exceptions import PlacementError
from fellowship.world import Item, World

# Range the auto-generated seed is drawn from in new_game. Stored on the Game
# so a run can be replayed exactly.
SEED_MAX = 2**32

# returns the names of rooms that can hold an item
# Skips win room (Dungeon) and any other item-free rooms, without hardcoding names.
def eligible_rooms(world: World) -> list[str]:
    return [name for name, room in world.rooms.items() if room.item is not None]

# assign each item to a room using a seeded shuffle
# The eligible rooms are shuffled with a random.Random(seed)
# and items are assigned to them positionally, so the same seed always produces the same layout.
def place_items(world: World, items: Sequence[Item], seed: int) -> None:
    rooms = eligible_rooms(world)
    if len(items) != len(rooms):
        raise PlacementError(
            f"Cannot place {len(items)} item(s) into {len(rooms)} eligible "
            "room(s): counts must match."
        )

    # Seeded shuffle logic: create a random.Random instance with the provided seed, 
    # shuffle the list of eligible rooms, and then assign items to rooms in the order they appear in the shuffled list.
    rng = random.Random(seed)
    shuffled = list(rooms)
    rng.shuffle(shuffled)

    # Clear the eligible rooms first so a re-placement never leaves stale items.
    for name in rooms:
        world.rooms[name].item = None
    for item, room_name in zip(items, shuffled):
        world.rooms[room_name].item = item

# Generate a fresh random seed, place items with it, and return that seed.
def new_game(world: World, items: Sequence[Item]) -> int:
    seed = random.randrange(SEED_MAX)
    place_items(world, items, seed)
    return seed
