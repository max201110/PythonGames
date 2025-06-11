import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import math
from enum import Enum
from PIL import Image, ImageTk, ImageColor

class TowerType(Enum):
    ARROW = 1    # 箭塔：基础攻击，中等攻速
    CANNON = 2   # 炮塔：范围攻击，慢攻速
    MAGIC = 3    # 魔法塔：减速效果，快攻速
    LASER = 4    # 激光塔：穿透攻击，中等攻速
    ICE = 5      # 冰塔：冻结效果，慢攻速
    POISON = 6   # 毒塔：持续伤害，中等攻速
    SNIPER = 7   # 狙击塔：超高伤害，极慢攻速
    SUPPORT = 8  # 支援塔：提升周围塔的攻击力

class EnemyType(Enum):
    NORMAL = 1   # 普通敌人：中等生命，中等速度
    FAST = 2     # 快速敌人：低生命，高速度
    TANK = 3     # 坦克敌人：高生命，低速度
    BOSS = 4     # Boss敌人：超高生命，中等速度
    FLYING = 5   # 飞行敌人：中等生命，高速度，无视地形
    STEALTH = 6  # 隐身敌人：低生命，高速度，周期性隐身
    HEALER = 7   # 治疗敌人：低生命，低速度，治疗其他敌人
    SWARM = 8    # 集群敌人：极低生命，极高速度，成群出现

class Tower:
    def __init__(self, tower_type, x, y):
        self.type = tower_type
        self.x = x
        self.y = y
        self.level = 1
        self.target = None
        self.cooldown = 0
        self.experience = 0
        self.max_experience = 100
        self.attack_trajectory = []  # 存储攻击轨迹点
        
        # 设置塔的属性
        if tower_type == TowerType.ARROW:
            self.damage = 30
            self.attack_speed = 20  # 调整攻击速度以适应新的更新频率
            self.range = 3
            self.cost = 100
            self.color = '#3498db'
            self.special = None
            self.description = "基础箭塔"
        elif tower_type == TowerType.CANNON:
            self.damage = 75
            self.attack_speed = 30  # 调整攻击速度以适应新的更新频率
            self.range = 2
            self.cost = 200
            self.color = '#e74c3c'
            self.special = "splash"
            self.description = "范围炮塔"
        elif tower_type == TowerType.MAGIC:
            self.damage = 25
            self.attack_speed = 15  # 调整攻击速度以适应新的更新频率
            self.range = 3
            self.cost = 150
            self.color = '#9b59b6'
            self.special = "slow"
            self.description = "减速魔法塔"
        elif tower_type == TowerType.LASER:
            self.damage = 45
            self.attack_speed = 25  # 调整攻击速度以适应新的更新频率
            self.range = 4
            self.cost = 250
            self.color = '#f1c40f'
            self.special = "pierce"
            self.description = "穿透激光塔"
        elif tower_type == TowerType.ICE:
            self.damage = 15
            self.attack_speed = 27  # 调整攻击速度以适应新的更新频率
            self.range = 3
            self.cost = 175
            self.color = '#00bfff'
            self.special = "freeze"
            self.description = "冰冻塔"
        elif tower_type == TowerType.POISON:
            self.damage = 8
            self.attack_speed = 20  # 调整攻击速度以适应新的更新频率
            self.range = 3
            self.cost = 225
            self.color = '#32cd32'
            self.special = "poison"
            self.description = "毒塔"
        elif tower_type == TowerType.SNIPER:
            self.damage = 300
            self.attack_speed = 40  # 调整攻击速度以适应新的更新频率
            self.range = 5
            self.cost = 300
            self.color = '#8b4513'
            self.special = "critical"
            self.description = "狙击塔"
        else:  # SUPPORT
            self.damage = 0
            self.attack_speed = 0
            self.range = 2
            self.cost = 275
            self.color = '#ffd700'
            self.special = "buff"
            self.description = "支援塔"

    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.damage *= 1.5
            self.range *= 1.2
            self.attack_speed = int(self.attack_speed * 0.9)
            return True
        return False

    def get_stats_text(self):
        return f"攻击力: {self.damage}\n攻速: {self.attack_speed}\n范围: {self.range}"

