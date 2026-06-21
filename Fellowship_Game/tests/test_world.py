 #Tests for world.py: load_world validation and structure. 
from __future__ import annotations

#import tooling for debugging
import json
from pathlib import Path

#import testing framework
import pytest

#import the code being tested
from fellowship.exceptions import ConfigError
from fellowship.world import World, load_world

#test that a good configuration file loads correctly and that the expected rooms are present
def test_valid_json_loads_correctly(minimal_world_path: Path) -> None:
    world = load_world(minimal_world_path)

    #check that each field was read correctly and that the rooms were loaded
    assert isinstance(world, World)
    assert world.start_room == "Start"
    assert world.win_room == "End"
    assert world.items_required == 1

    #check that the expected rooms are present
    assert "Start" in world.rooms
    assert "End" in world.rooms

#test that missing "start_room" key raises ConfigError 
def test_raises_on_missing_start_room_key(tmp_path: Path, minimal_world_data: dict) -> None:
    del minimal_world_data["start_room"]
    p = tmp_path / "w.json"
    p.write_text(json.dumps(minimal_world_data))
    with pytest.raises(ConfigError, match="start_room"):
        load_world(p)

#test that an exit pointing to a non-existent room raises ConfigError
def test_raises_on_dangling_exit_target(tmp_path: Path, minimal_world_data: dict) -> None:
    minimal_world_data["rooms"]["Start"]["exits"]["south"] = "GhostRoom"
    p = tmp_path / "w.json"
    p.write_text(json.dumps(minimal_world_data))
    with pytest.raises(ConfigError, match="GhostRoom"):
        load_world(p)

# test that trying to load from a file that doesn't exist raises ConfigError
def test_raises_on_nonexistent_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_world(tmp_path / "missing.json")

# test that a file containing text isn't valid JSON raises ConfigError
def test_raises_on_malformed_json(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("not { valid json")
    with pytest.raises(ConfigError):
        load_world(p)
