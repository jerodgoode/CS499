#Tests for database.py: save/load round-trip, run history, stats, and the
# parameterised-query (injection-safety) guarantee.
from __future__ import annotations

import sqlite3

import pytest

from fellowship import database
from fellowship.exceptions import SaveLoadError
from fellowship.game import Game
from fellowship.placement import place_items
from fellowship.player import Player
from fellowship.world import load_world

# A fixed seed keeps the placement (and therefore these tests) reproducible.
TEST_SEED = 4242

# In-memory database so tests never access a real file. 
@pytest.fixture
def conn() -> sqlite3.Connection:
    connection = database.connect(":memory:")
    database.init_db(connection)
    yield connection
    connection.close()

# Build a fresh game with items placed, ready for testing save/load and stats.
def _make_game(seed: int = TEST_SEED) -> tuple[Player, Game]:
    world = load_world(database.WORLD_JSON)
    items = [room.item for room in world.rooms.values() if room.item is not None]
    place_items(world, items, seed)
    player = Player(name="Frodo", current_room=world.start_room)
    game = Game(world=world, player=player, seed=seed)
    return player, game

 # Pick up the first two items found in the world, returning their names.
def _collect_two_items(player: Player, game: Game) -> list[str]:
    collected: list[str] = []
    for room in game.world.rooms.values():
        if room.item is not None and len(collected) < 2:
            player.pick_up(room.item)
            collected.append(room.item.name)
            # Picking an item up removes it from the room, just like in play.
            room.item = None
    return collected

# Test that saves a game and then loads it back. 
# The core state should stay the same. 
def test_save_load_round_trip(conn: sqlite3.Connection) -> None:
    player, game = _make_game()
    collected = _collect_two_items(player, game)

    # Move the player somewhere other than the start and give them a known
    # visit history so we can confirm every field survives the round trip.
    player.current_room = game.world.win_room
    player.visit_counts = {game.world.start_room: 1, game.world.win_room: 2}

    save_id = database.save_game(conn, player, game)
    restored = database.load_game(conn, save_id)

    # Core state comes back unchanged.
    assert restored.player.current_room == player.current_room
    assert restored.seed == game.seed
    assert restored.player.visit_counts == player.visit_counts
    assert sorted(item.name for item in restored.player.inventory) == sorted(collected)

    # An item that was picked up before saving must not still be lying in a room.
    rooms_after = {
        room.item.name
        for room in restored.world.rooms.values()
        if room.item is not None
    }
    for name in collected:
        assert name not in rooms_after

# Loading a non-existent save ID raises the expected exception.
def test_load_missing_save_raises(conn: sqlite3.Connection) -> None:
    with pytest.raises(SaveLoadError):
        database.load_game(conn, 999)

# Test that the stats math is correct and that runs for one player don't bleed into another's.
def test_run_history_and_stats_math(conn: sqlite3.Connection) -> None:
    # A known mix: two wins (10 and 20 moves) and one loss for the same player.
    database.record_run(conn, "Aragorn", TEST_SEED, database.OUTCOME_WIN, 10, 7)
    database.record_run(conn, "Aragorn", TEST_SEED, database.OUTCOME_WIN, 20, 7)
    database.record_run(conn, "Aragorn", TEST_SEED, database.OUTCOME_LOSS, 5, 3)
    # A different player's run must not bleed into Aragorn's stats.
    database.record_run(conn, "SamWise", TEST_SEED, database.OUTCOME_WIN, 99, 7)

    # The stats for Aragorn should reflect only his runs, and the derived numbers should be correct.
    stats = database.get_stats(conn, "Aragorn")
    assert stats["wins"] == 2
    assert stats["losses"] == 1
    assert stats["win_rate"] == pytest.approx(2 / 3)
    assert stats["avg_moves_per_win"] == pytest.approx(15.0)

# Stats for a player with no runs should be zero
def test_stats_with_no_runs_does_not_divide_by_zero(conn: sqlite3.Connection) -> None:
    stats = database.get_stats(conn, "Nobody")
    assert stats["wins"] == 0
    assert stats["losses"] == 0
    # Both derived numbers fall back to zero instead of raising.
    assert stats["win_rate"] == 0
    assert stats["avg_moves_per_win"] == 0

# Test that parameterised queries resist SQL injection.
def test_parameterised_queries_resist_injection(conn: sqlite3.Connection) -> None:
    malicious_name = "Robin'); DROP TABLE runs;--"
    database.record_run(conn, malicious_name, TEST_SEED, database.OUTCOME_WIN, 12, 7)

    # The table still exists and is queryable.
    stats = database.get_stats(conn, malicious_name)
    assert stats["wins"] == 1

    # The value round-trips as the exact literal string it went in as.
    cursor = conn.cursor()
    cursor.execute("SELECT player_name FROM runs WHERE outcome = ?", (database.OUTCOME_WIN,))
    assert cursor.fetchone()[0] == malicious_name

    # A save with the same malicious_name also round-trips intact.
    player, game = _make_game()
    player.name = malicious_name
    save_id = database.save_game(conn, player, game)
    restored = database.load_game(conn, save_id)
    assert restored.player.name == malicious_name
