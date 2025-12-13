# player.py
import pygame
import os


class Player:
    def __init__(self, x, y, can_double_jump=False, player_id=1, image_path=None):
        # ============ 修改：固定X坐标 ============
        self.fixed_x = 100  # 固定X坐标（与Game类中保持一致）
        self.rect = pygame.Rect(self.fixed_x, y, 50, 50)  # x使用固定值
        
        # ============ 新增：跑动动画相关 ============
        self.run_frames = []  # 跑动动画帧列表
        self.current_frame = 0  # 当前动画帧索引
        self.animation_timer = 0  # 动画计时器
        self.animation_speed = 0.15  # 动画播放速度（值越大越快）
        self.is_running = True  # 是否在跑动状态

        # 加载角色图片
        self.load_character_images(image_path)

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

        # ============ 新增：地面高度 ============
        self.ground_y = 450  # 地面高度（与Game类中的ground_y保持一致）

    def load_character_images(self, image_path):
        """加载角色图片和动画帧"""
        if image_path and os.path.exists(image_path):
            try:
                # 加载主图片
                main_image = pygame.image.load(image_path).convert_alpha()
                main_image = pygame.transform.scale(main_image, (50, 50))
                
                # ============ 新增：创建跑动动画帧 ============
                # 方法1：使用主图片创建简单动画帧
                self.create_simple_animation_frames(main_image)
                
            except Exception as e:
                print(f"加载角色图片失败: {e}")
                self.run_frames = []
        else:
            # 如果没有图片路径，创建默认动画帧
            self.create_default_animation_frames()

    def create_simple_animation_frames(self, base_image):
        """使用基础图片创建简单的跑动动画帧"""
        self.run_frames = []
        
        # 创建4个动画帧（模拟跑动）
        for i in range(4):
            # 创建一个新的Surface
            frame = pygame.Surface((50, 50), pygame.SRCALPHA)
            
            # 复制基础图片
            frame.blit(base_image, (0, 0))
            
            # 根据帧数轻微调整位置，模拟跑动
            if i == 0 or i == 2:
                # 中间位置
                pass
            elif i == 1:
                # 轻微向上（跳起状态）
                frame = pygame.transform.rotate(frame, 5)
            elif i == 3:
                # 轻微向下（落地状态）
                frame = pygame.transform.rotate(frame, -5)
            
            self.run_frames.append(frame)

    def jump(self):
        """执行跳跃"""
        if self.jump_count < self.max_jump_count:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.jump_count += 1

            # ============ 修改：跳跃时暂停跑动动画 ============
            self.is_running = False

            # 如果是二段跳，给一个较小的速度
            if self.jump_count == 2 and self.can_double_jump:
                self.velocity_y = self.jump_power * 0.8

                # ============ 新增：二段跳特殊效果 ============
                self.create_jump_particles()

            return True
        return False

    def create_default_animation_frames(self):
        """创建默认的跑动动画帧（没有图片时使用）"""
        self.run_frames = []
        
        # 定义不同帧的颜色
        if self.can_double_jump:
            colors = [
                (0, 180, 0),    # 深绿
                (0, 220, 0),    # 中绿
                (0, 255, 0),    # 亮绿
                (0, 220, 0),    # 中绿
            ]
        else:
            colors = [
                (0, 0, 180),    # 深蓝
                (0, 0, 220),    # 中蓝
                (0, 0, 255),    # 亮蓝
                (0, 0, 220),    # 中蓝
            ]
        
        # 创建4个动画帧
        for i, color in enumerate(colors):
            frame = pygame.Surface((50, 50), pygame.SRCALPHA)
            
            # 绘制身体
            pygame.draw.rect(frame, color, (10, 5, 30, 40), border_radius=5)
            
            # 绘制腿（模拟跑动动画）
            leg_offset = (i % 3) * 5  # 腿的位置偏移
            if i % 2 == 0:
                # 左腿在前
                pygame.draw.rect(frame, color, (15, 40, 8, 15 + leg_offset))
                pygame.draw.rect(frame, color, (27, 40, 8, 10 - leg_offset))
            else:
                # 右腿在前
                pygame.draw.rect(frame, color, (15, 40, 8, 10 - leg_offset))
                pygame.draw.rect(frame, color, (27, 40, 8, 15 + leg_offset))
            
            # 绘制眼睛
            pygame.draw.circle(frame, (255, 255, 255), (20, 20), 4)
            pygame.draw.circle(frame, (255, 255, 255), (30, 20), 4)
            pygame.draw.circle(frame, (0, 0, 0), (20, 20), 2)
            pygame.draw.circle(frame, (0, 0, 0), (30, 20), 2)
            self.run_frames.append(frame)
        
        self.current_image = self.run_frames[0]

    def update_animation(self):
        """更新跑动动画"""
        if not self.is_running or not self.on_ground:
            return
            
        # 更新动画计时器
        self.animation_timer += self.animation_speed
        
        # 切换到下一帧
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.run_frames)
            if self.run_frames:
                self.current_image = self.run_frames[self.current_frame]


    def update(self):
        """更新玩家状态"""
        # 应用重力
        self.velocity_y += 0.5

        # 更新位置
        self.rect.y += self.velocity_y

        # 检测是否到达地面 (y=400)
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.velocity_y = 0
            self.on_ground = True
            self.jump_count = 0

            # ============ 新增：落地后恢复跑动动画 ============
            self.is_running = True

            # ============ 新增：更新动画 ============
            self.update_animation()
                
            # ============ 重要：保持X坐标固定 ============
            self.rect.x = self.fixed_x



    def reset_position(self, x, y):
        """重置玩家位置"""
        # ============ 修改：X坐标保持固定，只更新Y坐标 ============
        self.rect.x = self.fixed_x  # 固定X坐标
        self.rect.y = y
        self.velocity_y = 0
        self.on_ground = True
        self.jump_count = 0
        self.is_running = True
        
        # ============ 新增：重置动画 ============
        self.current_frame = 0
        self.animation_timer = 0
        if self.run_frames:
            self.current_image = self.run_frames[0]

    def draw(self, screen):
        """绘制玩家"""
        if self.run_frames:
            # ============ 修改：绘制当前动画帧 ============
            screen.blit(self.current_image, self.rect)
        elif self.color:
            # 如果没有动画帧，使用颜色方块
            pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
            
            # 添加简单的眼睛
            pygame.draw.circle(screen, (255, 255, 255), 
                              (self.rect.x + 15, self.rect.y + 20), 4)
            pygame.draw.circle(screen, (255, 255, 255), 
                              (self.rect.x + 35, self.rect.y + 20), 4)

        # 显示跳跃次数（调试信息）
        font = pygame.font.Font(None, 24)
        jump_text = f"跳跃: {self.jump_count}/{self.max_jump_count}"
        jump_surface = font.render(jump_text, True, (255, 255, 255))
        screen.blit(jump_surface, (self.rect.x, self.rect.y - 25))
        
        # ============ 可选：绘制碰撞框（调试用） ============
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)

    # ============ 新增：设置地面高度的方法 ============
    def set_ground_y(self, ground_y):
        """设置地面高度（需要与Game类同步）"""
        self.ground_y = ground_y
