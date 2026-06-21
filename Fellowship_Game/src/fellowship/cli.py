# Command-line interface for the Fellowship & The Balrog text adventure game.
from __future__ import annotations

import argparse                         # python tool for parsing command-line arguments
import sys                              # prints the error message and exits the program with an error code
from pathlib import Path                # working with file paths 

# imports core game classes and functions
from fellowship import database, placement
from fellowship.algorithms import ALL_ITEMS_COLLECTED, HERE, NO_PATH
from fellowship.exceptions import SaveLoadError
from fellowship.game import Game
from fellowship.player import Player
from fellowship.puzzles import (
    CORRECT,
    HIGHER,
    LOCKPICK_ATTEMPTS,
    LOCKPICK_MAX,
    LOCKPICK_MIN,
    drop_random_item,
    evaluate_guess,
)
from fellowship.world import load_world

# builds the path to the world configuration JSON file, which defines the game world
# underscore prefix means its private to thie module.    
_WORLD_JSON = Path(__file__).parent / "config" / "world.json"

# Where finished-run history and saved games are kept between sessions. A single
# file in the user's home directory, mirroring how ~/.* dotfiles are stored.
DEFAULT_DB_PATH = Path.home() / ".fellowship_game.db"

# Text banner displayed when the game starts
# Triple quotes allow for multi-line strings
BANNER = """
+------------------------------------------------------+
|             THE FELLOWSHIP & THE BALROG              | 
|            "Keep it secret, keep it safe."           |
+------------------------------------------------------+
Gather all 7 items and face the Balrog in the Dungeon.
Items are scattered anew each game. Type 'hint' if you
lose your way, but beware the trap doors that open
beneath rooms if you visit them too many times!
Type 'help' for commands.
"""

def _format_hint(result: str) -> str:
    if result == ALL_ITEMS_COLLECTED:
        return "You carry everything you need. Make for the Dungeon!"
    if result == HERE:
        return "There's an item to pick up right where you're standing."
    if result == NO_PATH:
        return "You sense no path to anything you still need."
    return f"Your instincts pull you {result} toward the nearest item you still need."


def _run_trap_door(game: Game, room_name: str) -> None:
    secret = game.rng.randint(LOCKPICK_MIN, LOCKPICK_MAX)
    print(
        "\nThe floor gives way! You crash into a locked oubliette.\n"
        f"Pick the lock: guess the number between {LOCKPICK_MIN} and "
        f"{LOCKPICK_MAX}. You have {LOCKPICK_ATTEMPTS} attempts."
    )

    # Invalid input does not cost an attempt, so track remaining tries directly
    # rather than relying on a for-loop counter.
    attempts_left = LOCKPICK_ATTEMPTS
    while attempts_left > 0:
        try:
            raw = input(f"  [{attempts_left} left] guess > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nYou wrench yourself free of the trap.")
            game.player.visit_counts[room_name] = 0
            return

        try:
            guess = int(raw)
        except ValueError:
            print("  That's not a number. Try again.")
            continue
        if not LOCKPICK_MIN <= guess <= LOCKPICK_MAX:
            print(f"  Stay between {LOCKPICK_MIN} and {LOCKPICK_MAX}.")
            continue

        attempts_left -= 1
        result = evaluate_guess(secret, guess)
        if result == CORRECT:
            game.player.visit_counts[room_name] = 0
            print("  Click! The lock springs open and you climb back out.")
            return
        if result == HIGHER:
            print("  The tumblers resist -- the number is HIGHER.")
        else:
            print("  The tumblers resist -- the number is LOWER.")

    # All attempts spent without success: lose an item, then free the player.
    dropped = drop_random_item(game.player, game.rng)
    game.player.visit_counts[room_name] = 0
    if dropped is not None:
        print(f"  The lock holds. As you scramble out, you lose {dropped.name}!")
    else:
        print("  The lock holds. You scramble out empty-handed but unharmed.")

# function to print the current room's name, description, exits, and any item present.
# this is called at the start of a new game or when a saved game is loaded. 
def _print_current_room(game: Game) -> None:
    room = game.world.get_room(game.player.current_room)
    print(f"=== {room.name} ===")
    print(room.description)
    if room.exits:
        print("Exits: " + ", ".join(f"{d} -> {t}" for d, t in sorted(room.exits.items())))
    if room.item:
        print(f"Item here: {room.item.name}")
    print()

# function to format the stats dict from the database into a short readable block.
def _print_stats(stats: dict, player_name: str) -> None:

    # Win rate is stored as a 0..1 fraction; show it as a rounded percentage.
    win_rate_pct = stats["win_rate"] * 100
    print(f"Lifetime stats for {player_name}:")
    print(f"  Wins              : {stats['wins']}")
    print(f"  Losses            : {stats['losses']}")
    print(f"  Win rate          : {win_rate_pct:.1f}%")
    print(f"  Avg moves per win : {stats['avg_moves_per_win']:.1f}")


