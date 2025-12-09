# game_settings.py

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_Y = 300  # 地面Y坐标

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BACKGROUND_COLOR = (240, 240, 240)
MENU_BG_COLOR = (50, 50, 80)  # 菜单背景色
BUTTON_COLOR = (70, 130, 180)  # 按钮颜色
BUTTON_HOVER_COLOR = (100, 160, 210)  # 按钮悬停颜色

# 游戏参数
FPS = 60
BACKGROUND_SPEED = 10  # 背景速度，现在障碍物也使用这个速度
GRAVITY = 0.5  # 重力加速度
JUMP_POWER = -12  # 跳跃初速度

# 障碍物参数
OBSTACLE_MIN_SPACING = 400  # 障碍物之间的最小间隔
OBSTACLE_MIN_WIDTH = 25     # 障碍物最小宽度
OBSTACLE_MAX_WIDTH = 40     # 障碍物最大宽度
OBSTACLE_MIN_HEIGHT = 25    # 障碍物最小高度
OBSTACLE_MAX_HEIGHT = 40    # 障碍物最大高度

# 角色图片路径（你可以替换为你自己的图片路径）
PLAYER1_IMAGE_PATH = "player1.png"  # 角色1图片路径
PLAYER2_IMAGE_PATH = "player2.png"  # 角色2图片路径

# 游戏状态
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_CHARACTER_SELECT = "character_select"