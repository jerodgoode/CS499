# Player state: movement, inventory, and visit tracking. 
from __future__ import annotations
from fellowship.exceptions import InvalidMoveError
from fellowship.world import Item, World

# Represents the player character throughout a game session.
#   name          - display name for the player
#   current_room  - name of the room the player currently occupies
#   inventory     - ordered list of items being carried
#   visit_counts  - maps room name to how many times it has been entered
class Player:

    # Creates player starting in current_room. 
    # Inv starts empty, and visit_counts starts with current_room mapped to 1.
    def __init__(self, name: str, current_room: str) -> None:
        self.name = name
        self.current_room = current_room
        self.inventory: list[Item] = []
        # Start room count as first visit. 
        self.visit_counts: dict[str, int] = {current_room: 1}

    # Move the player one step in direction. Returns the name of the destination room.
    # If no exit in that direction, throws InvalidMoveError.
    def move(self, direction: str, world: World) -> str:

        # Takes input regardless of case or whitespace. 
        direction = direction.lower().strip()
        room = world.get_room(self.current_room)
        if direction not in room.exits:
            raise InvalidMoveError(
                f"You cannot go '{direction}' from {self.current_room}."
            )
        destination = room.exits[direction]
        self.current_room = destination
        # Visit counting is handled by puzzles.on_room_entry at the game layer,
        # so the trap door fires on the third entry to a room.
        return destination

    # Adds item to inventory if not already present. No effect if item is already in inventory.
    def pick_up(self, item: Item) -> None:
        if not any(i.name == item.name for i in self.inventory):
            self.inventory.append(item)

    # Returns True if the player has at least required_count items in their inventory, False otherwise.
    def has_all_items(self, required_count: int) -> bool:
        return len(self.inventory) >= required_count
