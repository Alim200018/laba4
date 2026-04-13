import tkinter as tk
from tkinter import messagebox
from enum import Enum
import random
import copy
from collections import deque
class ReversiGame:
    def __init__(self):
        self.size = 6
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 'black'
        self.black_score = 0
        self.white_score = 0
        self.init_board()
        
    def init_board(self):
        for i in range(self.size):
            for j in range(self.size):
                self.board[i][j] = None
        
        self.board[2][2] = 'white'
        self.board[3][3] = 'white'
        self.board[2][3] = 'black'
        self.board[3][2] = 'black'
        
        self.update_scores()
    
    def update_scores(self):
        self.black_score = 0
        self.white_score = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 'black':
                    self.black_score += 1
                elif self.board[i][j] == 'white':
                    self.white_score += 1
    
    def get_valid_moves(self, player):
        valid_moves = []
        opponent = 'white' if player == 'black' else 'black'
        
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] is None:
                    if self._is_valid_move(i, j, player, opponent):
                        valid_moves.append((i, j))
        return valid_moves
    
    def _is_valid_move(self, row, col, player, opponent):
        if self.board[row][col] is not None:
            return False
        
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False
            
            while 0 <= r < self.size and 0 <= c < self.size:
                if self.board[r][c] == opponent:
                    found_opponent = True
                elif self.board[r][c] == player and found_opponent:
                    return True
                else:
                    break
                r += dr
                c += dc
        return False
    
    def make_move(self, row, col, player):
        if (row, col) not in self.get_valid_moves(player):
            return False
        
        opponent = 'white' if player == 'black' else 'black'
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]
        
        self.board[row][col] = player
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            tiles_to_flip = []
            
            while 0 <= r < self.size and 0 <= c < self.size:
                if self.board[r][c] == opponent:
                    tiles_to_flip.append((r, c))
                elif self.board[r][c] == player:
                    for flip_r, flip_c in tiles_to_flip:
                        self.board[flip_r][flip_c] = player
                    break
                else:
                    break
                r += dr
                c += dc
        
        self.update_scores()
        return True
    
    def has_valid_move(self, player):
        return len(self.get_valid_moves(player)) > 0
    
    def is_game_over(self):
        return (not self.has_valid_move('black') and 
                not self.has_valid_move('white')) or self.is_board_full()
    
    def is_board_full(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] is None:
                    return False
        return True
    
    def get_winner(self):
        if self.black_score > self.white_score:
            return 'black'
        elif self.white_score > self.black_score:
            return 'white'
        else:
            return 'draw'
    
    def get_board_copy(self):
        return copy.deepcopy(self.board)
POSITION_WEIGHTS = [
    [100, -20, 10, 10, -20, 100],
    [-20, -30, 5, 5, -30, -20],
    [10, 5, 1, 1, 5, 10],
    [10, 5, 1, 1, 5, 10],
    [-20, -30, 5, 5, -30, -20],
    [100, -20, 10, 10, -20, 100]
]

