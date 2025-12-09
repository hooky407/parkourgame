# ui_components.py
import pygame


class Button:
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.normal_color = (70, 130, 180)  # 钢蓝色
        self.hover_color = (100, 160, 210)  # 浅钢蓝色
        self.text_color = (255, 255, 255)
        self.current_color = self.normal_color
        self.is_hovered = False

    def draw(self, screen):
        """绘制按钮"""
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)

        # 绘制文本
        self.font = pygame.font.Font('image/STKAITI.TTF', 48)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        """更新按钮状态"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.is_hovered else self.normal_color
        return self.is_hovered

    def is_clicked(self, mouse_pos, mouse_clicked):
        """检查按钮是否被点击"""
        return self.rect.collidepoint(mouse_pos) and mouse_clicked


class CharacterCard:
    def __init__(self, x, y, width, height, player_id, can_double_jump, image_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.player_id = player_id
        self.can_double_jump = can_double_jump
        self.selected = False
        self.font = pygame.font.Font(None, 28)

        # 加载角色图片
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                # 调整图片大小
                self.image = pygame.transform.scale(self.image, (80, 80))
            except:
                print(f"无法加载角色图片: {image_path}")
                self.image = None

        # 如果没有图片，创建颜色方块
        if not self.image:
            self.color = (0, 255, 0) if can_double_jump else (0, 0, 255)
        else:
            self.color = None

        # 卡片颜色
        self.normal_color = (80, 80, 120)
        self.selected_color = (120, 120, 180)
        self.border_color = (200, 200, 255)

    def draw(self, screen):
        """绘制角色卡片"""
        # 绘制卡片背景
        card_color = self.selected_color if self.selected else self.normal_color
        pygame.draw.rect(screen, card_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, self.border_color, self.rect, 3, border_radius=10)

        # 绘制角色图片或颜色方块
        if self.image:
            image_rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery - 20))
            screen.blit(self.image, image_rect)
        else:
            square_rect = pygame.Rect(0, 0, 60, 60)
            square_rect.center = (self.rect.centerx, self.rect.centery - 20)
            pygame.draw.rect(screen, self.color, square_rect)
            pygame.draw.rect(screen, (255, 255, 255), square_rect, 2)

        # 绘制角色信息
        player_type = "二段跳角色" if self.can_double_jump else "单段跳角色"
        player_text = f"角色 {self.player_id}"
        type_text = f"({player_type})"

        player_surface = self.font.render(player_text, True, (255, 255, 255))
        type_surface = self.font.render(type_text, True, (255, 255, 200))

        player_rect = player_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 40))
        type_rect = type_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 15))

        screen.blit(player_surface, player_rect)
        screen.blit(type_surface, type_rect)

    def update(self, mouse_pos, mouse_clicked):
        """更新卡片状态"""
        if self.rect.collidepoint(mouse_pos) and mouse_clicked:
            self.selected = True
            return True
        return False