class Enemy:
    def __init__(self, enemy_type, path, wave_number):
        self.type = enemy_type
        self.path = path
        self.path_index = 0
        self.x = path[0][0]
        self.y = path[0][1]
        self.speed = 0
        self.max_health = 0
        self.health = 0
        self.reward = 0
        self.stealth = False
        self.frozen = False
        self.poisoned = False
        self.poison_damage = 0
        self.poison_duration = 0
        self.heal_cooldown = 0
        
        # 进一步提高波次难度系数
        self.health_multiplier = 1 + (wave_number - 1) * 1.5  # 每波增加150%的血量
        self.speed_multiplier = 1 + (wave_number - 1) * 0.15  # 每波增加15%的速度
        
        # 设置敌人基础属性
        if enemy_type == EnemyType.NORMAL:
            base_health = 250  # 增加基础血量
            base_speed = 0.018
            base_reward = 20  # 减少奖励
            self.color = '#95a5a6'
        elif enemy_type == EnemyType.FAST:
            base_health = 150
            base_speed = 0.028
            base_reward = 25
            self.color = '#2ecc71'
        elif enemy_type == EnemyType.TANK:
            base_health = 600  # 增加坦克血量
            base_speed = 0.012
            base_reward = 40
            self.color = '#e67e22'
        elif enemy_type == EnemyType.BOSS:
            base_health = 2000  # 增加Boss血量
            base_speed = 0.015
            base_reward = 100
            self.color = '#c0392b'
        elif enemy_type == EnemyType.FLYING:
            base_health = 200
            base_speed = 0.025
            base_reward = 45
            self.color = '#9b59b6'
        elif enemy_type == EnemyType.STEALTH:
            base_health = 180
            base_speed = 0.028
            base_reward = 50
            self.color = '#34495e'
            self.stealth = True
        elif enemy_type == EnemyType.HEALER:
            base_health = 180
            base_speed = 0.015
            base_reward = 60
            self.color = '#1abc9c'
        else:  # SWARM
            base_health = 80
            base_speed = 0.035
            base_reward = 10
            self.color = '#e74c3c'
        
        # 应用波次难度系数
        self.max_health = int(base_health * self.health_multiplier)
        self.health = self.max_health
        self.speed = base_speed * self.speed_multiplier
        self.reward = int(base_reward * self.health_multiplier)