MOBILITY_WEIGHT = 5
class AIStrategy:
    
    @staticmethod
    def greedy_move(game, valid_moves, player):
        if not valid_moves:
            return None
        
        best_move = None
        best_count = -1
        
        for move in valid_moves:
            temp_game = ReversiGame()
            temp_game.board = game.get_board_copy()
            
            if temp_game.make_move(move[0], move[1], player):
                count = 0
                for i in range(temp_game.size):
                    for j in range(temp_game.size):
                        if temp_game.board[i][j] == player:
                            count += 1
                
                current_count = game.black_score if player == 'black' else game.white_score
                flipped = count - current_count
                
                if flipped > best_count:
                    best_count = flipped
                    best_move = move
        
        return best_move if best_move else valid_moves[0]
    
    @staticmethod
    def corner_move(game, valid_moves, player):
        if not valid_moves:
            return None
        
        corners = [(0, 0), (0, 5), (5, 0), (5, 5)]
        edges = []
        for i in range(6):
            for j in range(6):
                if i == 0 or i == 5 or j == 0 or j == 5:
                    if (i, j) not in corners:
                        edges.append((i, j))
        
        for move in valid_moves:
            if move in corners:
                return move
        
        for move in valid_moves:
            if move in edges:
                return move
        
        return AIStrategy.greedy_move(game, valid_moves, player)
    
    @staticmethod
    def control_move(game, valid_moves, player):
        if not valid_moves:
            return None
        
        best_move = None
        best_score = -float('inf')
        opponent = 'white' if player == 'black' else 'black'
        
        for move in valid_moves:
            score = 0
            score += POSITION_WEIGHTS[move[0]][move[1]]
            
            temp_game = ReversiGame()
            temp_game.board = game.get_board_copy()
            if temp_game.make_move(move[0], move[1], player):
                current_count = game.black_score if player == 'black' else game.white_score
                new_count = temp_game.black_score if player == 'black' else temp_game.white_score
                flipped = new_count - current_count
                score += flipped * 3
            
            temp_game = ReversiGame()
            temp_game.board = game.get_board_copy()
            temp_game.make_move(move[0], move[1], player)
            opponent_moves = len(temp_game.get_valid_moves(opponent))
            score -= opponent_moves * MOBILITY_WEIGHT
            
            corners = [(0, 0), (0, 5), (5, 0), (5, 5)]
            for corner in corners:
                dist = abs(move[0] - corner[0]) + abs(move[1] - corner[1])
                if dist <= 2:
                    score += (3 - dist) * 4
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else valid_moves[0]
    
    @staticmethod
    def look_ahead_move(game, valid_moves, player, depth=1):
        if not valid_moves:
            return None
        
        best_move = None
        best_score = -float('inf')
        
        for move in valid_moves:
            temp_game = ReversiGame()
            temp_game.board = game.get_board_copy()
            temp_game.make_move(move[0], move[1], player)
            score = AIStrategy._evaluate_board(temp_game.board, player)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else valid_moves[0]
    
    @staticmethod
    def _evaluate_board(board, player):
        opponent = 'white' if player == 'black' else 'black'
        score = 0
        for i in range(6):
            for j in range(6):
                if board[i][j] == player:
                    score += POSITION_WEIGHTS[i][j]
                elif board[i][j] == opponent:
                    score -= POSITION_WEIGHTS[i][j]
        return score
class AIState(Enum):
    AGGRESSIVE = "АГРЕССИВНАЯ (Жадная)"
    DEFENSIVE = "ЗАЩИТНАЯ (Угловая)"
    BALANCED = "СБАЛАНСИРОВАННАЯ (Контрольная)"
    ADAPTIVE = "АДАПТИВНАЯ"


