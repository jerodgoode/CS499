#Tests for algorithms.py: the breadth-first hint system.
from __future__ import annotations

from fellowship.algorithms import ALL_ITEMS_COLLECTED, HERE, NO_PATH, find_hint
from fellowship.world import Item, Room, World

# build a room with empty description
def _room(name: str, exits: dict[str, str], item: Item | None = None) -> Room:
    return Room(name=name, description="", exits=exits, item=item)

# Assemble a world from a list of rooms. 
def _world(*rooms: Room, start: str = "A", win: str = "WIN") -> World:
    mapping = {room.name: room for room in rooms}
    return World(rooms=mapping, start_room=start, win_room=win, items_required=len(rooms))

# hint points to nearest item, not just any item.
def test_returns_first_step_toward_nearest_item() -> None:
    gem = Item(name="Gem", description="")
    far = Item(name="Far", description="")
    world = _world(
        _room("A", {"north": "B", "east": "D"}),
        _room("B", {"south": "A", "north": "C"}),
        _room("C", {"south": "B"}, item=far),   # distance 2 from A
        _room("D", {"west": "A"}, item=gem),     # distance 1 from A
    )
    assert find_hint(world, "A", []) == "east"

# Checks all three special returns: standing on an item (HERE), item exists but
# can't be reached (NO_PATH), and nothing left to find (ALL_ITEMS_COLLECTED).
def test_sentinels_for_collected_here_and_unreachable() -> None:
    gem = Item(name="Gem", description="")
    world = _world(
        _room("A", {"north": "C"}, item=gem),
        _room("C", {"south": "A"}),
        _room("X", {}, item=Item(name="Lost", description="")),  # disconnected
    )
    # Standing on a needed item.
    assert find_hint(world, "A", []) == HERE
    # Everything in reach already collected, but an unreachable item remains.
    assert find_hint(world, "A", [Item(name="Gem", description="")]) == NO_PATH
    # Nothing needed anywhere.
    everything = [Item(name="Gem", description=""), Item(name="Lost", description="")]
    assert find_hint(world, "A", everything) == ALL_ITEMS_COLLECTED

# All three rooms connect to each other, forming a loop. BFS should still
# finish instead of going in circles.
def test_bfs_terminates_on_cyclic_graph() -> None:
    gem = Item(name="Gem", description="")
    world = _world(
        _room("A", {"east": "B", "south": "C"}),
        _room("B", {"west": "A", "south": "C"}),
        _room("C", {"north": "A", "east": "B"}, item=gem),
    )
    assert find_hint(world, "A", []) == "south"
