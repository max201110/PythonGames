import pygame
import math
import random
from typing import List, Tuple
import os

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
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 游戏类
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tower Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        self.money = 200  # Initial money
        self.lives = 20
        self.score = 0
        self.wave = 1
        self.enemies: List[Enemy] = []
        self.towers: List[Tower] = []
        self.path = self.create_path()
        self.end_point = self.path[-1]  # 保存终点位置
        self.spawn_timer = 0
        self.spawn_delay = 1500  # Spawn delay 1.5s
        self.last_spawn = pygame.time.get_ticks()
        
        # 设置中文字体
        if os.name == 'nt':  # Windows
            self.font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 36)
        elif os.name == 'posix':  # macOS 或 Linux
            self.font = pygame.font.SysFont('pingfang', 36)
        else:
            self.font = pygame.font.SysFont(None, 36)
        self.end_point_animation = 0  # 用于终点动画

    def create_path(self) -> List[Tuple[int, int]]:
        # Create a simple path
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
        # Draw the path
        for i in range(len(self.path) - 1):
            pygame.draw.line(self.screen, GRAY, self.path[i], self.path[i + 1], 40)
        
        # Draw the end point with animation
        self.end_point_animation = (self.end_point_animation + 2) % 360
        radius = 30 + math.sin(math.radians(self.end_point_animation)) * 5
        
        # Draw outer glow
        for r in range(3):
            pygame.draw.circle(self.screen, ORANGE, 
                             (int(self.end_point[0]), int(self.end_point[1])), 
                             int(radius + r * 2), 2)
        
        # Draw main circle
        pygame.draw.circle(self.screen, YELLOW, 
                         (int(self.end_point[0]), int(self.end_point[1])), 
                         int(radius))
        
        # Draw inner circle
        pygame.draw.circle(self.screen, ORANGE, 
                         (int(self.end_point[0]), int(self.end_point[1])), 
                         int(radius * 0.7))
        
        # Draw cross
        cross_size = radius * 0.4
        pygame.draw.line(self.screen, RED,
                        (self.end_point[0] - cross_size, self.end_point[1]),
                        (self.end_point[0] + cross_size, self.end_point[1]), 3)
        pygame.draw.line(self.screen, RED,
                        (self.end_point[0], self.end_point[1] - cross_size),
                        (self.end_point[0], self.end_point[1] + cross_size), 3)

    def draw_ui(self):
        # Show money
        money_text = self.font.render(f"Money: {self.money}", True, BLACK)
        self.screen.blit(money_text, (10, 10))
        
        # Show lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, BLACK)
        self.screen.blit(lives_text, (10, 50))
        
        # Show score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 90))
        
        # Show wave
        wave_text = self.font.render(f"Wave: {self.wave}", True, BLACK)
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
                if event.button == 1:  # Left click
                    self.place_tower(event.pos)

    def place_tower(self, pos):
        if self.money >= 30:  # Tower cost
            # 检查是否与现有塔重叠
            for tower in self.towers:
                distance = math.sqrt((tower.x - pos[0]) ** 2 + (tower.y - pos[1]) ** 2)
                if distance < tower.size * 2:  # 如果距离小于两个塔的直径，则视为重叠
                    return  # 如果重叠，直接返回，不放置新塔
            
            # 检查是否在路径上
            for i in range(len(self.path) - 1):
                # 计算点到线段的距离
                x1, y1 = self.path[i]
                x2, y2 = self.path[i + 1]
                # 计算线段向量
                line_vec = (x2 - x1, y2 - y1)
                # 计算点到线段起点的向量
                point_vec = (pos[0] - x1, pos[1] - y1)
                # 计算线段长度的平方
                line_len_sq = line_vec[0] ** 2 + line_vec[1] ** 2
                # 计算投影比例
                t = max(0, min(1, (point_vec[0] * line_vec[0] + point_vec[1] * line_vec[1]) / line_len_sq))
                # 计算投影点
                proj_x = x1 + t * line_vec[0]
                proj_y = y1 + t * line_vec[1]
                # 计算点到投影点的距离
                distance = math.sqrt((pos[0] - proj_x) ** 2 + (pos[1] - proj_y) ** 2)
                if distance < 40:  # 如果距离小于路径宽度的一半，则视为在路径上
                    return  # 如果在路径上，直接返回，不放置新塔
            
            # 如果通过所有检查，则放置新塔
            self.towers.append(Tower(pos[0], pos[1]))
            self.money -= 30

    def update(self):
        # Spawn enemies
        if len(self.enemies) < self.wave * 5:
            self.spawn_enemy()

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.path)
            if enemy.reached_end:
                self.lives -= 1
                self.enemies.remove(enemy)
            elif enemy.health <= 0:
                self.money += 20  # Enemy kill reward
                self.score += 10
                self.enemies.remove(enemy)

        # Update towers
        for tower in self.towers:
            tower.update(self.enemies)

        # Check game over
        if self.lives <= 0:
            self.running = False

        # Check next wave
        if not self.enemies and self.wave * 5 <= self.score:
            self.wave += 1
            self.money += 100  # Wave completion reward

    def draw(self):
        self.screen.fill(WHITE)
        self.draw_path()
        
        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        self.draw_ui()
        pygame.display.flip()

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 1  # Enemy speed
        self.health = 50  # Enemy health
        self.max_health = 50
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
        # Draw enemy
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.size)
        # Draw health bar
        health_width = (self.health / self.max_health) * (self.size * 2)
        pygame.draw.rect(screen, RED, (self.x - self.size, self.y - self.size - 10, self.size * 2, 5))
        pygame.draw.rect(screen, GREEN, (self.x - self.size, self.y - self.size - 10, health_width, 5))

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 150
        self.damage = 25  # Tower damage
        self.cooldown = 800  # Attack cooldown
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
        # Draw tower
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.size)
        # Draw attack range
        pygame.draw.circle(screen, (200, 200, 200), (int(self.x), int(self.y)), self.range, 1)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit() 