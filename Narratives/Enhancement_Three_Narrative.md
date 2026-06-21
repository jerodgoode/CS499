# Enhancement Three Narrative

## INTRODUCTION
For this third and final enhancement, I continued to use the same artifact from my first enhancement, The Fellowship & The Balrog text based game that I wrote for my final project in IT140. I took the single, 80ish line script file and expanded it into a modular object-oriented package, which laid the foundation to build upon for the remaining enhancements. The first enhancement saw the creation of the game rules, player, and world environment. The second enhancement added in the algorithms and data structures for the hints and trap door additions. This enhancement adds a database.py module and schema.sql files so that game can save mid-run, reload later, and record every result of each game played. 

## REASON FOR CHOOSING THIS PROJECT
Refactoring an old final project from my first year at SNHU seemed like a fitting project to close out my experience and time here. This original project was the perfect idea to implement more advanced features like a BFS algorithm, object oriented design, a binary-search lockpick puzzle, and seeded item placement. Now adding in a database to keep track of records and being able to save games and reload them finishes off the game nicely. 

## ADDED ENHANCEMENTS
•	Relational Schema: The saves table holds in-progress game state, and the runs table records one row per finished game with the seed, outcome, move count, items collected, and timestamp. Inventory and visit counts are stored as JSON text. 
•	Parameterized Queries: Instead of building queries by gluing strings together, every value goes into the SQL as a ? placeholder and gets filled by the driver. By separating data from query logic, parameterized queries mitigate the risk of SQL injection attacks and enable efficient query optimization (Shiferaw, 2023). 
•	Stats and Run History: The –-stats command runs a few parameterized SELECT queries for total wins and losses, win rate, and average moves per win. I also checked that a new player does not crash on a divide by zero. 
•	Dependency injection and testing: Instead of the database connection being set up once and shared everywhere, each function is handed the connection it should use. This way the tests hand in an in-memory database so they’re never accessing a real file. 

## COURSE OUTCOMES
This enhancement supports Outcome 4 by designing a relational schema and integrating a real database into the application without breaking the existing code. Outcome 5 is supported by parameterized queries defending against SQL injection. This established the 
security mindset I started in the first enhancement with input validations and custom exceptions. 

## REFERENCES
Shiferaw, A. (2023, June 25). Understanding parameterized queries. Medium. https://medium.com/@abelzerihun/understanding-parameterized-queries-3c4d81acbf41
