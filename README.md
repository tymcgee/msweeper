# msweeper
Minesweeper clone written in Python using pygame

This was a quick little project to pass some time during a school break. During its creation I learned and experimented with
- Using a class to represent the main window in pygame (this is useful for being able to reference window attributes from within functions without making them global variables)
- Writing a flood-filling algorithm (which was actually pretty simple; yay recursion!)
- Dealing with a whole lot of edge cases in the game logic, especially after adding the top bar and working with nonsquare grids.

Things I'd like to try in the future if I ever get around to it:
- Center the grid if it's not square
- Add a menu for choosing difficulty (easy/intermediate/expert) and/or allow for custom grid sizes and mine numbers