# builds the CLI argument parser which handles command-line options. 
# Keeping this in its own functions allows for easier testing. 
def _build_parser() -> argparse.ArgumentParser:

    # Creates an ArgumentParser object
    parser = argparse.ArgumentParser(
        prog="fellowship",
        description="The Fellowship & The Balrog — a text adventure.",
    )
    # Adds an optional argument for the player's name.
    # If user doesn't add one, it defaults to "Gandalf". 
    parser.add_argument(
        "--player",
        default="Gandalf",
        help="Player name (default: Gandalf)",
    )
    # Seed for reproducible item placement. 
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for reproducible item placement (default: random each game)",
    )
    # Path to the database file for saving game progress and stats.
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to the save/stats database (default: {DEFAULT_DB_PATH})",
    )
    # Argument for loading a saved game by its ID. This allows players to resume a previous game.
    parser.add_argument(
        "--load",
        type=int,
        default=None,
        metavar="ID",
        help="Load and resume a saved game by its id",
    )
    # Prints stats for specified player so user can see their lifetime stats. 
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print lifetime stats for --player and exit without playing",
    )
    return parser

###############################################################################################
###### ----------------------------------MAIN GAME LOOP--------------------------------- ######
###############################################################################################

# this is the main function that runs the game.
# it loads the world, the player, and starts the game loop.
def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    # Open (and create on first run) the database that holds saves and run
    # history, then make sure the tables exist.
    try:
        conn = database.connect(args.db)
        database.init_db(conn)
    except SaveLoadError as exc:
        print(f"Error opening database: {exc}", file=sys.stderr)
        sys.exit(1)

    # --stats just prints history and exits; no world or game is built.
    if args.stats:
        try:
            stats = database.get_stats(conn, args.player)
        except SaveLoadError as exc:
            print(f"Error reading stats: {exc}", file=sys.stderr)
            sys.exit(1)
        _print_stats(stats, args.player)
        return

    if args.load is not None:
        # Resume a saved game: load_game rebuilds the world, replays placement
        # with the saved seed, and restores the player's exact state.
        try:
            game = database.load_game(conn, args.load)
        except SaveLoadError as exc:
            print(f"Error loading save: {exc}", file=sys.stderr)
            sys.exit(1)
        player = game.player
        print(BANNER)
        print(f"Welcome back, {player.name}! Your quest resumes.\n")
    else:
        try:
            world = load_world(_WORLD_JSON)
        except Exception as exc:
            print(f"Error loading world: {exc}", file=sys.stderr)
            sys.exit(1)

        # Shuffle item placement for this run and seed the game from it, so the
        # whole playthrough (layout, traps, drops) is reproducible from
        # game.seed. A caller-supplied --seed reproduces a previous run exactly.
        items = [room.item for room in world.rooms.values() if room.item is not None]
        if args.seed is not None:
            placement.place_items(world, items, args.seed)
            seed = args.seed
        else:
            seed = placement.new_game(world, items)

        player = Player(name=args.player, current_room=world.start_room)
        game = Game(world=world, player=player, seed=seed)

        print(BANNER)
        print(f"Welcome, {player.name}! Your quest begins.\n")

    _print_current_room(game)

    while not game.is_over():
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFarewell.")
            break

        if raw.lower() in ("quit", "exit", "q"):
            print("You abandon the quest. The Fellowship is in peril...")
            break

        # 'save' is a CLI-only command (it touches the database, which game.py
        # must never do), so intercept it before the game processes the line.
        if raw.lower() == "save":
            try:
                save_id = database.save_game(conn, player, game)
                print(f"Game saved as #{save_id}. Resume later with --load {save_id}.")
            except SaveLoadError as exc:
                print(f"Could not save: {exc}")
            print()
            continue

        response = game.process_command(raw)
        if raw.lower() == "hint":
            print(_format_hint(response))
        else:
            print(response)
        print()

        # A move may have sprung a trap door; resolve it before the next prompt.
        if game.pending_trap is not None:
            trapped_room = game.pending_trap
            game.pending_trap = None
            _run_trap_door(game, trapped_room)
            print()

    if game.is_over():
        # The run reached a real ending (win or loss), so record it in history.
        # Quitting early breaks out of the loop above without an outcome, so no
        # row is written for an abandoned game.
        try:
            database.record_run(
                conn,
                player_name=player.name,
                seed=game.seed,
                outcome=game.outcome(),
                moves=game.moves,
                items_collected=len(player.inventory),
            )
        except SaveLoadError as exc:
            print(f"(Could not record run: {exc})")

        if game.outcome() == "win":
            print("Congratulations! The Fellowship endures.")
        else:
            print("The darkness claims victory. Better luck next time.")