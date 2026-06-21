#Shared pytest fixture for the game. 
from __future__ import annotations

#import tooling
import json                                                      #turns python dics into json strings and back
from pathlib import Path                                         #working with file paths
import pytest                                                    #testing framework  

#import the World class and the load_world function from the fellowship package
from fellowship.world import World, load_world

#Fixtures are reusable components that can be used across multiple test functions. 
@pytest.fixture
def minimal_world_data() -> dict:
    #return a dictionary representing a minimal world configuration
    #used for tests so we don't have to load the full world from a file every time
    return {
        "start_room": "Start",                                   #the room where the player starts
        "win_room": "End",                                       #the room that the player needs to reach to win
        "items_required": 1,                                     #how many items the player needs to collect to win
        "rooms": {
            "Start": {
                "description": "The beginning.",
                "exits": {"north": "End"},                      #going north leads to the End room
                "item": {"name": "Key", "description": "A shiny key."}, #item in the room
            },
            "End": {
                "description": "The finale.",                   #description of the End room
                "exits": {},                                    #no exits from the End room
                "item": None,                                   #no item in the End room
            },
        },
    }

#tmp_path is a built-in pytest fixture that provides a temporary directory for tests to use.
@pytest.fixture
def minimal_world_path(minimal_world_data: dict, tmp_path: Path) -> Path:
    p = tmp_path / "world.json"
    p.write_text(json.dumps(minimal_world_data))                #turns the dict into JSON and writes it to a file
    return p

#load JSON that we just created into a World object using the load_world function
@pytest.fixture
def minimal_world(minimal_world_path: Path) -> World:
    return load_world(minimal_world_path)

#Path to the full world configuration file included in the project
@pytest.fixture
def full_world_path() -> Path:
    return Path(__file__).parent.parent / "src" / "fellowship" / "config" / "world.json"

#Full world loaded from the configuration file, used for tests that need the complete game setup
@pytest.fixture
def full_world(full_world_path: Path) -> World:
    return load_world(full_world_path)