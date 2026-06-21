# World model: Room, Item, and World classes plus the JSON loader.
from __future__ import annotations

#importing necessary modules and classes for the world model.
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

#custom error type for any problems with the world configuration file.
from fellowship.exceptions import ConfigError

# Amount of items required to win.
DEFAULT_ITEMS_REQUIRED = 7

@dataclass
# represents an item that can be collected. 
class Item:

    name: str
    description: str


@dataclass
# represents a location in the game. 
class Room:

    name: str
    description: str
    exits: dict[str, str]
    item: Optional[Item] = None

# represents the entire game world, including all rooms and the win condition.
class World:

    def __init__(
        # creates the worlds with the given rooms.
        self,
        rooms: dict[str, Room],
        start_room: str,
        win_room: str,
        items_required: int,
    ) -> None:
        # store the room graph and config values for the game
        self.rooms = rooms
        self.start_room = start_room
        self.win_room = win_room
        self.items_required = items_required

    def get_room(self, name: str) -> Room:
        return self.rooms[name]

# Loads a world configuration from a JSON file at the given path.
def load_world(path: Path) -> World:
    try:
        # opens the file and loads the JSON data.
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        # if the file cannot be opened, this will show a config error.
        raise ConfigError(f"Cannot open world config at '{path}': {exc}") from exc
    except json.JSONDecodeError as exc:
        # if the file is not valid JSON, this will show a config error.
        raise ConfigError(f"Invalid JSON in world config at '{path}': {exc}") from exc

    # loop through and validate the top-level keys. 
    # if any are missing, shows a config error with the missing key.
    for key in ("start_room", "win_room", "items_required", "rooms"):
        if key not in data:
            raise ConfigError(f"Missing required top-level key: '{key}'")

    # rooms must be a dict, not a list or string.
    if not isinstance(data["rooms"], dict):
        raise ConfigError("'rooms' must be a JSON object")

    # start with empty dict of rooms that will fill with Room objects.
    rooms: dict[str, Room] = {}

    # Loop through each room in the JSON.
    for room_name, room_data in data["rooms"].items():
        if not isinstance(room_name, str):
            raise ConfigError(
                f"Room names must be strings; got {type(room_name).__name__!r}"
            )
        # make sure each room has required fields. 
        # if not, shows a config error with the room name and missing field.
        for field in ("description", "exits"):
            if field not in room_data:
                raise ConfigError(
                    f"Room '{room_name}' is missing required field '{field}'"
                )
        if not isinstance(room_data["exits"], dict):
            raise ConfigError(f"Room '{room_name}' exits must be a JSON object")

        # Start with no item in the room. 
        item: Optional[Item] = None
        raw_item = room_data.get("item")

        #if there is an item, validate it has the required fields and create an Item object.
        if raw_item is not None:
            if (
                not isinstance(raw_item, dict)
                or "name" not in raw_item
                or "description" not in raw_item
            ):
                raise ConfigError(
                    f"Room '{room_name}' item must be an object with 'name' and 'description'"
                )
            # Build the item object from the JSON data.
            item = Item(name=raw_item["name"], description=raw_item["description"])

        # Build the Room object and add it to the rooms dict.
        rooms[room_name] = Room(
            name=room_name,
            description=room_data["description"],
            exits={k.lower(): v for k, v in room_data["exits"].items()},
            item=item,
        )
    
    # Grab the values for the start_room and win_room
    start_room: str = data["start_room"]
    win_room: str = data["win_room"]

    # Start_room and win_room must be defined in the rooms dict.
    if start_room not in rooms:
        raise ConfigError(f"start_room '{start_room}' is not defined in rooms")
    if win_room not in rooms:
        raise ConfigError(f"win_room '{win_room}' is not defined in rooms")

    # Loop through every room and exit
    # make sure each one points to a valid room. 
    # if not, shows a config error. 
    for room_name, room in rooms.items():
        for direction, target in room.exits.items():
            if target not in rooms:
                raise ConfigError(
                    f"Room '{room_name}' exit '{direction}' points to undefined room '{target}'"
                )

    # build and return the World object with all the rooms and config values.
    return World(
        rooms=rooms,
        start_room=start_room,
        win_room=win_room,
        items_required=int(data["items_required"]),
    )
