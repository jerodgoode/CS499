#Core game logic: command dispatch, win/loss determination, move counter.
from __future__ import annotations

import random

#import custom error type and the main classes for the game.
from fellowship import algorithms, puzzles
from fellowship.exceptions import InvalidMoveError
from fellowship.placement import SEED_MAX
from fellowship.player import Player
from fellowship.world import World

#max imput from player, 200 characters. 
# prevents long inputs that could cause issues.
INPUT_MAX_LEN = 200

# navigation abbr to full direction mapping.
_DIRECTION_ABBREVS: dict[str, str] = {
    "w": "north",
    "s": "south",
    "d": "east",
    "a": "west",
}

# Game class manages the state of a single playthough
# Includes the world, player, move counter, random seed and rng, and pending trap state.
class Game:

    def __init__(self, world: World, player: Player, seed: int | None = None) -> None:
        # store world and player so other methods can access them.
        self.world = world
        self.player = player

        # counter goes up by 1 for each command
        self.moves: int = 0

        # tracks if the game ended and how
        # none = in progress, "win" = player won, "loss" = player lost
        self._outcome: str | None = None
        # seed and rng are used for any random elements in the game, like trap outcomes or item drops.
        self.seed: int = seed if seed is not None else random.randrange(SEED_MAX)
        self.rng = random.Random(self.seed)
        self.pending_trap: str | None = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    # these methods are called by the CLI to run the game.
    def process_command(self, raw: str) -> str:
      
        # if game is over, refuse to process anything else.
        if self.is_over():
            return "The game is already over."

        # trims whitespace, limits input to 200 chars, and lowercases for easier parsing.
        cmd = raw.strip()[:INPUT_MAX_LEN].lower()

        # counts this as a move. 
        self.moves += 1

        # handles empty input if player enters nothing.
        if not cmd:
            return "Please enter a command. Type 'help' for options."

        # handles movemnt commands and movement abbr. 
        if cmd in _DIRECTION_ABBREVS or cmd in _DIRECTION_ABBREVS.values():
            return self._handle_move(cmd)

        # handles get command to pick up items.
        if cmd.startswith("get "):
            item_name = raw.strip()[4:].strip()
            return self._handle_get(item_name)

        # handles look command to describe the current room.
        if cmd in ("look", "l"):
            return self._describe_room()

        # handles inventory command to display the player's inventory.
        if cmd in ("inventory", "inv", "i"):
            return self._describe_inventory()
        
        # handles hint command to give the player a hint based on their current location and inventory.
        if cmd == "hint":
            return algorithms.find_hint(
                self.world, self.player.current_room, self.player.inventory
            )

        # handles help command to show available commands.
        if cmd == "help":
            return self._help_text()

        # returns this message if the command isnt recognized.
        return f"Unknown command: '{cmd}'. Type 'help' for options."

    # returns true if the game has ended.
    def is_over(self) -> bool:
        return self._outcome is not None

    # returns the outcome of the game.
    def outcome(self) -> str | None:
        return self._outcome

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    # These are private methods for game logic. 

    # handles movement commands and checks if player won or lost after moving. 
    def _handle_move(self, direction: str) -> str:

    # if player typed "n" for instance, this converts it to "north"
        direction = _DIRECTION_ABBREVS.get(direction, direction)

        # moves player. if move is invalid, returns error message.
        try:
            destination = self.player.move(direction, self.world)
        except InvalidMoveError as exc:
            return str(exc)

        # if move is successful, this is the message shown to the player.
        msg = f"You move {direction} to {destination}."

        #Checks if player entered the win room (Dungeon). 
        # if so, checks if they have all items to win. 
        # if all items are held, player wins, if not player loses. 
        if destination == self.world.win_room:
            if self.player.has_all_items(self.world.items_required):
                self._outcome = "win"
                msg += (
                    "\n\nThe Fellowship stands ready! You have gathered all the items needed.\n"
                    "YOU DEFEATED THE BALROG — THE FELLOWSHIP PREVAILS!"
                )
            else:
                self._outcome = "loss"
                held = len(self.player.inventory)
                needed = self.world.items_required
                msg += (
                    f"\n\nYou enter the Dungeon with only {held} of {needed} required items.\n"
                    "The Balrog overwhelms you. The Fellowship falls. YOU HAVE LOST."
                )
            return msg
        
        # Track the entry and flag the trap door for the CLI if it opens. The
        # win room is terminal and handled above, so traps only fire elsewhere.
        if puzzles.on_room_entry(self.player, destination):
            self.pending_trap = destination

        #if the room is not the Dungeon, this is the description of the new room. 
        msg += "\n\n" + self._describe_room()
        return msg

    # handles the "get <item>" command to pick up an item from the current room.
    def _handle_get(self, item_name: str) -> str:
        
        # checks to see current room. 
        room = self.world.get_room(self.player.current_room)

        #if no item, return this message.
        if room.item is None:
            return "There is nothing here to pick up."
        
        # if items exists but name of item doesnt match, return this message.
        if room.item.name.lower() != item_name.lower():
            return f"There is no '{item_name}' here."
        
        # player picks up the item, and it is removed from the room.
        # setting room.item to None makes sure item cant be picked up more than once.
        item = room.item
        self.player.pick_up(item)
        room.item = None
        return f"You pick up {item.name}."

    # handles the "look" command to describe the current room and its contents.
    def _describe_room(self) -> str:

        # gets the current room object. 
        room = self.world.get_room(self.player.current_room)
        lines = [f"=== {room.name} ===", room.description]

        # shows the exits from the room. if no exits, says "none".
        if room.exits:
            dirs = ", ".join(
                f"{d} -> {t}" for d, t in sorted(room.exits.items())
            )
            lines.append(f"Exits: {dirs}")
        else:
            # no exits means its either the dungeon or a dead end room.
            lines.append("Exits: none")
        
        # shows the item if theres one in the room. 
        if room.item:
            lines.append(f"Item here: {room.item.name}")

        # Combines all the lines into single string. 
        return "\n".join(lines)

    # handles the "inventory" command to list the items the player is currently carrying.
    def _describe_inventory(self) -> str:

        # Handles empty inventory case. 
        if not self.player.inventory:
            return "Your pack is empty."
        
        # Builds a list of items and shows the count
        names = ", ".join(i.name for i in self.player.inventory)
        return f"Carrying ({len(self.player.inventory)}): {names}"

    # handles the "help" command to show available commands and their descriptions.
    def _help_text(self) -> str:

        # shows all the list of commands and how to use them.
        return (
            "Commands:\n"
            "  north / south / east / west  move in that direction\n"
            "  direction abbr. = /w = north / s = south / a = west / d = east\n"
            "  get <item name>              pick up an item\n"
            "  look                         describe the current room\n"
            "  inventory                    list what you are carrying\n"
            "  hint                         point toward the nearest item\n"
            "  save                         save your progress (resume with --load)\n"
            "  quit / exit                  end the session\n"
            "\n"
            "Beware: lingering in a room too long springs its trap door,\n"
            "and you must pick the lock to climb back out.\n"
        )