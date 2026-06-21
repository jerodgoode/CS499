-- Table definitions for the SQLite persistence layer.
-- CREATE TABLE IF NOT EXISTS keeps re-running setup safe: tables are only
-- created the first time and left untouched on every run after that.

-- One row per saved-in-progress game. The seed plus the player's state is
-- everything needed to rebuild a run exactly where it was left off.
CREATE TABLE IF NOT EXISTS saves (
    id            INTEGER PRIMARY KEY,
    player_name   TEXT NOT NULL,
    current_room  TEXT NOT NULL,   -- room name the player is standing in
    seed          INTEGER NOT NULL,
    inventory     TEXT NOT NULL,   -- JSON list of item names
    visit_counts  TEXT NOT NULL,   -- JSON dict of room name -> visit count
    saved_at      TIMESTAMP NOT NULL
);

-- One row per finished game (a win or a loss). This history is what the
-- stats screen reads from.
CREATE TABLE IF NOT EXISTS runs (
    id               INTEGER PRIMARY KEY,
    player_name      TEXT NOT NULL,
    seed             INTEGER NOT NULL,
    outcome          TEXT NOT NULL,   -- 'win' or 'loss'
    moves            INTEGER NOT NULL,
    items_collected  INTEGER NOT NULL,
    finished_at      TIMESTAMP NOT NULL
);
