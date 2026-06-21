Welcome to my professional ePortfolio for the Southern New Hampshire University Computer Science program, completed with a concentration in Information Security. The work below centers on a single artifact, a Python text adventure game called *The Fellowship & The Balrog*, enhanced across the three core areas of computer science: software design and engineering, algorithms and data structures, and databases.

---

## Professional Self-Assessment

I started my path to getting my bachelor’s in computer science a little differently than most. Before starting at SNHU, I worked in retail management, specializing in customer service for 15 years, with the majority being in the wine and spirits industry. This is where I learned to listen, figure out what someone actually needs, and stay calm when something breaks. I started the Computer Science program here at SNHU to turn a long-time curiosity for computers and software into a career for myself. I chose Information Security because I had an interest in securing systems and protecting an organization against cyber threats. About 7 months ago, I got an opportunity to make the transition from the retail world to the tech industry as a Cloud Support Engineer at Lambda, a GPU cloud provider, which let me to put what I was learning to use right away. Building this ePortfolio has been a way to bring all that together. 

Collaboration runs through both my coursework and my job. At Lambda, I work on a support team where problems are rarely solved by myself. A GPU cluster issue usually means that I am collaborating with different engineering teams, establishing communication channels with the customer, and keeping everything aligned until it is resolved. To help improve our metrics, I’ve implemented the 4DX framework to our ticket process and built a small command-line tracker for our lead measures, which helped reduce our mean time to close from more than 30 days to an average of 3 days. 

Communicating with stakeholders is something that I do on a daily basis. They want to know what is wrong, what I am doing about it, and when it will be fixed. Turning a technical problem into plain language without losing accuracy is a skill I built over years of customer work and sharpened at Lambda. The program reinforced it by making me write for different audiences, from design documents to artifact narratives to a recorded walkthrough.

My foundation in data structures and algorithms comes courses like CS-370. I worked through deep Q-learning on the CartPole and pirate-maze problems, trained convolutional networks on image data, and studied how systems like AlphaGo learn. I learned a lot about taking a minute to think about what structure would be the best fit, as opposed to what works right now. 

Software engineering and databases are where I have grown the most. CS 250 taught me the software development life cycle and the habit of designing before writing code, and DAD 220 gave me my SQL foundation. Outside the program I built a retrieval-based donor research tool for a family member's nonprofit, wiring together a vector database, an API, and a React front end to turn messy records into answers someone could actually use. That project, more than any single class, showed me how the pieces of a real application fit together.

Security is the thread that ties the rest together. CS320, Software Test-Automation QA taught me to treat tests as a way to prove the code actually does what I claim, and that idea is what pushed me to build a real test suite into my enhancements rather than just checking things by hand. I leaned on it most on the security side. The test that throws a SQL injection payload at the database and confirms it gets stored as harmless text came directly from that habit, and so did the tests around input validation and error handling.

The artifacts that follow this assessment are one project shown three ways. Rather than submit three unrelated pieces, I took a single artifact, my text adventure game, and enhanced it across the three core areas of the field: software design and engineering, algorithms and data structures, and databases. Together they trace the same code from a rough script to a tested, secure, persistent application, which is the clearest way I could show growth across the whole program in one place.

Finishing this degree while working full time has been demanding, but it confirmed the direction I want to go. I want to keep building toward infrastructure and security-focused engineering, where my support background, my Linux and Python skills, and my security training come together. This portfolio is the evidence behind that goal.

## Course Outcomes

**Outcome 1, collaborative environments.** I met this through the code review I completed before starting any enhancements. Walking through the original code, analyzing it against a review checklist, and laying out a plan is the same work a team does to decide where a codebase should go. The thorough in-code comments in the enhanced version support the same goal, since they let another developer pick the project up and contribute.  

**Outcome 2, professional communication.** I met this through the written narratives, the project README, and the recorded code review. Each one takes the same technical material and adapts it for a specific audience, in writing, on screen, and out loud, with clear error messages doing the same job inside the program itself.

