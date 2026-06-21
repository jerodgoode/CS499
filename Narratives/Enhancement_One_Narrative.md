# Enhancement One Narrative

## ARTIFACT DESCRIPTION
The artifact is a text-based adventure game called The Fellowship & The Balrog, written for my final project in IT140, back in 2022. The player takes on the role of Gandalf, who has fallen into the Mines of Moria. In order to escape, he must navigate room to room and collect all 7 of the Fellowships items in order to defeat the Balrog and escape the mines. The original game file was about 80 lines all on a single file, with no Object Oriented Programming, no modulization, and no functions besides two small helper functions.

##REASON FOR CHOOSING THIS PROJECT
This enhanced version is a proper package under src/fellowship/, with the world model (world.py), player state (player.py), game loop (game.py), a command-line interface, or CLI (cli.py) and custom exceptions (exceptions.py). The game world loads from world.json config file, the package runs with python -m fellowship, and a pytest suite covers world loading, player behavior, and game outcomes. 
The enhancements specifically showcase several new components compared to the old code base.
•	Modular design and separation of concerns. Separation of concerns is a software design principle that divides the application into distinct modules, each with their own feature. This allows “each component to be simpler and more easily understood” (Johnson, 2026). In this game, the World class only knows about rooms and items, the Player class only knows about state and inventory, and the Game class only knows about rules of the game. The CLI is the only layer that touches input() and print(). This allows for me to write tests and makes the game scalable, in the event that I ever wanted to add a UI. 
•	Defensive programming and input validation. The load_world function validates the JSON config file before the game can start. It checks if top level keys (for key in ("start_room", "win_room", "items_required", "rooms"):), room exits point to defined rooms, and that all items have a name and description. Anything corrupted will throw a ConfigError with a message of what went wrong. In game.py, user input is trimmed, length-capped at 200 chars, and lowercased so the command parser never handles anything unexpected. 
•	Custom Exceptions. All game errors inherit from FellowshipError, so callers can catch the entire family with one except clause or handle specific subclasses. 
•	Automated Testing. The pytest uses shared fixtures in conftest.py to build a minimal in-memory world for unit tests and load the full world for integration tests. Tests cover a full winning playthrough, losing by entering the Dungeon empty handed or not having all the items, invalid moves, etc…
•	Packaging. pyproject.toml makes it pip-installable. __main__.py makes it runnable as a module.

## COURSE OUTCOMES
Outcome 2 is supported by the code’s in-line comments throughout each module, a instructional README.md file, and descriptive error messages that explain exactly what went wrong. Together, these make the code far more readable to other developers. Outcome 4 is supported by the use of modern python tools like pyproject.toml, argparse, and dataclasses. Outcome 5 begins the scratch the surface of secure coding by implementing input cap length, JSON validation, and custom exceptions. However more security implementations will be added in future developments.

## CONCLUSION
One thing I realized is that when starting this project was about how much goes into designing before you write the program itself. The design differs so much from the original program. When it was all on one file, there wasn’t anything to really think about, but with separated concerns, I had to make real decisions. What started as a small text game turned into a real exercise in thinking as a software engineer. The structure I built here is the foundation for the next two future enhancements.



## References
Johnston, B. P. (2026, January 5). Separation of concerns - embedded artistry. Embedded Artistry. https://embeddedartistry.com/fieldmanual-terms/separation-of-concerns/ 
