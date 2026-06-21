# Tests for game.py: win/loss paths, command behavior, guard rails.
from __future__ import annotations

# imports three main classes to get the game setup for testing.  
from fellowship.game import Game
from fellowship.player import Player
from fellowship.world import World

# helper function to create a fresh game instance for each test, using the provided world fixture.
def _fresh_game(world: World) -> Game:
    player = Player(name="Gandalf", current_room=world.start_room)
    return Game(world=world, player=player)

# test function that does full playthrough, following a sequence of commands that should win. 
def test_full_playthrough_wins(full_world: World) -> None:
   
    #creates a new game
    game = _fresh_game(full_world)
    
# defines a list of commands that represent the winning path through the game.
    commands = [
        "get Seeing Stone",
        "north", "get Staff of Gandalf",
        "east",  "get Mythril Armor",
        "west",  "south", "south", "get Light of Galadriel",
        "east",  "get Helmet of Eowyn",
        "west",  "north", "west", "get Lothlorien Bow",
        "east",  "east",  "get Sword of Gondor",
        "north",
    ]

    # goes through each command. if game is over, it breaks out of the loop. 
    for cmd in commands:
       
       #stops sending commands if game is over. 
        if game.is_over():
            break
        game.process_command(cmd)

    # checks that the game ended with a win outcome.
    assert game.outcome() == "win"

# test function that simulates entering the dungeon without any items, which should result in a loss.
def test_entering_dungeon_without_items_loses(full_world: World) -> None:
    game = _fresh_game(full_world)
    game.process_command("east") 
    game.process_command("north")
    assert game.outcome() == "loss"

# test function that checks if invalid move returns a string message instead of raising an exception.
def test_invalid_move_returns_string_not_exception(full_world: World) -> None:
    game = _fresh_game(full_world)
    game.process_command("west")       # -> West Wing
    result = game.process_command("north")  # no north exit from West Wing
    assert isinstance(result, str)
    assert len(result) > 0

# test function that checks if getting an item adds it to the player's inventory and removes it from the room.
def test_get_item_adds_to_inventory_and_clears_room(full_world: World) -> None:
    game = _fresh_game(full_world)
    start_room = full_world.rooms[full_world.start_room]
    item_name = start_room.item.name  
    game.process_command(f"get {item_name}")
    assert any(i.name == item_name for i in game.player.inventory)
    assert start_room.item is None

# test function that checks if commands after game is over tell the player the game is done.
def test_commands_after_game_over_return_already_over(full_world: World) -> None:
    game = _fresh_game(full_world)
    game.process_command("east")
    game.process_command("north")   
    result = game.process_command("north")
    assert "already over" in result.lower()
