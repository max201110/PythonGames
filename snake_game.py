import tkinter as tk
from tkinter import messagebox
import json
import os
import random

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("贪吃蛇游戏")
        
        # 游戏常量
        self.GRID_SIZE = 20
        self.GRID_COUNT = 20
        self.CANVAS_SIZE = self.GRID_SIZE * self.GRID_COUNT
        
        # 游戏状态
        self.snake = []
        self.food = None
        self.direction = 'right'
        self.next_direction = 'right'
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_speed = 150
        self.is_running = False
        
        # 创建界面
        self.create_widgets()
        
        # 绑定键盘事件
        self.root.bind('<Key>', self.handle_keypress)
        
    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=10)
        
        # 创建画布
        self.canvas = tk.Canvas(main_frame, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE, bg='#f0f0f0')
        self.canvas.pack(pady=10)
        
        # 创建信息框架
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill='x', pady=5)
        
        # 分数显示
        self.score_label = tk.Label(info_frame, text=f"当前分数: 0")
        self.score_label.pack(side='left', padx=5)
        
        self.high_score_label = tk.Label(info_frame, text=f"最高分数: {self.high_score}")
        self.high_score_label.pack(side='left', padx=5)
        
        # 开始按钮
        self.start_button = tk.Button(main_frame, text="开始游戏", command=self.start_game)
        self.start_button.pack(pady=5)
        
        # 控制说明
        controls_label = tk.Label(main_frame, text="使用方向键或 WASD 控制蛇的移动")
        controls_label.pack(pady=5)
    
    def load_high_score(self):
        if os.path.exists('high_scores.json'):
            with open('high_scores.json', 'r') as f:
                return json.load(f)['high_score']
        return 0
    
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open('high_scores.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
            self.high_score_label.config(text=f"最高分数: {self.high_score}")
    
    def init_game(self):
        self.snake = [
            {'x': 5, 'y': 5},
            {'x': 4, 'y': 5},
            {'x': 3, 'y': 5}
        ]
        self.generate_food()
        self.direction = 'right'
        self.next_direction = 'right'
        self.score = 0
        self.score_label.config(text=f"当前分数: {self.score}")
        self.game_speed = 150
    
    def generate_food(self):
        while True:
            self.food = {
                'x': random.randint(0, self.GRID_COUNT - 1),
                'y': random.randint(0, self.GRID_COUNT - 1)
            }
            if not any(segment['x'] == self.food['x'] and segment['y'] == self.food['y'] for segment in self.snake):
                break
    
    def draw(self):
        self.canvas.delete('all')
        
        # 绘制蛇
        for i, segment in enumerate(self.snake):
            color = '#2ecc71' if i == 0 else '#27ae60'
            x = segment['x'] * self.GRID_SIZE
            y = segment['y'] * self.GRID_SIZE
            self.canvas.create_rectangle(x, y, x + self.GRID_SIZE - 1, y + self.GRID_SIZE - 1, fill=color)
        
        # 绘制食物
        x = self.food['x'] * self.GRID_SIZE
        y = self.food['y'] * self.GRID_SIZE
        self.canvas.create_rectangle(x, y, x + self.GRID_SIZE - 1, y + self.GRID_SIZE - 1, fill='#e74c3c')
    
    def move_snake(self):
        self.direction = self.next_direction
        head = {'x': self.snake[0]['x'], 'y': self.snake[0]['y']}
        
        if self.direction == 'up':
            head['y'] -= 1
        elif self.direction == 'down':
            head['y'] += 1
        elif self.direction == 'left':
            head['x'] -= 1
        elif self.direction == 'right':
            head['x'] += 1
        
        # 检查是否撞墙
        if (head['x'] < 0 or head['x'] >= self.GRID_COUNT or
            head['y'] < 0 or head['y'] >= self.GRID_COUNT):
            self.game_over()
            return
        
        # 检查是否撞到自己
        if any(segment['x'] == head['x'] and segment['y'] == head['y'] for segment in self.snake):
            self.game_over()
            return
        
        self.snake.insert(0, head)
        
        # 检查是否吃到食物
        if head['x'] == self.food['x'] and head['y'] == self.food['y']:
            self.score += 10
            self.score_label.config(text=f"当前分数: {self.score}")
            self.generate_food()
            # 加快游戏速度
            if self.game_speed > 50:
                self.game_speed -= 5
                self.root.after_cancel(self.game_loop)
                self.game_loop = self.root.after(self.game_speed, self.game_step)
        else:
            self.snake.pop()
    
    def game_step(self):
        if self.is_running:
            self.move_snake()
            self.draw()
            self.game_loop = self.root.after(self.game_speed, self.game_step)
    
    def game_over(self):
        self.is_running = False
        self.start_button.config(text="重新开始", state='normal')
        self.save_high_score()
        messagebox.showinfo("游戏结束", f"游戏结束！\n你的得分是: {self.score}")
    
    def start_game(self):
        if not self.is_running:
            self.init_game()
            self.is_running = True
            self.start_button.config(text="游戏进行中", state='disabled')
            self.game_loop = self.root.after(self.game_speed, self.game_step)
    
    def handle_keypress(self, event):
        if not self.is_running:
            return
        
        key = event.keysym.lower()
        if key in ['up', 'w'] and self.direction != 'down':
            self.next_direction = 'up'
        elif key in ['down', 's'] and self.direction != 'up':
            self.next_direction = 'down'
        elif key in ['left', 'a'] and self.direction != 'right':
            self.next_direction = 'left'
        elif key in ['right', 'd'] and self.direction != 'left':
            self.next_direction = 'right'

if __name__ == '__main__':
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop() 