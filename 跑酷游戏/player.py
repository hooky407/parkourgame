# player.py
import pygame
import os


class Player:
    def __init__(self, x, y, can_double_jump=False, player_id=1, image_path=None):
        # 基本属性
        self.rect = pygame.Rect(x, y, 50, 50)

        # 加载角色图片
        self.image = None
        if image_path and os.path.exists(image_path):
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (50, 50))
            except:
                self.image = None

        # 如果没有图片，使用颜色
        if not self.image:
            self.color = (0, 255, 0) if can_double_jump else (0, 0, 255)
        else:
            self.color = None

        # 物理属性
        self.velocity_y = 0
        self.on_ground = True
        self.jump_count = 0
        self.max_jump_count = 2 if can_double_jump else 1

        # 玩家类型
        self.can_double_jump = can_double_jump
        self.player_id = player_id

        # 跳跃参数
        self.jump_power = -12

    def jump(self):
        """执行跳跃"""
        if self.jump_count < self.max_jump_count:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.jump_count += 1

            # 如果是二段跳，给一个较小的速度
            if self.jump_count == 2 and self.can_double_jump:
                self.velocity_y = self.jump_power * 0.8

            return True
        return False

    def update(self):
        """更新玩家状态"""
        # 应用重力
        self.velocity_y += 0.5

        # 更新位置
        self.rect.y += self.velocity_y

        # 检测是否到达地面 (y=300)
        if self.rect.bottom >= 300:
            self.rect.bottom = 300
            self.velocity_y = 0
            self.on_ground = True
            self.jump_count = 0

    def reset_position(self, x, y):
        """重置玩家位置"""
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.on_ground = True
        self.jump_count = 0

    def draw(self, screen):
        """绘制玩家"""
        if self.image:
            # 绘制图片角色
            screen.blit(self.image, self.rect)
        else:
            # 绘制颜色方块角色
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        # 显示跳跃次数
        font = pygame.font.Font(None, 24)
        jump_text = f"跳跃: {self.jump_count}/{self.max_jump_count}"
        jump_surface = font.render(jump_text, True, (255, 255, 255))
        screen.blit(jump_surface, (self.rect.x, self.rect.y - 25))