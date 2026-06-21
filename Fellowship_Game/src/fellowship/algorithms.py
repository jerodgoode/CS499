#Graph algorithms for the game: a breadth-first hint system.

# allows World and Item imports without circular import issues.
from __future__ import annotations

from collections import deque
from typing import Iterable

from fellowship.world import Item, World

# Sentinel return values for find_hint. They are returned in place of a
# direction so the CLI can translate them into friendly messages.
ALL_ITEMS_COLLECTED = "all_items_collected"
NO_PATH = "no_path"
HERE = "here"

# The main algorithm: find the first step toward the nearest uncollected item.
# Breadth-first search (BFS) from current_room, returning the first direction 
# toward a room that holds an item the player does not yet have.
def find_hint(world: World, current_room: str, inventory: Iterable[Item]) -> str:
    collected = {item.name for item in inventory}

    # Rooms that still hold an item the player does not yet have. Identity is
    # compared on item name, matching Player.pick_up's duplicate check.
    needed_rooms = {
        name
        for name, room in world.rooms.items()
        if room.item is not None and room.item.name not in collected
    }
    # If there are no such rooms, the player has collected all items.
    if not needed_rooms:
        return ALL_ITEMS_COLLECTED

    # If the player is already in a needed room, return the HERE message.
    if current_room in needed_rooms:
        return HERE

    # BFS from current_room, tracking visited rooms and the first step taken to reach each room.
    visited: set[str] = {current_room}
    queue: deque[tuple[str, str]] = deque()

    # seed with direct neighbors of current_room, with the direction as the first step to reach them
    for direction, target in world.get_room(current_room).exits.items():
        if target not in visited:
            visited.add(target)
            queue.append((target, direction))

    # Continue BFS until it finds a needed room or exhaust the graph.
    while queue:
        room_name, first_step = queue.popleft()
        if room_name in needed_rooms:
            return first_step
        for _, target in world.get_room(room_name).exits.items():
            if target not in visited:
                visited.add(target)
                queue.append((target, first_step))

    # if no path to a needed room is found, return the NO_PATH message
    return NO_PATH 
