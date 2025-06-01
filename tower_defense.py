import pygame
import math
import random
from typing import List, Tuple

# 初始化Pygame
pygame.init()

# 游戏常量
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# 游戏类
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("塔防游戏")
        self.clock = pygame.time.Clock()
        self.running = True
        self.money = 100
        self.lives = 20
        self.score = 0
        self.wave = 1
        self.enemies: List[Enemy] = []
        self.towers: List[Tower] = []
        self.path = self.create_path()
        self.spawn_timer = 0
        self.spawn_delay = 1000  # 1秒
        self.last_spawn = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, 36)

    def create_path(self) -> List[Tuple[int, int]]:
        # 创建一条简单的路径
        return [
            (0, 300),
            (200, 300),
            (200, 100),
            (400, 100),
            (400, 500),
            (600, 500),
            (600, 300),
            (800, 300)
        ]

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn > self.spawn_delay:
            self.enemies.append(Enemy(self.path[0][0], self.path[0][1]))
            self.last_spawn = current_time

    def draw_path(self):
        for i in range(len(self.path) - 1):
            pygame.draw.line(self.screen, GRAY, self.path[i], self.path[i + 1], 40)

    def draw_ui(self):
        # 显示金钱
        money_text = self.font.render(f"金钱: {self.money}", True, BLACK)
        self.screen.blit(money_text, (10, 10))
        
        # 显示生命值
        lives_text = self.font.render(f"生命: {self.lives}", True, BLACK)
        self.screen.blit(lives_text, (10, 50))
        
        # 显示分数
        score_text = self.font.render(f"分数: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 90))
        
        # 显示波数
        wave_text = self.font.render(f"波数: {self.wave}", True, BLACK)
        self.screen.blit(wave_text, (10, 130))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self.place_tower(event.pos)

    def place_tower(self, pos):
        if self.money >= 50:  # 塔的价格
            self.towers.append(Tower(pos[0], pos[1]))
            self.money -= 50

    def update(self):
        # 生成敌人
        if len(self.enemies) < self.wave * 5:
            self.spawn_enemy()

        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update(self.path)
            if enemy.reached_end:
                self.lives -= 1
                self.enemies.remove(enemy)
            elif enemy.health <= 0:
                self.money += 10
                self.score += 10
                self.enemies.remove(enemy)

        # 更新塔
        for tower in self.towers:
            tower.update(self.enemies)

        # 检查游戏是否结束
        if self.lives <= 0:
            self.running = False

        # 检查是否进入下一波
        if not self.enemies and self.wave * 5 <= self.score:
            self.wave += 1
            self.money += 50  # 每波奖励

    def draw(self):
        self.screen.fill(WHITE)
        self.draw_path()
        
        # 绘制塔
        for tower in self.towers:
            tower.draw(self.screen)
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        self.draw_ui()
        pygame.display.flip()

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.health = 100
        self.max_health = 100
        self.size = 20
        self.path_index = 0
        self.reached_end = False

    def update(self, path):
        if self.path_index < len(path) - 1:
            target_x, target_y = path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < self.speed:
                self.path_index += 1
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
        else:
            self.reached_end = True

    def draw(self, screen):
        # 绘制敌人
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.size)
        # 绘制血条
        health_width = (self.health / self.max_health) * (self.size * 2)
        pygame.draw.rect(screen, RED, (self.x - self.size, self.y - self.size - 10, self.size * 2, 5))
        pygame.draw.rect(screen, GREEN, (self.x - self.size, self.y - self.size - 10, health_width, 5))

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 150
        self.damage = 20
        self.cooldown = 1000  # 1秒
        self.last_shot = 0
        self.size = 30

    def update(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.cooldown:
            for enemy in enemies:
                distance = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
                if distance <= self.range:
                    enemy.health -= self.damage
                    self.last_shot = current_time
                    break

    def draw(self, screen):
        # 绘制塔
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.size)
        # 绘制攻击范围
        pygame.draw.circle(screen, (200, 200, 200), (int(self.x), int(self.y)), self.range, 1)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit() 