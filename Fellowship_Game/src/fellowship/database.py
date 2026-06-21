#SQLite persistence: saving, loading, run history, and stats.
#This is the only module that talks to the database. It does no console I/O —
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from fellowship.exceptions import SaveLoadError
from fellowship.placement import place_items
from fellowship.player import Player
from fellowship.game import Game
from fellowship.world import load_world

# Paths to the schema and world config files, relative to this module. 
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
WORLD_JSON = Path(__file__).parent / "config" / "world.json"

# Constants for run outcomes. Only two options, win or loss. 
OUTCOME_WIN = "win"
OUTCOME_LOSS = "loss"

# Constants for stats when there are no games. 
ZERO_WIN_RATE = 0.0
ZERO_AVG_MOVES = 0.0

# Open a SQLite connection 
def connect(db_path: str | Path) -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as exc:
        raise SaveLoadError(f"Could not open database at '{db_path}': {exc}") from exc

# Create the tables if they don't exist
def init_db(conn: sqlite3.Connection) -> None:
    try:
        # Load the table definitions from schema.sql and run them in one shot.
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema_sql)
        conn.commit()
    except (OSError, sqlite3.Error) as exc:
        raise SaveLoadError(f"Could not initialise database schema: {exc}") from exc

# returns the current timestamp as a string for recording when saves and runs happen. 
def _now() -> str:
    return datetime.now().isoformat(sep=" ", timespec="seconds")

# Writes the player's current state to the database, returning the assigned save id.
def save_game(conn: sqlite3.Connection, player: Player, game: Game) -> int:
    # Inventory holds Item objects; store just the names and re-resolve them to
    # real items on load. visit_counts is already a name -> count dict.
    inventory_names = [item.name for item in player.inventory]
    inventory_json = json.dumps(inventory_names)
    visit_counts_json = json.dumps(player.visit_counts)

    try:
        cursor = conn.cursor()
        # Values go in as ? placeholders
        # User input is treated as data, never as SQL code (prevents injection).
        cursor.execute(
            "INSERT INTO saves "
            "(player_name, current_room, seed, inventory, visit_counts, saved_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                player.name,
                player.current_room,
                game.seed,
                inventory_json,
                visit_counts_json,
                _now(),
            ),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as exc:
        raise SaveLoadError(f"Could not save game: {exc}") from exc

# rebuilds a saved game and return a ready-to-play game. 
def load_game(conn: sqlite3.Connection, save_id: int) -> Game:
    try:
        cursor = conn.cursor()
        # ? placeholder keeps the id as data, not executable SQL.
        cursor.execute(
            "SELECT player_name, current_room, seed, inventory, visit_counts "
            "FROM saves WHERE id = ?",
            (save_id,),
        )
        row = cursor.fetchone()
    except sqlite3.Error as exc:
        raise SaveLoadError(f"Could not read save #{save_id}: {exc}") from exc

    # No row means the id was wrong; surface it as a SaveLoadError, not None.
    if row is None:
        raise SaveLoadError(f"No save found with id {save_id}.")

    seed = row["seed"]
    inventory_names = json.loads(row["inventory"])
    visit_counts = json.loads(row["visit_counts"])

    # Rebuild the world from world.json, then replay placement with saved seed.
    world = load_world(WORLD_JSON)
    items = [room.item for room in world.rooms.values() if room.item is not None]
    place_items(world, items, seed)

    # Pull saved items out of the world and into the player's inventory.
    player = Player(name=row["player_name"], current_room=row["current_room"])
    restored_inventory = []
    for name in inventory_names:
        for room in world.rooms.values():
            if room.item is not None and room.item.name == name:
                restored_inventory.append(room.item)
                room.item = None
                break

    # Overrides fresh state with saved state
    player.inventory = restored_inventory
    player.visit_counts = visit_counts

    # Rebuild the Game with the saved seed so traps and drops replay identically.
    return Game(world=world, player=player, seed=seed)

# Records a finished run to database. 
def record_run(
    conn: sqlite3.Connection,
    player_name: str,
    seed: int,
    outcome: str,
    moves: int,
    items_collected: int,
) -> int:
    try:
        cursor = conn.cursor()
        # Parameterised INSERT, timestamped here so the caller stays simple.
        cursor.execute(
            "INSERT INTO runs "
            "(player_name, seed, outcome, moves, items_collected, finished_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (player_name, seed, outcome, moves, items_collected, _now()),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as exc:
        raise SaveLoadError(f"Could not record run: {exc}") from exc

# Reads all runs for a player and calculates stats.
def get_stats(conn: sqlite3.Connection, player_name: str) -> dict:
    try:
        cursor = conn.cursor()

        # Count wins and losses with separate parameterised queries. 
        # Filtering by both player_name and outcome keeps each count to one player.
        cursor.execute(
            "SELECT COUNT(*) FROM runs WHERE player_name = ? AND outcome = ?",
            (player_name, OUTCOME_WIN),
        )
        wins = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM runs WHERE player_name = ? AND outcome = ?",
            (player_name, OUTCOME_LOSS),
        )
        losses = cursor.fetchone()[0]

        # Get the average moves per win, filtering to just wins. 
        cursor.execute(
            "SELECT AVG(moves) FROM runs WHERE player_name = ? AND outcome = ?",
            (player_name, OUTCOME_WIN),
        )
        avg_moves_raw = cursor.fetchone()[0]
    except sqlite3.Error as exc:
        raise SaveLoadError(f"Could not read stats: {exc}") from exc

    # Calculate win rate 
    total_games = wins + losses
    win_rate = (wins / total_games) if total_games > 0 else ZERO_WIN_RATE

    # Calculate average moves per win
    avg_moves_per_win = (
        float(avg_moves_raw) if avg_moves_raw is not None else ZERO_AVG_MOVES
    )

    return {
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_moves_per_win": avg_moves_per_win,
    }