class TowerDefense:
    def __init__(self, root):
        self.root = root
        self.root.title("塔防游戏")
        
        # 游戏常量
        self.GRID_SIZE = 30
        self.GRID_WIDTH = 35
        self.GRID_HEIGHT = 18
        self.CANVAS_WIDTH = self.GRID_WIDTH * self.GRID_SIZE
        self.CANVAS_HEIGHT = self.GRID_HEIGHT * self.GRID_SIZE
        
        # 加载图片
        self.tower_images = {}
        self.enemy_images = {}
        self.load_images()
        
        # 游戏状态
        self.towers = []
        self.enemies = []
        self.waves = []
        self.current_wave = 0
        self.lives = 30
        self.money = 300
        self.score = 0
        self.is_running = False
        self.selected_tower = None
        self.game_speed = 30
        self.wave_timer = 0
        self.wave_interval = 200
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 12
        self.current_wave_enemies = 0
        self.wave_enemies_count = 0
        
        # 创建路径
        self.paths = self.create_paths()  # 修改为多条路径
        self.path = self.paths[0]  # 默认使用第一条路径
        
        # 创建界面
        self.create_widgets()
        
        # 绑定事件
        self.canvas.bind('<Button-1>', self.handle_click)
        self.root.bind('<Key>', self.handle_keypress)
        
        # 开始游戏循环
        self.update()

    def create_paths(self):
        paths = []
        
        # 第一条路径（左上到右中）
        path1 = []
        path1.append((0, 4))
        for x in range(1, 12):
            path1.append((x, 4))
        for y in range(5, 8):
            path1.append((11, y))
        for x in range(10, -1, -1):
            path1.append((x, 7))
        for y in range(6, 3, -1):
            path1.append((0, y))
        for x in range(1, 20):
            path1.append((x, 4))
        paths.append(path1)
        
        # 第二条路径（左下到右上）
        path2 = []
        path2.append((0, 12))
        for x in range(1, 15):
            path2.append((x, 12))
        for y in range(11, 8, -1):
            path2.append((14, y))
        for x in range(15, 25):
            path2.append((x, 9))
        for y in range(10, 13):
            path2.append((24, y))
        for x in range(23, 18, -1):
            path2.append((x, 12))
        paths.append(path2)
        
        # 第三条路径（右边到中间）
        path3 = []
        path3.append((34, 8))
        for x in range(33, 28, -1):
            path3.append((x, 8))
        for y in range(9, 15):
            path3.append((28, y))
        for x in range(29, 32):
            path3.append((x, 14))
        paths.append(path3)
        
        # 第四条路径（右边到左下）
        path4 = []
        path4.append((34, 16))
        for x in range(33, 28, -1):
            path4.append((x, 16))
        for y in range(15, 12, -1):
            path4.append((28, y))
        for x in range(27, 22, -1):
            path4.append((x, 12))
        paths.append(path4)
        
        # 第五条路径（上方到中间）
        path5 = []
        path5.append((17, 0))
        for y in range(1, 6):
            path5.append((17, y))
        for x in range(16, 13, -1):
            path5.append((x, 5))
        for y in range(6, 9):
            path5.append((13, y))
        for x in range(14, 17):
            path5.append((x, 8))
        paths.append(path5)
        
        # 第六条路径（左上方到右下方）
        path6 = []
        path6.append((0, 0))
        for x in range(1, 8):
            path6.append((x, x))
        for x in range(8, 15):
            path6.append((x, 7))
        for y in range(8, 15):
            path6.append((14, y))
        for x in range(15, 22):
            path6.append((x, 14))
        paths.append(path6)
        
        # 第七条路径（右上方到左下方）
        path7 = []
        path7.append((34, 0))
        for x in range(33, 26, -1):
            path7.append((x, 34-x))
        for x in range(26, 19, -1):
            path7.append((x, 8))
        for y in range(9, 16):
            path7.append((19, y))
        for x in range(18, 11, -1):
            path7.append((x, 15))
        paths.append(path7)
        
        return paths

    def load_images(self):
        # 创建图片目录
        if not os.path.exists('game_images'):
            os.makedirs('game_images')
        
        # 加载防御塔图片
        tower_colors = {
            TowerType.ARROW: '#3498db',
            TowerType.CANNON: '#e74c3c',
            TowerType.MAGIC: '#9b59b6',
            TowerType.LASER: '#f1c40f',
            TowerType.ICE: '#00bfff',
            TowerType.POISON: '#32cd32',
            TowerType.SNIPER: '#8b4513',
            TowerType.SUPPORT: '#ffd700'
        }
        
        for tower_type, color in tower_colors.items():
            img = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
            pixels = img.load()
            base_rgb = ImageColor.getrgb(color)
            
            # 绘制防御塔
            self.draw_tower(pixels, base_rgb, tower_type)
            
            img_path = f'game_images/{tower_type.name.lower()}.png'
            img.save(img_path)
            self.tower_images[tower_type] = ImageTk.PhotoImage(img)
        
        # 加载敌人图片
        enemy_colors = {
            EnemyType.NORMAL: '#95a5a6',
            EnemyType.FAST: '#2ecc71',
            EnemyType.TANK: '#e67e22',
            EnemyType.BOSS: '#c0392b',
            EnemyType.FLYING: '#9b59b6',
            EnemyType.STEALTH: '#34495e',
            EnemyType.HEALER: '#1abc9c',
            EnemyType.SWARM: '#e74c3c'
        }
        
        for enemy_type, color in enemy_colors.items():
            img = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
            pixels = img.load()
            base_rgb = ImageColor.getrgb(color)
            
            # 绘制敌人
            self.draw_enemy(pixels, base_rgb, enemy_type)
            
            img_path = f'game_images/{enemy_type.name.lower()}.png'
            img.save(img_path)
            self.enemy_images[enemy_type] = ImageTk.PhotoImage(img)

    def draw_tower(self, pixels, base_rgb, tower_type):
        # 绘制底座
        for x in range(30):
            for y in range(22, 28):
                dx = (x-15)/10.0
                dy = (y-26)/3.0
                if dx*dx + dy*dy <= 1:
                    shadow = int(60 - 40*abs(dx))
                    pixels[x, y] = (shadow, shadow, shadow, 120)
        
        # 绘制塔身
        for x in range(30):
            for y in range(30):
                dx, dy = x-15, y-20
                r = math.sqrt(dx*dx + dy*dy)
                if r <= 12:
                    shade = max(0.4, 1 - r/15)
                    edge = 0.7 if r > 10 else 1.0
                    rgb = tuple(int(c*shade*edge) for c in base_rgb)
                    pixels[x, y] = rgb + (255,)
                elif 12 < r <= 13:
                    rgb = tuple(int(c*0.3) for c in base_rgb)
                    pixels[x, y] = rgb + (255,)
        
        # 根据塔类型添加特殊效果
        if tower_type == TowerType.ARROW:
            # 箭塔顶部
            for y in range(2, 9):
                for x in range(13, 17):
                    if abs(x-15) <= (y-2)/2:
                        highlight = tuple(min(255, int(c*1.3+80)) for c in base_rgb)
                        pixels[x, y] = highlight + (255,)
        elif tower_type == TowerType.CANNON:
            # 炮塔炮管
            for x in range(11, 20):
                for y in range(7, 19):
                    dx = (x-15)/4.5
                    dy = (y-13)/6.0
                    if dx*dx + dy*dy <= 1:
                        shade = 0.5 + 0.5*(x-11)/9
                        rgb = tuple(int(c*shade) for c in base_rgb)
                        pixels[x, y] = rgb + (255,)
        elif tower_type == TowerType.MAGIC:
            # 魔法塔光环
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 8 <= r <= 10:
                        pixels[x, y] = base_rgb + (150,)
        elif tower_type == TowerType.LASER:
            # 激光塔发射器
            for x in range(13, 17):
                for y in range(5, 15):
                    pixels[x, y] = base_rgb + (255,)
        elif tower_type == TowerType.ICE:
            # 冰塔冰晶
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 5 <= r <= 7:
                        pixels[x, y] = (200, 200, 255, 200)
        elif tower_type == TowerType.POISON:
            # 毒塔毒气
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 6 <= r <= 8:
                        pixels[x, y] = (100, 255, 100, 150)
        elif tower_type == TowerType.SNIPER:
            # 狙击塔瞄准镜
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 3 <= r <= 5:
                        pixels[x, y] = (255, 255, 255, 200)
        elif tower_type == TowerType.SUPPORT:
            # 支援塔光环
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 7 <= r <= 9:
                        pixels[x, y] = (255, 255, 200, 150)

    def draw_enemy(self, pixels, base_rgb, enemy_type):
        # 绘制基础形状
        for x in range(30):
            for y in range(30):
                dx, dy = x-15, y-15
                r = math.sqrt(dx*dx + dy*dy)
                if r <= 10:
                    shade = max(0.4, 1 - r/12)
                    rgb = tuple(int(c*shade) for c in base_rgb)
                    pixels[x, y] = rgb + (255,)
        
        # 根据敌人类型添加特殊效果
        if enemy_type == EnemyType.NORMAL:
            # 普通敌人
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 8 <= r <= 9:
                        pixels[x, y] = (200, 200, 200, 200)
        elif enemy_type == EnemyType.FAST:
            # 快速敌人速度线
            for x in range(30):
                for y in range(30):
                    if abs(x-15) <= 2 and y > 20:
                        pixels[x, y] = (200, 255, 200, 200)
        elif enemy_type == EnemyType.TANK:
            # 坦克装甲
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 7 <= r <= 8:
                        pixels[x, y] = (150, 150, 150, 200)
        elif enemy_type == EnemyType.BOSS:
            # Boss光环
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 9 <= r <= 11:
                        pixels[x, y] = (255, 0, 0, 150)
        elif enemy_type == EnemyType.FLYING:
            # 飞行敌人翅膀
            for x in range(30):
                for y in range(30):
                    if abs(x-15) > 8 and abs(y-15) < 5:
                        pixels[x, y] = (200, 200, 255, 200)
        elif enemy_type == EnemyType.STEALTH:
            # 隐身敌人半透明效果
            for x in range(30):
                for y in range(30):
                    if pixels[x, y][3] > 0:
                        pixels[x, y] = pixels[x, y][:3] + (150,)
        elif enemy_type == EnemyType.HEALER:
            # 治疗者光环
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 8 <= r <= 10:
                        pixels[x, y] = (200, 255, 200, 150)
        elif enemy_type == EnemyType.SWARM:
            # 集群敌人小点
            for x in range(30):
                for y in range(30):
                    dx, dy = x-15, y-15
                    r = math.sqrt(dx*dx + dy*dy)
                    if 3 <= r <= 4:
                        pixels[x, y] = (255, 200, 200, 200)

    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=3, pady=3)  # 进一步减小边距
        
        # 创建画布
        self.canvas = tk.Canvas(main_frame, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg='#f0f0f0')
        self.canvas.pack(pady=3)  # 进一步减小边距
        
        # 创建信息框架
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill='x', pady=1)  # 进一步减小边距
        
        # 生命值显示
        self.lives_label = tk.Label(info_frame, text=f"生命值: {self.lives}", font=('Arial', 9))  # 进一步减小字体
        self.lives_label.pack(side='left', padx=2)  # 进一步减小边距
        
        # 金钱显示
        self.money_label = tk.Label(info_frame, text=f"金钱: {self.money}", font=('Arial', 9))  # 进一步减小字体
        self.money_label.pack(side='left', padx=2)  # 进一步减小边距
        
        # 分数显示
        self.score_label = tk.Label(info_frame, text=f"分数: {self.score}", font=('Arial', 9))  # 进一步减小字体
        self.score_label.pack(side='left', padx=2)  # 进一步减小边距
        
        # 波数显示
        self.wave_label = tk.Label(info_frame, text=f"波数: {self.current_wave}", font=('Arial', 9))  # 进一步减小字体
        self.wave_label.pack(side='left', padx=2)  # 进一步减小边距
        
        # 开始按钮
        self.start_button = tk.Button(main_frame, text="开始游戏", command=self.start_game, font=('Arial', 9))  # 进一步减小字体
        self.start_button.pack(pady=2)  # 进一步减小边距
        
        # 创建卡牌区域（使用滚动条）
        cards_container = tk.Frame(main_frame)
        cards_container.pack(fill='x', pady=2)  # 进一步减小边距
        
        # 创建画布和滚动条
        cards_canvas = tk.Canvas(cards_container)
        scrollbar = tk.Scrollbar(cards_container, orient="horizontal", command=cards_canvas.xview)
        scrollable_frame = tk.Frame(cards_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: cards_canvas.configure(scrollregion=cards_canvas.bbox("all"))
        )
        
        cards_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        cards_canvas.configure(xscrollcommand=scrollbar.set)
        
        # 创建塔卡牌
        self.tower_cards = []
        for tower_type in TowerType:
            # 创建临时塔实例来获取属性
            temp_tower = Tower(tower_type, 0, 0)
            
            # 创建卡牌框架
            card_frame = tk.Frame(scrollable_frame, relief='raised', borderwidth=1)
            card_frame.pack(side='left', padx=2)  # 进一步减小边距
            
            # 卡牌标题
            title_label = tk.Label(card_frame, text=temp_tower.description, font=('Arial', 7, 'bold'))  # 进一步减小字体
            title_label.pack()
            
            # 卡牌属性
            stats_label = tk.Label(card_frame, text=temp_tower.get_stats_text(), font=('Arial', 7))  # 进一步减小字体
            stats_label.pack()
            
            # 卡牌价格
            cost_label = tk.Label(card_frame, text=f"价格: {temp_tower.cost}金币", font=('Arial', 7))  # 进一步减小字体
            cost_label.pack()
            
            # 卡牌按钮
            btn = tk.Button(card_frame, 
                          text="选择",
                          command=lambda t=tower_type: self.select_tower(t),
                          font=('Arial', 7))  # 进一步减小字体
            btn.pack(pady=1)
            
            self.tower_cards.append((card_frame, btn))
        
        # 放置滚动条和画布
        scrollbar.pack(side="bottom", fill="x")
        cards_canvas.pack(side="top", fill="x")
        
        # 控制说明
        controls_label = tk.Label(main_frame, 
                                text="点击空地建造防御塔\n1-8 快速选择防御塔\n右键点击塔升级",
                                font=('Arial', 7))  # 进一步减小字体
        controls_label.pack(pady=2)  # 进一步减小边距
        
        # 绑定右键点击事件
        self.canvas.bind('<Button-3>', self.handle_right_click)
        
        # 默认选择第一个塔
        self.selected_tower = TowerType.ARROW
    
    def get_tower_cost(self, tower_type):
        if tower_type == TowerType.ARROW:
            return 100
        elif tower_type == TowerType.CANNON:
            return 200
        elif tower_type == TowerType.MAGIC:
            return 150
        elif tower_type == TowerType.LASER:
            return 250
        elif tower_type == TowerType.ICE:
            return 175
        elif tower_type == TowerType.POISON:
            return 225
        elif tower_type == TowerType.SNIPER:
            return 300
        else:  # SUPPORT
            return 275
    
    def update(self):
        if self.is_running:
            # 更新波次计时器
            self.wave_timer += 1
            self.enemy_spawn_timer += 1
            
            # 检查是否需要开始新的波次
            if self.wave_timer >= self.wave_interval and not self.enemies:
                self.start_new_wave()
                self.wave_timer = 0
            
            # 在当前波次中生成敌人
            if self.current_wave_enemies < self.wave_enemies_count and self.enemy_spawn_timer >= self.enemy_spawn_interval:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
            
            # 更新敌人位置和状态
            for enemy in self.enemies[:]:
                # 处理特殊状态
                if enemy.frozen:
                    enemy.speed = 0
                    enemy.frozen = False
                if enemy.poisoned:
                    enemy.health -= enemy.poison_damage
                    enemy.poison_duration -= 1
                    if enemy.poison_duration <= 0:
                        enemy.poisoned = False
                
                # 处理治疗者
                if enemy.type == EnemyType.HEALER and enemy.heal_cooldown <= 0:
                    for other_enemy in self.enemies:
                        if other_enemy != enemy and other_enemy.health < other_enemy.max_health:
                            other_enemy.health = min(other_enemy.max_health, other_enemy.health + 10)
                    enemy.heal_cooldown = 60
                enemy.heal_cooldown = max(0, enemy.heal_cooldown - 1)
                
                # 处理隐身敌人
                if enemy.type == EnemyType.STEALTH:
                    enemy.stealth = not enemy.stealth
                
                # 更新位置
                if enemy.path_index < len(enemy.path) - 1:
                    target_x, target_y = enemy.path[enemy.path_index + 1]
                    dx = target_x - enemy.x
                    dy = target_y - enemy.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance < enemy.speed:
                        enemy.path_index += 1
                        enemy.x = target_x
                        enemy.y = target_y
                    else:
                        move_speed = enemy.speed * (1.0 + random.uniform(-0.1, 0.1))
                        enemy.x += dx * move_speed / distance
                        enemy.y += dy * move_speed / distance
                else:
                    self.lives -= 1
                    self.lives_label.config(text=f"生命值: {self.lives}")
                    self.enemies.remove(enemy)
                    if self.lives <= 0:
                        self.game_over()
            
            # 更新塔的攻击
            for tower in self.towers:
                if tower.cooldown > 0:
                    tower.cooldown -= 1
                    continue
                
                # 支援塔效果
                if tower.type == TowerType.SUPPORT:
                    for other_tower in self.towers:
                        if other_tower != tower:
                            dx = other_tower.x - tower.x
                            dy = other_tower.y - tower.y
                            distance = math.sqrt(dx * dx + dy * dy)
                            if distance <= tower.range:
                                other_tower.damage *= 1.2
                    continue
                
                # 寻找目标
                if not tower.target or tower.target not in self.enemies:
                    tower.target = None
                    min_distance = float('inf')
                    for enemy in self.enemies:
                        if enemy.stealth and tower.type != TowerType.SNIPER:
                            continue
                        dx = enemy.x - tower.x
                        dy = enemy.y - tower.y
                        distance = math.sqrt(dx * dx + dy * dy)
                        if distance <= tower.range and distance < min_distance:
                            tower.target = enemy
                            min_distance = distance
                
                # 攻击目标
                if tower.target:
                    dx = tower.target.x - tower.x
                    dy = tower.target.y - tower.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance <= tower.range:
                        tower.attack_trajectory = [(tower.x, tower.y), (tower.target.x, tower.target.y)]
                        
                        if tower.type == TowerType.CANNON:
                            for enemy in self.enemies[:]:
                                ex = enemy.x - tower.x
                                ey = enemy.y - tower.y
                                if math.sqrt(ex * ex + ey * ey) <= 1:
                                    enemy.health -= tower.damage
                                    if enemy.health <= 0:
                                        self.money += enemy.reward
                                        self.score += enemy.reward
                                        self.enemies.remove(enemy)
                        elif tower.type == TowerType.SNIPER:
                            damage = tower.damage * (2 if random.random() < 0.3 else 1)
                            tower.target.health -= damage
                            if tower.target.health <= 0:
                                self.money += tower.target.reward
                                self.score += tower.target.reward
                                self.enemies.remove(tower.target)
                                tower.target = None
                        elif tower.type == TowerType.ICE:
                            tower.target.frozen = True
                            tower.target.health -= tower.damage
                            if tower.target.health <= 0:
                                self.money += tower.target.reward
                                self.score += tower.target.reward
                                self.enemies.remove(tower.target)
                                tower.target = None
                        elif tower.type == TowerType.POISON:
                            tower.target.poisoned = True
                            tower.target.poison_duration = 5
                            tower.target.poison_damage = tower.damage
                            tower.target.health -= tower.damage
                            if tower.target.health <= 0:
                                self.money += tower.target.reward
                                self.score += tower.target.reward
                                self.enemies.remove(tower.target)
                                tower.target = None
                        else:
                            tower.target.health -= tower.damage
                            if tower.target.health <= 0:
                                self.money += tower.target.reward
                                self.score += tower.target.reward
                                self.enemies.remove(tower.target)
                                tower.target = None
                        
                        tower.cooldown = tower.attack_speed
                    else:
                        tower.attack_trajectory = []
            
            # 更新显示
            self.money_label.config(text=f"金钱: {self.money}")
            self.score_label.config(text=f"分数: {self.score}")
        
        # 重绘游戏画面
        self.draw()
        
        # 继续游戏循环
        self.root.after(self.game_speed, self.update)
    
    def start_new_wave(self):
        self.current_wave += 1
        self.wave_label.config(text=f"波数: {self.current_wave}")
        
        # 根据波数设置敌人数量和类型
        if self.current_wave <= 5:
            self.wave_enemies_count = 10 + self.current_wave
            self.enemy_types = [EnemyType.NORMAL, EnemyType.FAST]
        elif self.current_wave <= 10:
            self.wave_enemies_count = 12 + self.current_wave
            self.enemy_types = [EnemyType.NORMAL, EnemyType.FAST, EnemyType.FLYING, EnemyType.TANK]
        elif self.current_wave <= 15:
            self.wave_enemies_count = 15 + self.current_wave
            self.enemy_types = [EnemyType.NORMAL, EnemyType.FAST, EnemyType.FLYING, 
                              EnemyType.TANK, EnemyType.STEALTH, EnemyType.HEALER]
        elif self.current_wave <= 20:
            self.wave_enemies_count = 18 + self.current_wave
            self.enemy_types = [EnemyType.NORMAL, EnemyType.FAST, EnemyType.FLYING,
                              EnemyType.TANK, EnemyType.STEALTH, EnemyType.HEALER, EnemyType.BOSS]
        else:
            self.wave_enemies_count = 20 + self.current_wave
            self.enemy_types = list(EnemyType)
        
        self.current_wave_enemies = 0
        print(f"开始第{self.current_wave}波，将生成{self.wave_enemies_count}个敌人")
        print(f"当前波次血量系数：{1 + (self.current_wave - 1) * 1.5:.2f}")

    def spawn_enemy(self):
        if self.current_wave_enemies < self.wave_enemies_count:
            # 选择敌人类型
            if self.current_wave > 6 and random.random() < 0.5:
                enemy_type = EnemyType.BOSS
            else:
                enemy_type = random.choice(self.enemy_types)
            
            # 随机选择起点和对应的路径
            start_points = [
                (0, 4),    # 左上
                (0, 12),   # 左下
                (34, 8),   # 右边中间
                (34, 16),  # 右边下方
                (17, 0),   # 上方
                (0, 0),    # 左上方
                (34, 0)    # 右上方
            ]
            start_point = random.choice(start_points)
            
            # 根据起点选择对应的路径
            path_index = start_points.index(start_point)
            enemy_path = self.paths[path_index]  # 每个怪物独立路径
            
            # 创建敌人，传入当前波数和选择的路径
            enemy = Enemy(enemy_type, enemy_path, self.current_wave)
            enemy.x = start_point[0]
            enemy.y = start_point[1]
            # 添加随机偏移
            enemy.x += random.uniform(-0.1, 0.1)
            enemy.y += random.uniform(-0.1, 0.1)
            self.enemies.append(enemy)
            self.current_wave_enemies += 1
            
            # 如果是治疗者，额外生成集群敌人
            if enemy_type == EnemyType.HEALER:
                for _ in range(8):
                    swarm = Enemy(EnemyType.SWARM, enemy_path, self.current_wave)
                    swarm.x = start_point[0]
                    swarm.y = start_point[1]
                    swarm.x += random.uniform(-0.1, 0.1)
                    swarm.y += random.uniform(-0.1, 0.1)
                    self.enemies.append(swarm)
                    self.current_wave_enemies += 1
            
            print(f"生成{enemy_type.name}敌人，当前波次进度：{self.current_wave_enemies}/{self.wave_enemies_count}")

    def handle_click(self, event):
        if not self.is_running:
            return
        
        # 将点击位置转换为网格坐标
        grid_x = event.x // self.GRID_SIZE
        grid_y = event.y // self.GRID_SIZE
        
        # 检查是否在路径上
        is_on_path = False
        for path in self.paths:
            for x, y in path:
                if abs(x - grid_x) < 1 and abs(y - grid_y) < 1:
                    is_on_path = True
                    break
            if is_on_path:
                break
        
        if is_on_path:
            return
        
        # 检查是否已有塔
        for tower in self.towers:
            if tower.x == grid_x and tower.y == grid_y:
                return
        
        # 建造选中的塔
        if self.selected_tower:
            cost = self.get_tower_cost(self.selected_tower)
            if self.money >= cost:
                self.money -= cost
                new_tower = Tower(self.selected_tower, grid_x, grid_y)
                self.towers.append(new_tower)
                self.money_label.config(text=f"金钱: {self.money}")
                print(f"建造了{self.selected_tower.name}塔在位置({grid_x}, {grid_y})")

    def handle_keypress(self, event):
        if not self.is_running:
            return
        
        key = event.keysym
        if key in ['1', '2', '3', '4', '5', '6', '7', '8']:
            index = int(key) - 1
            if 0 <= index < len(TowerType):
                self.selected_tower = list(TowerType)[index]
                print(f"通过按键选择了{self.selected_tower.name}塔")
    
    def select_tower(self, tower_type):
        if self.is_running:
            self.selected_tower = tower_type
            print(f"选择了{tower_type.name}塔")
    
    def start_game(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(text="游戏进行中", state='disabled')
            self.selected_tower = TowerType.ARROW
            
            # 减少初始防御塔
            initial_towers = [
                (TowerType.ARROW, 2, 2),    # 箭塔
                (TowerType.ARROW, 2, 6),    # 箭塔
                (TowerType.MAGIC, 6, 2),    # 魔法塔
                (TowerType.ICE, 6, 6)       # 冰塔
            ]
            
            for tower_type, x, y in initial_towers:
                # 检查位置是否在路径上
                is_on_path = False
                for path in self.paths:
                    for path_x, path_y in path:
                        if abs(path_x - x) < 1 and abs(path_y - y) < 1:
                            is_on_path = True
                            break
                    if is_on_path:
                        break
                
                if not is_on_path:
                    new_tower = Tower(tower_type, x, y)
                    self.towers.append(new_tower)
                    print(f"赠送了{tower_type.name}塔在位置({x}, {y})")
            
            # 初始化第一波
            self.start_new_wave()
            print("游戏开始，赠送了初始防御塔")
    
    def game_over(self):
        self.is_running = False
        self.start_button.config(text="重新开始", state='normal')
        messagebox.showinfo("游戏结束", f"游戏结束！\n你的得分是: {self.score}")
    
    def handle_right_click(self, event):
        if not self.is_running:
            return
        
        # 将点击位置转换为网格坐标
        grid_x = event.x // self.GRID_SIZE
        grid_y = event.y // self.GRID_SIZE
        
        # 查找点击位置的塔
        for tower in self.towers:
            if tower.x == grid_x and tower.y == grid_y:
                # 升级塔
                upgrade_cost = self.get_tower_cost(tower.type) * tower.level
                if self.money >= upgrade_cost and tower.upgrade():
                    self.money -= upgrade_cost
                    self.money_label.config(text=f"金钱: {self.money}")
                    break

    def draw(self):
        self.canvas.delete('all')
        
        # 绘制背景网格
        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                self.canvas.create_rectangle(
                    x * self.GRID_SIZE, y * self.GRID_SIZE,
                    (x + 1) * self.GRID_SIZE, (y + 1) * self.GRID_SIZE,
                    outline='#e0e0e0'
                )
        
        # 绘制路径
        for path in self.paths:
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                self.canvas.create_line(
                    x1 * self.GRID_SIZE + self.GRID_SIZE // 2,
                    y1 * self.GRID_SIZE + self.GRID_SIZE // 2,
                    x2 * self.GRID_SIZE + self.GRID_SIZE // 2,
                    y2 * self.GRID_SIZE + self.GRID_SIZE // 2,
                    fill='#95a5a6', width=3
                )
        
        # 绘制所有起点
        for path in self.paths:
            for x, y in path:
                self.canvas.create_oval(
                    x * self.GRID_SIZE + 5, y * self.GRID_SIZE + 5,
                    x * self.GRID_SIZE + self.GRID_SIZE - 5,
                    y * self.GRID_SIZE + self.GRID_SIZE - 5,
                    fill='#2ecc71'
                )
        
        # 绘制终点
        end_x, end_y = self.path[-1]
        self.canvas.create_oval(
            end_x * self.GRID_SIZE + 5, end_y * self.GRID_SIZE + 5,
            end_x * self.GRID_SIZE + self.GRID_SIZE - 5,
            end_y * self.GRID_SIZE + self.GRID_SIZE - 5,
            fill='#e74c3c'
        )
        
        # 绘制塔
        for tower in self.towers:
            x = tower.x * self.GRID_SIZE + self.GRID_SIZE // 2
            y = tower.y * self.GRID_SIZE + self.GRID_SIZE // 2
            
            # 使用图片绘制塔
            self.canvas.create_image(x, y, image=self.tower_images[tower.type])
            
            # 绘制塔等级
            if tower.level > 1:
                self.canvas.create_text(
                    x, y + 15,
                    text=str(tower.level),
                    fill='white',
                    font=('Arial', 10, 'bold')
                )
            
            # 绘制攻击范围
            if tower.target:
                self.canvas.create_oval(
                    x - tower.range * self.GRID_SIZE, y - tower.range * self.GRID_SIZE,
                    x + tower.range * self.GRID_SIZE, y + tower.range * self.GRID_SIZE,
                    outline=tower.color, width=1
                )
                
                # 绘制攻击轨迹
                if tower.attack_trajectory:
                    points = []
                    for tx, ty in tower.attack_trajectory:
                        points.extend([
                            tx * self.GRID_SIZE + self.GRID_SIZE // 2,
                            ty * self.GRID_SIZE + self.GRID_SIZE // 2
                        ])
                    if len(points) >= 4:
                        self.canvas.create_line(
                            points,
                            fill=tower.color,
                            width=2,
                            dash=(4, 4)
                        )
        
        # 绘制敌人
        for enemy in self.enemies:
            x = enemy.x * self.GRID_SIZE + self.GRID_SIZE // 2
            y = enemy.y * self.GRID_SIZE + self.GRID_SIZE // 2
            
            # 使用图片绘制敌人
            if enemy.stealth:
                # 隐身敌人半透明
                self.canvas.create_image(x, y, image=self.enemy_images[enemy.type])
                self.canvas.create_oval(
                    x - 15, y - 15, x + 15, y + 15,
                    fill='', outline='gray', stipple='gray50'
                )
            else:
                self.canvas.create_image(x, y, image=self.enemy_images[enemy.type])
            
            # 绘制血条背景
            self.canvas.create_rectangle(
                x - 15, y - 20,
                x + 15, y - 15,
                fill='#e74c3c'
            )
            
            # 绘制血条
            health_ratio = enemy.health / enemy.max_health
            health_width = 30 * health_ratio
            self.canvas.create_rectangle(
                x - 15, y - 20,
                x - 15 + health_width, y - 15,
                fill='#2ecc71'
            )
            
            # 绘制特殊状态效果
            if enemy.frozen:
                self.canvas.create_oval(
                    x - 12, y - 12, x + 12, y + 12,
                    outline='#00bfff',
                    width=2
                )
            if enemy.poisoned:
                self.canvas.create_oval(
                    x - 12, y - 12, x + 12, y + 12,
                    outline='#32cd32',
                    width=2
                )
            
            # 绘制敌人类型标记
            if enemy.type == EnemyType.BOSS:
                self.canvas.create_text(
                    x, y - 25,
                    text="BOSS",
                    fill='red',
                    font=('Arial', 8, 'bold')
                )
            elif enemy.type == EnemyType.HEALER:
                self.canvas.create_text(
                    x, y - 25,
                    text="+",
                    fill='green',
                    font=('Arial', 8, 'bold')
                )

if __name__ == '__main__':
    root = tk.Tk()
    game = TowerDefense(root)
    root.mainloop() 