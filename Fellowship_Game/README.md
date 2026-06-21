# Fellowship & The Balrog

A terminal-based text adventure where Gandalf must gather the Fellowship's equipment and face the Balrog in the depths of Moria.

## Background

This is CS 499 capstone enhancement of an IT140 final project. The original was a single-file procedural Python script (~80 lines). This version refactors it into a modular OOP package with a BFS hint system, seeded random item placement, a trap-door puzzle, and SQLite persistence.

## Features

- **OOP design** — `World`, `Room`, `Item`, `Player`, and `Game` classes with clear separation of concerns
- **JSON-configured world** — room layout, exits, and items driven by `config/world.json`
- **Input validation** — all config is validated on load; player input is capped and sanitised
- **BFS hint system** — `hint` command finds the shortest path to the nearest uncollected item
- **Seeded item placement** — item positions are shuffled each game and reproducible with `--seed`
- **Trap-door puzzle** — binary-search lockpick fires on the 3rd visit to a room
- **SQLite save/load** — save mid-run and resume later; every finished game is recorded and summarised with lifetime stats, all through parameterised queries

## Installation

```bash
git clone <repo-url>
cd Fellowship_Game
pip install -e ".[dev]"
```

Requires Python 3.11+.

## Usage

```bash
fellowship                           # start a new game as Gandalf
fellowship --player Sam              # play as a custom name
fellowship --seed 1234               # reproduce a specific item layout
fellowship --load 1                  # resume the game saved as #1
fellowship --player Sam --stats      # print Sam's lifetime stats and exit
fellowship --db /path/to/saves.db    # use a specific database file
```

In-game commands:

```
north / south / east / west   move in that direction
get <item name>               pick up an item
look                          describe the current room
inventory                     list what you are carrying
hint                          point toward the nearest uncollected item
save                          save progress (resume later with --load <id>)
quit                          end the session
```

Linger too long in a room and its trap door springs: pick the lock by guessing
a number between 1 and 100 (a binary search wins within the 7 allowed attempts)
or lose a random item from your pack.

## Saves & Stats

Saves and run history live in a SQLite database, `~/.fellowship_game.db` by
default (override with `--db`). Typing `save` mid-game writes the current state
and prints a save id; `fellowship --load <id>` rebuilds that exact game — same
room, inventory, visit counts, and item layout. Every win or loss is recorded
automatically when the game ends, and `--stats` reports wins, losses, win rate,
and average moves per win for a player. Every value reaching SQL is bound through
a `?` placeholder, never built with string formatting.

## Project Layout

```
Fellowship_Game/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── fellowship/
│       ├── __init__.py
│       ├── __main__.py
│       ├── exceptions.py
│       ├── world.py
│       ├── player.py
│       ├── game.py
│       ├── algorithms.py
│       ├── puzzles.py
│       ├── placement.py
│       ├── database.py
│       ├── schema.sql
│       ├── cli.py
│       └── config/
│           └── world.json
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_world.py        # 5 tests
    ├── test_player.py       # 5 tests
    ├── test_game.py         # 5 tests
    ├── test_algorithms.py   # 3 tests
    ├── test_puzzles.py      # 3 tests
    ├── test_placement.py    # 3 tests
    └── test_database.py     # 5 tests
```

## Running Tests

```bash
pytest
```

29 tests across seven files covering the core win/loss paths, config validation, Player
invariants, BFS hint pathfinding, the trap-door lockpick, seeded item placement, and the
SQLite save/load round-trip, run history, stats math, and injection-safety.

## Course Outcomes Mapped

- **Outcome 2 (Software Engineering)** — `world.py`, `player.py`, `game.py`: modular OOP refactor with dataclasses, clear class boundaries, and dependency injection
- **Outcome 3 (Algorithms & Data Structures)** — `algorithms.py`: BFS over the room graph; `placement.py`: seeded Fisher-Yates shuffle; `puzzles.py`: binary-search game loop
- **Outcome 4 (Software Security)** — `cli.py`: input length cap, no `eval`/`exec`; `world.py`: `load_world` validates all structural invariants before the game starts; `database.py`: every value reaching SQL is bound through a `?` placeholder (never string-formatted), and a regression test proves a SQL-injection payload round-trips as a harmless literal
- **Outcome 5 (Databases)** — `database.py`: dependency-injected `sqlite3` save/load/run-history/stats with guarded divisions; `schema.sql`: explicit `CREATE TABLE IF NOT EXISTS` schema for the `saves` and `runs` tables