**Outcome 3, algorithmic solutions and trade-offs.** I met this in the algorithms enhancement, where I treated the rooms as a graph and used breadth-first search to point a player toward the nearest item they still need. The lockpick puzzle is bounded so binary search can always solve it, and the hint returns a single direction rather than a full path, both deliberate trade-offs between giving help and keeping the game a challenge.

**Outcome 4, well-founded tools and techniques.** I met this across all three enhancements, by rebuilding the game as a modular, object-oriented package with a pytest suite and a pyproject build, and by adding a SQLite database for saves and run history. These are the same standard tools and patterns used in industry, applied to deliver a working, maintainable product.

**Outcome 5, security mindset.** I met this in the software and database enhancements. I validate the game's configuration when it loads, cap and normalize player input, and raise custom exceptions instead of letting the program crash. Every value that reaches the database goes through a parameterized query, and I wrote a test that throws a SQL injection payload at it to prove the input is stored as harmless text. This is where my Information Security concentration shows up most directly.

---

## Code Review

Before making any enhancements, I recorded a code review of the original artifact. It walks through how the existing code works, analyzes it against a code review checklist, and lays out my plan for each enhancement and how it maps to the program's course outcomes.

  <iframe width="560" height="315"
    src="https://www.youtube.com/embed/JN0WZo90wVw"
    title="CS 499 Code Review"
    frameborder="0"
    allowfullscreen></iframe>

---

## The Artifact

All three enhancements build on the same project, a text based adventure game I first wrote in 2022 for IT 140, Introduction to Scripting. The original was a single Python file of about eighty lines, with the whole world in one dictionary and all the logic in one loop.

**[View the original IT 140 script](https://github.com/jerodgoode/CS499/blob/main/Original_IT140_Project/original_game.py)**

---

## Enhancement One: Software Design and Engineering

I refactored the original procedural script into a modular, object-oriented Python package. The world, player, game rules, and command-line interface each live in their own module, the game world loads from a JSON config file, and a pytest suite covers the major behaviors. This enhancement also adds input validation, custom exceptions, and pip packaging.

- **[Read the narrative](https://github.com/jerodgoode/CS499/blob/main/Narratives/Enhancement_One_Narrative.md)**
- **[Pseudocode](https://github.com/jerodgoode/CS499/blob/main/Pseudocode/Enhancement_One_Pseudocode)**

---

## Enhancement Two: Algorithms and Data Structures

I added the data structures and algorithms that make the game interesting. A hint system uses breadth-first search over the rooms, treated as a graph, to point the player toward the nearest item they still need. A trap-door lockpick puzzle is bounded so that binary search can always solve it, and items are placed each game with a seeded random generator so runs are repeatable but never identical. The test suite grew from fifteen to twenty-four tests to cover the new logic.

- **[Read the narrative](https://github.com/jerodgoode/CS499/blob/main/Narratives/Enhancement_Two_Narrative.md)**
- **[Pseudocode](https://github.com/jerodgoode/CS499/blob/main/Pseudocode/Enhancement_Two_Pseudocode)**

---

## Enhancement Three: Databases

I added a SQLite database so games persist between sessions. A saves table holds an in-progress game and a runs table records every finished game, which feeds a stats command for wins, losses, win rate, and average moves. Every value reaching the database goes through a parameterized query to defend against SQL injection, and a dedicated test fires an injection payload to prove the input is stored as harmless text.

- **[Read the narrative](https://github.com/jerodgoode/CS499/blob/main/Narratives/Enhancement_Three_Narrative.md)**
- **[Pseudocode](https://github.com/jerodgoode/CS499/blob/main/Pseudocode/Enhancement_Three_Pseudocode)**

---

## Final Enhanced Code Base
### The Fellowship and The Balrog

- **[Review the game](https://github.com/jerodgoode/CS499/tree/main/Fellowship_Game)**

---

Southern New Hampshire University | Bachelor of Science in Computer Science | Information Security Concentration
