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
        for i in range(len(self.path) - 1):
            pygame.draw.line(self.screen, GRAY, self.path[i], self.path[i + 1], 40)

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