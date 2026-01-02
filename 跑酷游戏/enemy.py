"""敌人和战斗系统集成模块。

该模块从原有的“打怪系统”草稿整理而来，提供：
- 基础的怪物、子弹、技能定义
- 敌人管理器（生成、更新、绘制、碰撞检测）
- 资源加载占位与缺失记录
"""

import os
import random
from typing import Dict, List, Optional

import pygame


class Monster:
    """简单的怪物实体。"""

    def __init__(self, x: int, y: int, monster_type: str, image: Optional[pygame.Surface] = None):
        self.rect = pygame.Rect(x, y, 60, 60)
        self.type = monster_type

        # 战斗属性
        self.health = 100
        self.max_health = 100
        self.damage = 10
        self.speed = 2
        self.attack_range = 50
        self.attack_cooldown = 0

        # 状态
        self.is_alive = True
        self.is_attacking = False

        # 视觉
        self.image = image if image else self._build_fallback_surface()
        self.color = self._get_color_by_type()
        self.animation_frame = 0

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    def _get_color_by_type(self):
        colors = {
            "slime": (0, 255, 0),  # 绿色史莱姆
            "goblin": (139, 69, 19),  # 棕色哥布林
            "bat": (75, 0, 130),  # 紫色蝙蝠
            "boss": (255, 0, 0),  # 红色Boss
        }
        return colors.get(self.type, (128, 128, 128))

    def _build_fallback_surface(self):
        surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        surface.fill(self._get_color_by_type())
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)
        return surface

    def update(self, scroll_speed: int):
        if not self.is_alive:
            return

        # 敌人向左移动，叠加基础速度
        self.rect.x -= scroll_speed + self.speed

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.animation_frame = (self.animation_frame + 1) % 60

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        if self.health <= 0:
            self.die()
            return True
        return False

    def die(self):
        self.is_alive = False

    def attack(self, player_rect: pygame.Rect) -> bool:
        if self.attack_cooldown > 0:
            return False

        distance = abs(self.rect.centerx - player_rect.centerx)
        if distance <= self.attack_range:
            self.is_attacking = True
            self.attack_cooldown = 30
            return True
        return False

    def draw(self, screen: pygame.Surface):
        if not self.is_alive:
            return

        screen.blit(self.image, self.rect)
        self._draw_health_bar(screen)

        if self.is_attacking:
            self._draw_attack_effect(screen)
            self.is_attacking = False

    def _draw_health_bar(self, screen: pygame.Surface):
        bar_width = self.rect.width
        bar_height = 5
        health_percent = max(self.health, 0) / self.max_health

        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            (self.rect.x, self.rect.y - 10, bar_width * health_percent, bar_height),
        )

    def _draw_attack_effect(self, screen: pygame.Surface):
        effect_rect = pygame.Rect(self.rect.centerx, self.rect.centery - 10, 20, 20)
        pygame.draw.rect(screen, (255, 255, 0), effect_rect, border_radius=3)


class Bullet:
    def __init__(self, x: int, y: int, direction: str = "right", damage: int = 20):
        self.rect = pygame.Rect(x, y, 15, 5)
        self.speed = 10
        self.damage = damage
        self.direction = direction
        self.is_active = True

    def update(self):
        if self.direction == "right":
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

        if self.rect.x > 1000 or self.rect.x < -50:
            self.is_active = False

    def draw(self, screen: pygame.Surface):
        if self.is_active:
            pygame.draw.rect(screen, (255, 255, 0), self.rect)


class Skill:
    def __init__(self, name: str, skill_type: str, cooldown: int, damage: int, effect: Optional[str]):
        self.name = name
        self.type = skill_type
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.damage = damage
        self.effect = effect
        self.is_ready = True

    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            if self.current_cooldown <= 0:
                self.is_ready = True

    def use(self, player_rect: pygame.Rect, target_pos=None):
        if not self.is_ready:
            return None

        self.current_cooldown = self.cooldown
        self.is_ready = False

        if self.type == "projectile":
            return Bullet(x=player_rect.right, y=player_rect.centery, direction="right", damage=self.damage)
        elif self.type == "area":
            return {
                "x": player_rect.x - 50,
                "y": player_rect.y - 50,
                "width": 150,
                "height": 150,
                "damage": self.damage,
                "duration": 10,
            }
        elif self.type == "buff":
            return None


class EnemyManager:
    """统一管理怪物和战斗交互。"""

    def __init__(self):
        self.monsters: List[Monster] = []
        self.player_bullets: List[Bullet] = []
        self.spawn_timer = 0
        self.spawn_interval = 120
        self.missing_assets: List[str] = []

        self.monster_images = self._load_monster_images()

    def _load_monster_images(self) -> Dict[str, pygame.Surface]:
        images: Dict[str, pygame.Surface] = {}
        expected = {
            "slime": "assets/enemy/slime.png",
            "goblin": "assets/enemy/goblin.png",
            "bat": "assets/enemy/bat.png",
            "boss": "assets/enemy/boss.png",
        }

        for monster_type, path in expected.items():
            if os.path.exists(path):
                loaded = pygame.image.load(path).convert_alpha()
                loaded = pygame.transform.scale(loaded, (60, 60))
                images[monster_type] = loaded
            else:
                self.missing_assets.append(path)

        return images

    def reset(self):
        self.monsters.clear()
        self.player_bullets.clear()
        self.spawn_timer = 0

    def spawn_monster(self):
        monster_types = ["slime", "goblin", "bat"]
        monster_type = random.choice(monster_types)
        ground_y = 400 - 60
        new_monster = Monster(800, ground_y, monster_type, self.monster_images.get(monster_type))
        self.monsters.append(new_monster)

    def spawn_player_bullet(self, player_rect: pygame.Rect, damage: int = 25):
        bullet = Bullet(x=player_rect.right, y=player_rect.centery, direction="right", damage=damage)
        self.player_bullets.append(bullet)

    def update(self, scroll_speed: int, player_rect: Optional[pygame.Rect]) -> bool:
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_monster()
            self.spawn_interval = random.randint(100, 160)
            self.spawn_timer = 0

        player_hit = False

        for monster in self.monsters[:]:
            monster.update(scroll_speed)
            if monster.rect.right < 0 or not monster.is_alive:
                self.monsters.remove(monster)

        for bullet in self.player_bullets[:]:
            bullet.update()
            if not bullet.is_active:
                self.player_bullets.remove(bullet)
                continue

            for monster in self.monsters[:]:
                if bullet.rect.colliderect(monster.rect) and monster.is_alive:
                    bullet.is_active = False
                    is_dead = monster.take_damage(bullet.damage)
                    if is_dead:
                        self.monsters.remove(monster)
                    break

        if player_rect:
            for monster in self.monsters:
                if monster.attack(player_rect):
                    # 玩家受击逻辑可在外部补充，这里仅标记攻击动画
                    player_hit = True

        return player_hit

    def draw(self, screen: pygame.Surface):
        for monster in self.monsters:
            monster.draw(screen)

        for bullet in self.player_bullets:
            bullet.draw(screen)