class AIAutomaton:
    def __init__(self):
        self.state = AIState.BALANCED
        self.player_move_history = deque(maxlen=5)
        self.state_history = deque(maxlen=10)
        self.consecutive_same_type = 0
        self.last_move_type = None
        
    def _get_move_type(self, move):
        if not move:
            return None
        corners = [(0, 0), (0, 5), (5, 0), (5, 5)]
        edges = []
        for i in range(6):
            for j in range(6):
                if (i == 0 or i == 5 or j == 0 or j == 5) and (i, j) not in corners:
                    edges.append((i, j))
        
        if move in corners:
            return 'corner'
        elif move in edges:
            return 'edge'
        else:
            return 'center'
    
    def _is_repeating_pattern(self):
        if len(self.player_move_history) < 3:
            return False
        types = [t for t in self.player_move_history if t is not None]
        if len(types) < 3:
            return False
        return len(set(types)) == 1
    
    def _is_corner_captured(self, game, move):
        corners = [(0, 0), (0, 5), (5, 0), (5, 5)]
        if move and move in corners:
            return game.board[move[0]][move[1]] == 'black'
        return False
    
    def _get_winning_rate(self, game):
        total = game.black_score + game.white_score
        if total == 0:
            return 0.5
        return game.white_score / total
    
    def update_state(self, game, player_last_move):
        move_type = self._get_move_type(player_last_move)
        if move_type:
            self.player_move_history.append(move_type)
        
        winning_rate = self._get_winning_rate(game)
        old_state = self.state
        
        if self._is_repeating_pattern():
            self.state = AIState.ADAPTIVE
            self.consecutive_same_type += 1
        else:
            self.consecutive_same_type = 0
        
        if self._is_corner_captured(game, player_last_move):
            self.state = AIState.DEFENSIVE
        elif winning_rate < 0.4:
            self.state = AIState.AGGRESSIVE
        elif winning_rate > 0.6:
            self.state = AIState.BALANCED
        elif move_type == 'corner' and self.state != AIState.DEFENSIVE:
            self.state = AIState.DEFENSIVE
        elif self.state == AIState.AGGRESSIVE and winning_rate > 0.55:
            self.state = AIState.BALANCED
        elif self.state == AIState.DEFENSIVE and winning_rate < 0.45:
            self.state = AIState.AGGRESSIVE
        
        if old_state != self.state:
            self.state_history.append((old_state, self.state))
    
    def choose_move(self, game, valid_moves):
        if not valid_moves:
            return None
        
        if random.random() < 0.1:
            return random.choice(valid_moves)
        
        if self.state == AIState.AGGRESSIVE:
            move = AIStrategy.greedy_move(game, valid_moves, 'white')
        elif self.state == AIState.DEFENSIVE:
            move = AIStrategy.corner_move(game, valid_moves, 'white')
        elif self.state == AIState.BALANCED:
            move = AIStrategy.control_move(game, valid_moves, 'white')
        else:
            move = self._adaptive_choice(game, valid_moves)
        
        if self.state == AIState.ADAPTIVE and random.random() < 0.5:
            look_ahead_move = AIStrategy.look_ahead_move(game, valid_moves, 'white', depth=1)
            if look_ahead_move:
                move = look_ahead_move
        
        return move if move else valid_moves[0]
    
    def _adaptive_choice(self, game, valid_moves):
        if not self.player_move_history:
            return AIStrategy.control_move(game, valid_moves, 'white')
        
        corner_count = self.player_move_history.count('corner')
        edge_count = self.player_move_history.count('edge')
        
        if corner_count >= 2:
            return AIStrategy.control_move(game, valid_moves, 'white')
        elif edge_count >= 3:
            return AIStrategy.corner_move(game, valid_moves, 'white')
        else:
            return AIStrategy.greedy_move(game, valid_moves, 'white')
    
    def get_state_name(self):
        return self.state.value
    
    def reset(self):
        self.state = AIState.BALANCED
        self.player_move_history.clear()
        self.state_history.clear()
        self.consecutive_same_type = 0
        self.last_move_type = None
class ReversiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Реверси (Отелло) 6x6 - ИИ с конечным автоматом")
        self.root.geometry("700x680")
        self.root.configure(bg="#2b2b2b")
        
        self.game = ReversiGame()
        self.ai_automaton = AIAutomaton()
        self.cell_size = 80
        self.board_offset_x = 50
        self.board_offset_y = 80
        
        self.create_widgets()
        self.draw_board()
        self.update_status()
        
        if self.game.current_player == 'white':
            self.root.after(500, self.ai_move)
    
    def create_widgets(self):
        bg_color = "#2b2b2b"
        fg_color = "#00ff00"
        font_main = ("Arial", 12)
        font_title = ("Arial", 14, "bold")
        
        title_label = tk.Label(self.root, text="РЕВЕРСИ (ОТЕЛЛО) 6x6", 
                                font=("Arial", 18, "bold"), 
                                bg=bg_color, fg="#ffaa00")
        title_label.pack(pady=10)
        
        info_frame = tk.Frame(self.root, bg=bg_color)
        info_frame.pack(pady=5)
        
        self.score_label = tk.Label(info_frame, text="Чёрные (Вы): 2  |  Белые (ИИ): 2",
                                     font=font_title, bg=bg_color, fg=fg_color)
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        self.turn_label = tk.Label(info_frame, text="Ваш ход", 
                                    font=font_title, bg=bg_color, fg="#ffaa00")
        self.turn_label.pack(side=tk.LEFT, padx=20)
        
        strategy_frame = tk.Frame(self.root, bg=bg_color)
        strategy_frame.pack(pady=5)
        
        tk.Label(strategy_frame, text="Стратегия ИИ:", 
                 font=font_main, bg=bg_color, fg=fg_color).pack(side=tk.LEFT)
        
        self.strategy_label = tk.Label(strategy_frame, text="СБАЛАНСИРОВАННАЯ", 
                                        font=("Arial", 12, "bold"), 
                                        bg=bg_color, fg="#ffaa00")
        self.strategy_label.pack(side=tk.LEFT, padx=10)
        
        button_frame = tk.Frame(self.root, bg=bg_color)
        button_frame.pack(pady=10)
        
        self.new_game_btn = tk.Button(button_frame, text="Новая игра", 
                                       command=self.new_game,
                                       font=font_main, bg="#555555", fg="white",
                                       padx=20, pady=5)
        self.new_game_btn.pack(side=tk.LEFT, padx=10)
        
        self.reset_btn = tk.Button(button_frame, text="Сбросить автомат", 
                                    command=self.reset_automaton,
                                    font=font_main, bg="#555555", fg="white",
                                    padx=20, pady=5)
        self.reset_btn.pack(side=tk.LEFT, padx=10)
        
        self.status_var = tk.StringVar(value="Игра начата. Ваш ход (чёрные).")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                               bd=1, relief=tk.SUNKEN, anchor=tk.W,
                               font=font_main, bg=bg_color, fg=fg_color)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        canvas_size = self.cell_size * self.game.size + 20
        self.canvas = tk.Canvas(self.root, width=canvas_size + 100, 
                                 height=canvas_size + 50,
                                 bg="#1e1e1e")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)
    
    def draw_board(self):
        self.canvas.delete("all")
        
        for i in range(self.game.size + 1):
            self.canvas.create_line(self.board_offset_x + i * self.cell_size,
                                    self.board_offset_y,
                                    self.board_offset_x + i * self.cell_size,
                                    self.board_offset_y + self.game.size * self.cell_size,
                                    fill="#888888", width=2)
            self.canvas.create_line(self.board_offset_x,
                                    self.board_offset_y + i * self.cell_size,
                                    self.board_offset_x + self.game.size * self.cell_size,
                                    self.board_offset_y + i * self.cell_size,
                                    fill="#888888", width=2)
        
        for i in range(self.game.size):
            for j in range(self.game.size):
                x = self.board_offset_x + j * self.cell_size + self.cell_size // 2
                y = self.board_offset_y + i * self.cell_size + self.cell_size // 2
                r = self.cell_size // 2 - 5
                
                if self.game.board[i][j] == 'black':
                    self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#333333", outline="#ffffff", width=2)
                elif self.game.board[i][j] == 'white':
                    self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#ffffff", outline="#333333", width=2)
        
        if self.game.current_player == 'black':
            valid_moves = self.game.get_valid_moves('black')
            for move in valid_moves:
                x = self.board_offset_x + move[1] * self.cell_size + self.cell_size // 2
                y = self.board_offset_y + move[0] * self.cell_size + self.cell_size // 2
                r = self.cell_size // 2 - 15
                self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="#00ff00", width=3, tags="valid_move")
    
    def on_click(self, event):
        if self.game.current_player != 'black':
            self.status_var.set("Сейчас не ваш ход! Подождите.")
            return
        
        col = (event.x - self.board_offset_x) // self.cell_size
        row = (event.y - self.board_offset_y) // self.cell_size
        
        if 0 <= row < self.game.size and 0 <= col < self.game.size:
            if self.game.make_move(row, col, 'black'):
                self.draw_board()
                self.update_status()
                
                if self.game.is_game_over():
                    self.end_game()
                    return
                
                self.game.current_player = 'white'
                self.update_status()
                self.root.after(500, self.ai_move)
            else:
                self.status_var.set("Недопустимый ход! Нажмите на зелёный кружок.")
    
    def ai_move(self):
        if self.game.current_player != 'white':
            return
        
        if self.game.is_game_over():
            self.end_game()
            return
        
        valid_moves = self.game.get_valid_moves('white')
        
        if not valid_moves:
            if not self.game.has_valid_move('black'):
                self.end_game()
                return
            else:
                self.status_var.set("У ИИ нет ходов. Ваш ход.")
                self.game.current_player = 'black'
                self.update_status()
                self.draw_board()
                return
        
        self.ai_automaton.update_state(self.game, None)
        self.strategy_label.config(text=self.ai_automaton.get_state_name())
        
        move = self.ai_automaton.choose_move(self.game, valid_moves)
        
        if move:
            self.game.make_move(move[0], move[1], 'white')
            self.status_var.set(f"ИИ сходил на позицию ({move[0]}, {move[1]})")
        
        self.draw_board()
        self.update_status()
        
        if self.game.is_game_over():
            self.end_game()
            return
        
        if self.game.has_valid_move('black'):
            self.game.current_player = 'black'
            self.update_status()
        else:
            self.status_var.set("У вас нет ходов. Ход ИИ.")
            self.root.after(500, self.ai_move)
    
    def update_status(self):
        self.score_label.config(text=f"Чёрные (Вы): {self.game.black_score}  |  Белые (ИИ): {self.game.white_score}")
        
        if self.game.current_player == 'black':
            if self.game.has_valid_move('black'):
                self.turn_label.config(text="Ваш ход", fg="#00ff00")
                self.status_var.set("Ваш ход. Нажмите на зелёный кружок.")
            else:
                self.turn_label.config(text="У вас нет ходов", fg="#ff6600")
                self.status_var.set("У вас нет допустимых ходов. Ход переходит ИИ.")
        else:
            self.turn_label.config(text="Ход ИИ", fg="#ffaa00")
            self.status_var.set("ИИ думает...")
        
        self.strategy_label.config(text=self.ai_automaton.get_state_name())
    
    def end_game(self):
        winner = self.game.get_winner()
        if winner == 'black':
            messagebox.showinfo("Игра окончена", f"Поздравляем! Вы победили!\nСчёт: {self.game.black_score} : {self.game.white_score}")
        elif winner == 'white':
            messagebox.showinfo("Игра окончена", f"ИИ победил!\nСчёт: {self.game.black_score} : {self.game.white_score}")
        else:
            messagebox.showinfo("Игра окончена", f"Ничья!\nСчёт: {self.game.black_score} : {self.game.white_score}")
        
        self.turn_label.config(text="Игра окончена", fg="#ff0000")
  
    def new_game(self):
        self.game = ReversiGame()
        self.ai_automaton.reset()
        self.draw_board()
        self.update_status()
        self.strategy_label.config(text=self.ai_automaton.get_state_name())
        self.status_var.set("Начата новая игра. Ваш ход (чёрные).")
        
        if self.game.current_player == 'white':
            self.root.after(500, self.ai_move)
    
    def reset_automaton(self):
        self.ai_automaton.reset()
        self.strategy_label.config(text=self.ai_automaton.get_state_name())
        self.status_var.set("Автомат сброшен в сбалансированное состояние.")
if __name__ == "__main__":
    root = tk.Tk()
    app = ReversiGUI(root)
    root.mainloop()