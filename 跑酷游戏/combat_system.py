"""战斗与怪物系统。

"""包含怪物、子弹、技能的基础实现。

该模块同时提供了 ``MonsterManager``，用于集中管理怪物生成、
子弹更新与碰撞检测，使主循环可以方便地集成基础的打怪玩法。
"""

import random
import pygame


class Monster:
    """基础怪物类，负责自身移动、绘制和受击处理。"""

    TYPE_CONFIG = {
        "slime": {
            "color": (0, 255, 0),
            "health": 80,
            "damage": 10,
            "speed": 3,
        },
        "goblin": {
            "color": (139, 69, 19),
            "health": 120,
            "damage": 12,
            "speed": 4,
        },
        "bat": {
            "color": (75, 0, 130),
            "health": 60,
            "damage": 8,
            "speed": 5,
        },
        "boss": {
            "color": (255, 0, 0),
            "health": 300,
            "damage": 20,
            "speed": 2,
        },
    }

    def __init__(self, x: int, y: int, monster_type: str = "slime"):
        self.rect = pygame.Rect(x, y, 60, 60)
        config = self.TYPE_CONFIG.get(monster_type, {})

        self.type = monster_type
        self.health = config.get("health", 100)
        self.max_health = self.health
        self.damage = config.get("damage", 10)
        self.speed = config.get("speed", 2)
        self.color = config.get("color", (128, 128, 128))

        self.attack_range = 50
        self.attack_cooldown = 0
        self.attack_cooldown_max = 30
        self.is_alive = True
        self.is_attacking = False
        self.animation_frame = 0

    def update(self, scroll_speed: int):
        """更新怪物状态并处理移动。"""
        if not self.is_alive:
            return

        # 怪物向左移动，滚动速度加上自身速度
        self.rect.x -= scroll_speed + self.speed

        # 更新攻击冷却
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # 简单动画帧计数（可用于拓展）
        self.animation_frame = (self.animation_frame + 1) % 60

    def take_damage(self, damage: int) -> bool:
        """怪物受到伤害，返回是否被击败。"""
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False
            return True
        return False

    def can_attack_player(self, player_rect: pygame.Rect) -> bool:
        if self.attack_cooldown > 0:
            return False
        distance = abs(self.rect.centerx - player_rect.centerx)
        if distance <= self.attack_range:
            self.is_attacking = True
            self.attack_cooldown = self.attack_cooldown_max
            return True
        return False

    def draw(self, screen: pygame.Surface):
        if not self.is_alive:
            return

        pygame.draw.rect(screen, self.color, self.rect)
        self._draw_health_bar(screen)

        if self.is_attacking:
            self._draw_attack_effect(screen)
            self.is_attacking = False

    def _draw_health_bar(self, screen: pygame.Surface):
        bar_width = self.rect.width
        bar_height = 5
        health_percent = max(0, self.health / self.max_health)

        pygame.draw.rect(
            screen,
            (255, 0, 0),
            (self.rect.x, self.rect.y - 10, bar_width, bar_height),
        )
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            (
                self.rect.x,
                self.rect.y - 10,
                bar_width * health_percent,
                bar_height,
            ),
        )

    def _draw_attack_effect(self, screen: pygame.Surface):
        effect_rect = pygame.Rect(self.rect)
        effect_rect.inflate_ip(10, 10)
        pygame.draw.rect(screen, (255, 200, 0), effect_rect, 2)


class Bullet:
    """子弹类，支持左右方向飞行。"""

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

        if self.rect.x > 1000 or self.rect.right < -50:
            self.is_active = False

    def draw(self, screen: pygame.Surface):
        if self.is_active:
            pygame.draw.rect(screen, (255, 255, 0), self.rect)


class Skill:
    """通用技能系统，提供投射、范围和增益三种类型。"""

    def __init__(self, name, skill_type, cooldown, damage, effect):
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

    def use(self, player, target_pos=None):
        if not self.is_ready:
            return None

        self.current_cooldown = self.cooldown
        self.is_ready = False

        if self.type == "projectile":
            return self.create_projectile(player, target_pos)
        if self.type == "area":
            return self.create_area_effect(player)
        if self.type == "buff":
            self.apply_buff(player)
            return None
        return None

    def create_projectile(self, player, target_pos=None):
        return Bullet(
            x=player.rect.x + player.rect.width,
            y=player.rect.y + player.rect.height // 2,
            direction="right",
            damage=self.damage,
        )

    def create_area_effect(self, player):
        return {
            "x": player.rect.x - 50,
            "y": player.rect.y - 50,
            "width": 150,
            "height": 150,
            "damage": self.damage,
            "duration": 10,
        }

    def apply_buff(self, player):
        if self.effect == "speed_boost":
            player.speed_multiplier = 1.5
            player.buff_timer = 180
        elif self.effect == "invincible":
            player.is_invincible = True
            player.buff_timer = 120


class MonsterManager:
    """管理怪物、子弹与战斗交互的类。"""

    def __init__(self):
        self.monsters: list[Monster] = []
        self.bullets: list[Bullet] = []
        self.spawn_timer = 0
        self.spawn_interval = 150

    def reset(self):
        self.monsters.clear()
        self.bullets.clear()
        self.spawn_timer = 0

    def fire_bullet(self, player):
        bullet = Bullet(
            x=player.rect.right,
            y=player.rect.centery,
            direction="right",
        )
        self.bullets.append(bullet)

    def spawn_monster(self):
        monster_type = random.choice(list(Monster.TYPE_CONFIG.keys()))
        y = random.randint(300, 360)
        monster = Monster(800, y, monster_type)
        self.monsters.append(monster)

    def update(self, scroll_speed: int, player_rect: pygame.Rect | None):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_monster()
            self.spawn_timer = 0
            self.spawn_interval = random.randint(120, 200)

        # 更新怪物
        for monster in self.monsters[:]:
            monster.update(scroll_speed)
            if monster.rect.right < 0 or not monster.is_alive:
                self.monsters.remove(monster)

        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.is_active:
                self.bullets.remove(bullet)

        kills = self._handle_bullet_collisions()
        player_hit = self._check_player_collision(player_rect) if player_rect else False

        return {"kills": kills, "player_hit": player_hit}

    def _handle_bullet_collisions(self) -> int:
        kills = 0
        for bullet in self.bullets[:]:
            for monster in self.monsters[:]:
                if bullet.rect.colliderect(monster.rect):
                    bullet.is_active = False
                    if monster.take_damage(bullet.damage):
                        kills += 1
                        self.monsters.remove(monster)
                    break
            if not bullet.is_active and bullet in self.bullets:
                self.bullets.remove(bullet)
        return kills

    def _check_player_collision(self, player_rect: pygame.Rect) -> bool:
        for monster in self.monsters:
            if monster.rect.colliderect(player_rect):
                return True
            if monster.can_attack_player(player_rect):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        for monster in self.monsters:
            monster.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
