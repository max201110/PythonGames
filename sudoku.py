import tkinter as tk
from tkinter import messagebox
import numpy as np
import random
import time

class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("数独游戏")
        self.root.resizable(False, False)
        
        # 创建游戏数据
        self.board = np.zeros((9, 9), dtype=int)
        self.solution = None
        self.fixed_cells = set()
        
        # 计时器相关变量
        self.timer_running = False
        self.start_time = 0
        self.elapsed_time = 0
        
        # 创建界面
        self.create_widgets()
        
        # 开始新游戏
        self.new_game()

    def create_widgets(self):
        # 创建顶部按钮框架
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        
        # 难度选择
        self.difficulty_var = tk.StringVar(value="medium")
        difficulties = [
            ("简单", "easy"),
            ("中等", "medium"),
            ("困难", "hard")
        ]
        for text, value in difficulties:
            tk.Radiobutton(top_frame, text=text, value=value,
                          variable=self.difficulty_var).pack(side=tk.LEFT, padx=5)
        
        # 新游戏按钮
        tk.Button(top_frame, text="新游戏", command=self.new_game).pack(side=tk.LEFT, padx=5)
        
        # 开始/暂停按钮
        self.start_button = tk.Button(top_frame, text="开始", command=self.toggle_timer)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 计时器标签
        self.timer_label = tk.Label(top_frame, text="时间: 00:00", font=('Arial', 12))
        self.timer_label.pack(side=tk.LEFT, padx=5)
        
        # 检查答案按钮
        tk.Button(top_frame, text="检查答案", command=self.check_solution).pack(side=tk.LEFT, padx=5)
        
        # 提示按钮
        tk.Button(top_frame, text="提示", command=self.get_hint).pack(side=tk.LEFT, padx=5)
        
        # 创建数独格子
        self.cells = {}
        cell_frame = tk.Frame(self.root)
        cell_frame.pack(padx=10, pady=10)
        
        for i in range(9):
            for j in range(9):
                cell = tk.Entry(cell_frame, width=2, font=('Arial', 20),
                              justify='center')
                cell.grid(row=i, column=j, padx=1, pady=1)
                
                # 添加3x3方格的边框
                if i % 3 == 0 and i != 0:
                    cell.grid(pady=(10, 1))
                if j % 3 == 0 and j != 0:
                    cell.grid(padx=(10, 1))
                
                # 绑定验证函数
                cell.bind('<KeyRelease>', lambda e, row=i, col=j: self.validate_input(e, row, col))
                self.cells[(i, j)] = cell

    def toggle_timer(self):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.start_button.config(text="暂停")
            self.update_timer()
        else:
            self.timer_running = False
            self.start_button.config(text="继续")
            self.elapsed_time = time.time() - self.start_time

    def update_timer(self):
        if self.timer_running:
            current_time = time.time() - self.start_time
            minutes = int(current_time // 60)
            seconds = int(current_time % 60)
            self.timer_label.config(text=f"时间: {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)

    def validate_input(self, event, row, col):
        if (row, col) in self.fixed_cells:
            return
        
        cell = self.cells[(row, col)]
        value = cell.get()
        
        # 只允许输入1-9的数字
        if value and (not value.isdigit() or int(value) not in range(1, 10)):
            cell.delete(0, tk.END)
            return
        
        # 更新游戏数据
        self.board[row][col] = int(value) if value else 0

    def is_valid(self, board, row, col, num):
        # 检查行
        for x in range(9):
            if board[row][x] == num:
                return False
        
        # 检查列
        for x in range(9):
            if board[x][col] == num:
                return False
        
        # 检查3x3方格
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        
        return True

    def solve_sudoku(self, board):
        empty = self.find_empty(board)
        if not empty:
            return True
        
        row, col = empty
        for num in range(1, 10):
            if self.is_valid(board, row, col, num):
                board[row][col] = num
                if self.solve_sudoku(board):
                    return True
                board[row][col] = 0
        
        return False

    def find_empty(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None

    def generate_sudoku(self, difficulty):
        # 创建空棋盘
        board = np.zeros((9, 9), dtype=int)
        
        # 填充对角线方格
        for i in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for row in range(3):
                for col in range(3):
                    board[row + i][col + i] = nums.pop()
        
        # 解决剩余部分
        self.solve_sudoku(board)
        
        # 根据难度移除数字
        cells_to_remove = {
            'easy': 30,
            'medium': 40,
            'hard': 50
        }.get(difficulty, 40)
        
        solution = board.copy()
        while cells_to_remove > 0:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if board[row][col] != 0:
                board[row][col] = 0
                cells_to_remove -= 1
        
        return board, solution

    def new_game(self):
        # 重置计时器
        self.timer_running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.timer_label.config(text="时间: 00:00")
        self.start_button.config(text="开始")
        
        # 清空所有格子
        for i in range(9):
            for j in range(9):
                cell = self.cells[(i, j)]
                cell.config(state='normal')  # 先设置为可编辑状态
                cell.delete(0, tk.END)       # 清空内容
                cell.config(bg='white')      # 重置背景色
        
        # 生成新的数独
        self.board, self.solution = self.generate_sudoku(self.difficulty_var.get())
        self.fixed_cells.clear()
        
        # 更新界面
        for i in range(9):
            for j in range(9):
                cell = self.cells[(i, j)]
                if self.board[i][j] != 0:
                    cell.insert(0, str(self.board[i][j]))
                    cell.config(state='readonly', bg='#f0f0f0')  # 固定数字使用灰色背景
                    self.fixed_cells.add((i, j))
                else:
                    cell.config(state='normal', bg='white')  # 空白格子使用白色背景

    def check_solution(self):
        if not self.timer_running:
            messagebox.showinfo("提示", "请先点击开始按钮！")
            return
            
        # 检查是否完成
        if 0 in self.board:
            messagebox.showinfo("提示", "请完成所有空格！")
            return
        
        # 检查答案是否正确
        if np.array_equal(self.board, self.solution):
            self.timer_running = False
            self.start_button.config(text="开始")
            current_time = time.time() - self.start_time
            minutes = int(current_time // 60)
            seconds = int(current_time % 60)
            messagebox.showinfo("恭喜", f"答案正确！\n用时：{minutes:02d}:{seconds:02d}")
        else:
            messagebox.showinfo("提示", "答案不正确，请继续尝试！")

    def get_hint(self):
        if not self.timer_running:
            messagebox.showinfo("提示", "请先点击开始按钮！")
            return
            
        # 找到第一个空位并显示答案
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    cell = self.cells[(i, j)]
                    cell.delete(0, tk.END)
                    cell.insert(0, str(self.solution[i][j]))
                    self.board[i][j] = self.solution[i][j]
                    return

if __name__ == "__main__":
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop() 