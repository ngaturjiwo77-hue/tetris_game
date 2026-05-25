import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
import random

# Konfigurasi game
COLS = 10
ROWS = 20
CELL_SIZE = 30

# Bentuk tetromino
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

COLORS = [
    (0, 1, 1, 1),      # Cyan
    (1, 1, 0, 1),      # Yellow
    (0.5, 0, 0.5, 1),  # Purple
    (1, 0.5, 0, 1),    # Orange
    (0, 0, 1, 1),      # Blue
    (0, 1, 0, 1),      # Green
    (1, 0, 0, 1)       # Red
]

class TetrisGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.paused = False
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.speed = 1.0
        
        # Inisialisasi board
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = None
        self.current_color = None
        self.current_x = 0
        self.current_y = 0
        
        # Header info
        self.info_layout = BoxLayout(size_hint=(1, 0.1))
        self.score_label = Label(text='Score: 0', bold=True, font_size=20)
        self.level_label = Label(text='Level: 1', bold=True, font_size=20)
        self.info_layout.add_widget(self.score_label)
        self.info_layout.add_widget(self.level_label)
        self.add_widget(self.info_layout)
        
        # Area game
        self.game_layout = FloatLayout(size_hint=(1, 0.8))
        self.game_canvas = GameCanvas()
        self.game_layout.add_widget(self.game_canvas)
        self.add_widget(self.game_layout)
        
        # Tombol kontrol
        self.control_layout = BoxLayout(size_hint=(1, 0.1), spacing=5, padding=5)
        
        self.btn_left = Button(text='⬅', font_size=20, on_press=self.move_left)
        self.btn_right = Button(text='➡', font_size=20, on_press=self.move_right)
        self.btn_rotate = Button(text='🔄', font_size=20, on_press=self.rotate_piece)
        self.btn_down = Button(text='⬇', font_size=20, on_press=self.move_down)
        self.btn_pause = Button(text='⏸', font_size=20, on_press=self.toggle_pause)
        
        self.control_layout.add_widget(self.btn_left)
        self.control_layout.add_widget(self.btn_rotate)
        self.control_layout.add_widget(self.btn_down)
        self.control_layout.add_widget(self.btn_right)
        self.control_layout.add_widget(self.btn_pause)
        
        self.add_widget(self.control_layout)
        
        # Keyboard binding
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        # Mulai game
        self.spawn_piece()
        Clock.schedule_interval(self.update, 1.0/60.0)
        self.fall_time = 0
    
    def _keyboard_closed(self):
        pass
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.game_over or self.paused:
            return True
        
        if keycode[1] == 'left':
            self.move_left()
        elif keycode[1] == 'right':
            self.move_right()
        elif keycode[1] == 'down':
            self.move_down()
        elif keycode[1] == 'up':
            self.rotate_piece()
        elif keycode[1] == 'spacebar':
            self.hard_drop()
        elif keycode[1] == 'p':
            self.toggle_pause()
        
        return True
    
    def spawn_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        self.current_piece = [row[:] for row in SHAPES[shape_idx]]
        self.current_color = COLORS[shape_idx]
        self.current_x = COLS // 2 - len(self.current_piece[0]) // 2
        self.current_y = ROWS - len(self.current_piece)
        
        if not self.is_valid_position(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
            self.show_game_over()
    
    def is_valid_position(self, piece, x, y):
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = x + col_idx
                    board_y = y + row_idx
                    if (board_x < 0 or board_x >= COLS or 
                        board_y < 0 or board_y >= ROWS or 
                        (board_y >= 0 and self.board[board_y][board_x])):
                        return False
        return True
    
    def lock_piece(self):
        for row_idx, row in enumerate(self.current_piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = self.current_x + col_idx
                    board_y = self.current_y + row_idx
                    if 0 <= board_y < ROWS:
                        self.board[board_y][board_x] = self.current_color
        
        self.clear_lines()
        self.spawn_piece()
    
    def clear_lines(self):
        lines_cleared = 0
        y = ROWS - 1
        while y >= 0:
            if all(self.board[y]):
                del self.board[y]
                self.board.insert(0, [0 for _ in range(COLS)])
                lines_cleared += 1
            else:
                y -= 1
        
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            points = [0, 100, 300, 500, 800]
            self.score += points[lines_cleared] * self.level
            self.level = (self.lines_cleared // 10) + 1
            self.speed = max(0.1, 1.0 - (self.level - 1) * 0.1)
            self.update_info()
    
    def move_left(self, *args):
        if not self.game_over and not self.paused:
            if self.is_valid_position(self.current_piece, self.current_x - 1, self.current_y):
                self.current_x -= 1
    
    def move_right(self, *args):
        if not self.game_over and not self.paused:
            if self.is_valid_position(self.current_piece, self.current_x + 1, self.current_y):
                self.current_x += 1
    
    def move_down(self, *args):
        if not self.game_over and not self.paused:
            if self.is_valid_position(self.current_piece, self.current_x, self.current_y - 1):
                self.current_y -= 1
            else:
                self.lock_piece()
    
    def rotate_piece(self, *args):
        if not self.game_over and not self.paused:
            rotated = list(zip(*self.current_piece[::-1]))
            rotated = [list(row) for row in rotated]
            if self.is_valid_position(rotated, self.current_x, self.current_y):
                self.current_piece = rotated
    
    def hard_drop(self):
        if not self.game_over and not self.paused:
            while self.is_valid_position(self.current_piece, self.current_x, self.current_y - 1):
                self.current_y -= 1
            self.lock_piece()
    
    def toggle_pause(self, *args):
        if not self.game_over:
            self.paused = not self.paused
            if self.paused:
                self.btn_pause.text = '▶'
            else:
                self.btn_pause.text = '⏸'
    
    def update_info(self):
        self.score_label.text = f'Score: {self.score}'
        self.level_label.text = f'Level: {self.level}'
    
    def update(self, dt):
        if not self.game_over and not self.paused:
            self.fall_time += dt
            if self.fall_time >= self.speed:
                self.fall_time = 0
                if self.is_valid_position(self.current_piece, self.current_x, self.current_y - 1):
                    self.current_y -= 1
                else:
                    self.lock_piece()
            
            self.game_canvas.draw_board(self.board, self.current_piece, 
                                       self.current_x, self.current_y, self.current_color)
    
    def show_game_over(self):
        popup = Popup(title='Game Over',
                     content=Label(text=f'Score: {self.score}\nTap to restart'),
                     size_hint=(0.6, 0.4),
                     auto_dismiss=False)
        popup.bind(on_dismiss=self.restart_game)
        popup.open()
    
    def restart_game(self, *args):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.speed = 1.0
        self.game_over = False
        self.paused = False
        self.btn_pause.text = '⏸'
        self.update_info()
        self.spawn_piece()

class GameCanvas(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
    
    def draw_board(self, board, current_piece, current_x, current_y, current_color):
        self.canvas.clear()
        
        with self.canvas:
            # Background
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Grid
            cell_w = self.width / COLS
            cell_h = self.height / ROWS
            actual_cell = min(cell_w, cell_h)
            
            # Gambar board
            for y in range(ROWS):
                for x in range(COLS):
                    if board[y][x]:
                        Color(*board[y][x])
                        Rectangle(
                            pos=(self.x + x * actual_cell, 
                                 self.y + y * actual_cell),
                            size=(actual_cell - 1, actual_cell - 1)
                        )
            
            # Gambar current piece
            if current_piece:
                Color(*current_color)
                for row_idx, row in enumerate(current_piece):
                    for col_idx, cell in enumerate(row):
                        if cell:
                            board_x = current_x + col_idx
                            board_y = current_y + row_idx
                            if board_y >= 0:
                                Rectangle(
                                    pos=(self.x + board_x * actual_cell,
                                         self.y + board_y * actual_cell),
                                    size=(actual_cell - 1, actual_cell - 1)
                                )
            
            # Grid lines
            Color(0.3, 0.3, 0.3, 0.5)
            for x in range(COLS + 1):
                Rectangle(
                    pos=(self.x + x * actual_cell, self.y),
                    size=(1, self.height)
                )
            for y in range(ROWS + 1):
                Rectangle(
                    pos=(self.x, self.y + y * actual_cell),
                    size=(self.width, 1)
                )
    
    def update_canvas(self, *args):
        pass

class TetrisApp(App):
    def build(self):
        self.title = 'Tetris Game'
        return TetrisGame()

if __name__ == '__main__':
    TetrisApp().run()
