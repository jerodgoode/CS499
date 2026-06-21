# Enhancement Two Narrative

## Introduction
For this second enhancement, I continued to use the same artifact from my first enhancement, The Fellowship & The Balrog text based game that I wrote for my final project in IT140. In the first enhancement, I took the single file, 80ish line script into a modular object-oriented package, which laid the foundation to build upon for the second stage enhancement this week. The first enhancement saw the creation of the game rules, player, and world environment. This enhancement adds in the algorithms and data structures for the hints and trap door additions. 

### Graph traversal with breadth-first search: 
Breadth-first search (BFS) algorithm here operates as a hint system, that goes out and searches for the closest room that contains an item that the player needs. BFS uses a queue to explore the graph "one level at a time" (Joshi, 2017), checking every room one step away before it looks at rooms two steps away, and so on outward. Because the rooms are discovered in order of how many steps away they are, the first matching room the search reaches is the closest one.  The game keeps track of rooms I've already checked so the loop doesn’t run continuously, and it also remembers the first direction taken toward each room, so the hint comes back as a single direction to go rather than a whole list of rooms. 

### Number guessing game: 
Every time a player enters a room, the game counts the visit, and on the third visit gives away, trapping the player in a lockpick puzzle. The puzzle is solved by guessing a number between 1 and 100 within 7 attempts, with higher or lower after each guess. The seven attempts are by design since binary search can solve a range of 100 in at most 7 guesses. There is no luck with this design concept. 

### Seeded random placement: 
At the start of each game the items are shuffled into the rooms using a seeded random generator. The same seed always produces the same layout, so particular runs are replayable, but a new game scatters new items in a new pattern. In the old version, the items were in the same room every time, making extremely easy to memorize with no variation. 

### Logic and Testing:  
In line with the first enhancement, I kept the search logic separate from input and output. The comparison, visit-counting, and item-drop functions have print or input in them, so I could test them directly while the interactive loop stayed in the CLI. Pytest grew from 15 tests to 24 to cover BFS hint system, the binary search, and item placement. 

## Course Outcomes
Outcome 3 is supported by the BFS hint system, a well-known algorithm returning a single direction instead of a whole path. Outcome 4 is supported by the use of graphs, BFS, and seeded randomness. These were not chosen just to implement them, but because they are actual solutions to a problem with the game’s original structure. 

## Conclusions
At the start with this enhancement, we had a solid foundation, but it was a pretty boring structure. This made the structure interesting by adding the hint system with the BFS algorithm and the lockpick binary-search puzzle. The next enhancement will to be adding a database so that players can track and save their game between sessions. 
