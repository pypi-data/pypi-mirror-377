# puzzle_game

لعبة ألغاز 8-puzzle باستخدام خوارزمية BFS لحلها.

## التثبيت

```bash
pip install puzzle-game

##الاستخدام
from puzzle_game import Puzzle, bfs_solve

puzzle = Puzzle()
puzzle.shuffle(10)
solution, expanded, time_taken = bfs_solve(puzzle)
