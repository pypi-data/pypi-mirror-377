
from collections import deque
import time

class Puzzle:
    def __init__(self, size=3):
        self.size = size
        self.tiles = list(range(1, size*size)) + [0]
        self.empty_pos = size*size - 1
        self.solved_state = tuple(list(range(1, size*size)) + [0])
        
    def shuffle(self, moves=20):
        # نخلط اللعبة بتحريك القطع بشكل عشوائي
        for _ in range(moves):
            moves = self.get_valid_moves()
            move = random.choice(moves)
            self.move(move)
    
    def get_valid_moves(self):
        moves = []
        row, col = self.empty_pos // self.size, self.empty_pos % self.size
        
        if row > 0: moves.append((row-1, col))  # أعلى
        if row < self.size-1: moves.append((row+1, col))  # أسفل
        if col > 0: moves.append((row, col-1))  # يسار
        if col < self.size-1: moves.append((row, col+1))  # يمين
        
        return moves
    
    def move(self, pos):
        row, col = pos
        idx = row * self.size + col
        if pos in self.get_valid_moves():
            self.tiles[self.empty_pos], self.tiles[idx] = self.tiles[idx], self.tiles[self.empty_pos]
            self.empty_pos = idx
    
    def is_solved(self):
        return tuple(self.tiles) == self.solved_state
    
    def get_state(self):
        return tuple(self.tiles)
    
    def copy(self):
        new_puzzle = Puzzle(self.size)
        new_puzzle.tiles = self.tiles[:]
        new_puzzle.empty_pos = self.empty_pos
        return new_puzzle
    
    def print_board(self):
        for i in range(self.size):
            row = []
            for j in range(self.size):
                tile = self.tiles[i*self.size+j]
                row.append(str(tile) if tile != 0 else ' ')
            print(' | '.join(row))
            if i < self.size - 1:
                print('-' * (self.size * 4 - 3))
        print()

def bfs_solve(puzzle):
    start_state = puzzle.get_state()
    queue = deque([(puzzle.tiles[:], [])])  # (الحالة, المسار)
    visited = set([start_state])
    nodes_expanded = 0
    
    start_time = time.time()
    
    while queue:
        current_tiles, path = queue.popleft()
        nodes_expanded += 1
        
        current_puzzle = Puzzle(puzzle.size)
        current_puzzle.tiles = current_tiles
        current_puzzle.empty_pos = current_tiles.index(0)
        
        if current_puzzle.is_solved():
            end_time = time.time()
            return path, nodes_expanded, end_time - start_time
        
        for move in current_puzzle.get_valid_moves():
            new_puzzle = current_puzzle.copy()
            new_puzzle.move(move)
            new_state = new_puzzle.get_state()
            
            if new_state not in visited:
                visited.add(new_state)
                new_path = path + [move]
                queue.append((new_puzzle.tiles[:], new_path))
    
    end_time = time.time()
    return None, nodes_expanded, end_time - start_time

def print_solution_steps(initial_puzzle, solution):
    if not solution:
        print("لم يتم إيجاد حل للغز.")
        return
    
    current_puzzle = initial_puzzle.copy()
    print("الحالة الابتدائية:")
    current_puzzle.print_board()
    
    for step, move in enumerate(solution, 1):
        current_puzzle.move(move)
        print(f"الخطوة {step}: تحريك القطعة في الصف {move[0]+1}, العمود {move[1]+1}")
        current_puzzle.print_board()
    
    print("تم حل اللغز!")

# اختبار الخوارزمية
if __name__ == "__main__":
    import random
    
    # إنشاء لغز 3x3
    puzzle = Puzzle(3)
    
    # خلط اللغز
    puzzle.shuffle(10)
    
    print("حالة اللغز الأولية:")
    puzzle.print_board()
    
    # حل اللغز باستخدام BFS
    solution, nodes_expanded, time_taken = bfs_solve(puzzle.copy())
    
    if solution:
        print(f"تم إيجاد حل في {len(solution)} خطوة")
        print(f"عدد الحالات التي تم فحصها: {nodes_expanded}")
        print(f"الوقت المستغرق: {time_taken:.4f} ثانية")
        
        # عرض خطوات الحل (اختياري)
        show_steps = input("هل تريد عرض خطوات الحل؟ (y/n): ").lower()
        if show_steps == 'y':
            print_solution_steps(puzzle, solution)
    else:
        print("لم يتم إيجاد حل للغز.")