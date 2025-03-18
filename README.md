# Minesweeper
- Minesweeper game in Python using Tkinter library
- Requirements: python 3.10, pillow 10.2
- Gameplay guidance:
    - Left click **empty** square to open
    - Right click to flag/unflag
    - Left click **non-empty** square to **automate** trivial case
    - Click **"Exit"** to save the records permanently
- Press **s** to visualize the solver
- **Guarantee** ability to solve the whole grid without guessing
    - Idea taken from [Mines from Simon Tatham's Puzzle Collection](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html)
    - Use a **different strategy** to alter the map

- BUG: cannot run with python managed by rye

