import pygame
import sys
# 初始化pygame
pygame.init()

# 设置屏幕大小
screen_size = (600, 600)
screen = pygame.display.set_mode(screen_size)

# 设置标题
pygame.display.set_caption("五子棋")

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
BOARD_COLOR = (222, 184, 135)  # 添加棋盘背景色

# 棋盘参数
BOARD_SIZE = 19
GRID_WIDTH = screen_size[0] // (BOARD_SIZE + 1)  # 修改以留出标记空间

def draw_board():
    # 填充棋盘背景
    screen.fill(BOARD_COLOR)
    
    # 画网格线
    for i in range(BOARD_SIZE):
        # 画横线
        pygame.draw.line(screen, BLACK, 
            (GRID_WIDTH, (i + 1) * GRID_WIDTH), 
            (BOARD_SIZE * GRID_WIDTH, (i + 1) * GRID_WIDTH))
        # 画竖线
        pygame.draw.line(screen, BLACK, 
            ((i + 1) * GRID_WIDTH, GRID_WIDTH), 
            ((i + 1) * GRID_WIDTH, BOARD_SIZE * GRID_WIDTH))
        
        # 添加坐标标记
        font = pygame.font.Font(None, 24)
        # 数字标记（1-19）
        num_text = font.render(str(i + 1), True, BLACK)
        screen.blit(num_text, (GRID_WIDTH * (i + 1) - 10, 5))
        # 字母标记（A-S）
        letter_text = font.render(chr(65 + i), True, BLACK)
        screen.blit(letter_text, (5, GRID_WIDTH * (i + 1) - 10))

def place_piece(x, y, color):
    """ 在指定位置放置棋子 """
    # 调整为交叉点位置
    center_x = (x + 1) * GRID_WIDTH
    center_y = (y + 1) * GRID_WIDTH
    # 绘制棋子阴影
    pygame.draw.circle(screen, GRAY, (center_x + 2, center_y + 2), GRID_WIDTH // 3)
    # 绘制棋子
    pygame.draw.circle(screen, color, (center_x, center_y), GRID_WIDTH // 3)

def get_grid_pos(mouse_x, mouse_y):
    """ 根据鼠标坐标获取网格位置 """
    # 计算最近的交叉点
    x = round((mouse_x - GRID_WIDTH) / GRID_WIDTH)
    y = round((mouse_y - GRID_WIDTH) / GRID_WIDTH)
    if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
        return x, y
    return None

def check_win(board, x, y, color):
    """检查是否获胜，返回获胜的棋子位置列表"""
    directions = [
        [(0, 1), (0, -1)],    # 垂直方向
        [(1, 0), (-1, 0)],    # 水平方向
        [(1, 1), (-1, -1)],   # 主对角线
        [(1, -1), (-1, 1)]    # 副对角线
    ]
    
    for dir_pair in directions:
        winning_pieces = [(x, y)]  # 包含当前落子位置
        for dx, dy in dir_pair:  # 检查每个方向
            temp_x, temp_y = x, y
            # 向该方向延伸检查
            for _ in range(4):  # 最多延伸4步
                temp_x += dx
                temp_y += dy
                if (0 <= temp_x < BOARD_SIZE and 
                    0 <= temp_y < BOARD_SIZE and 
                    board[temp_y][temp_x] == color):
                    winning_pieces.append((temp_x, temp_y))
                else:
                    break
        if len(winning_pieces) >= 5:
            return True, winning_pieces[:5]  # 只返回5个连珠的位置
    return False, []

def highlight_winning_pieces(winning_pieces, color):
    """高亮显示获胜的五个棋子"""
    for x, y in winning_pieces:
        center_x = (x + 1) * GRID_WIDTH
        center_y = (y + 1) * GRID_WIDTH
        # 绘制红色边框
        pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 
                         GRID_WIDTH // 3 + 2, 2)

def find_chinese_font():
    """查找系统中支持中文的字体（优化版）"""
    print("正在检测系统支持的中文字体...")
    
    # 优先检测常见的中文字体
    priority_fonts = [
        "simhei", "simsun", "nsimsun", "microsoftyahei", "microsoftyaheibold",
        "stkaiti", "stheiti", "stxihei", "stfangsong", "fzshuti", "fzyaoti",
        "arplumingcn", "arplumingtcn", "nanumgothic", "malgungothic", "msgothic",
        "sourcehansans", "notosanscjk", "dengxian", "fangsong", "kaiti", "stsongsuti"
    ]
    
    # 先检测优先字体
    for font_name in priority_fonts:
        try:
            test_font = pygame.font.SysFont(font_name, 24)
            test_surface = test_font.render("中", True, (0, 0, 0))
            if test_surface.get_width() > 10:
                print(f"找到支持中文的字体: {font_name}")
                return font_name
        except:
            pass
    
    # 如果优先字体都不支持中文，检测系统其他字体
    available_fonts = pygame.font.get_fonts()
    for font_name in available_fonts:
        # 跳过已检测的优先字体
        if font_name.lower() in priority_fonts:
            continue
            
        try:
            test_font = pygame.font.SysFont(font_name, 24)
            test_surface = test_font.render("中", True, (0, 0, 0))
            if test_surface.get_width() > 10:
                print(f"找到支持中文的字体: {font_name}")
                return font_name
        except:
            pass
    
    print("未找到支持中文的字体")
    return None

def reset_game():
    """重置游戏状态"""
    # 创建空棋盘
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    # 黑方先手
    current_color = BLACK
    # 重置游戏状态
    game_over = False
    winning_pieces = []
    return board, current_color, game_over, winning_pieces

def draw_popup(screen, message, sub_message, font, small_font, position=None):
    """绘制弹出窗口，返回窗口矩形区域"""
    # 创建半透明背景
    popup_width, popup_height = 400, 200
    popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
    popup_surface.fill((0, 0, 0, 180))  # 黑色半透明背景
    
    # 绘制边框
    pygame.draw.rect(popup_surface, (255, 255, 255), 
                    (0, 0, popup_width, popup_height), 2)
    
    # 绘制主要信息
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(popup_width//2, popup_height//2 - 30))
    popup_surface.blit(text, text_rect)
    
    # 绘制次要信息
    sub_text = small_font.render(sub_message, True, (200, 200, 255))
    sub_text_rect = sub_text.get_rect(center=(popup_width//2, popup_height//2 + 30))
    popup_surface.blit(sub_text, sub_text_rect)
    
    # 添加拖动提示
    drag_text = small_font.render("(可拖动)", True, (150, 150, 150))
    drag_rect = drag_text.get_rect(center=(popup_width//2, popup_height - 20))
    popup_surface.blit(drag_text, drag_rect)
    
    # 设置弹窗位置
    if position:
        popup_rect = popup_surface.get_rect(topleft=position)
    else:
        popup_rect = popup_surface.get_rect(center=(screen_size[0]//2, screen_size[1]//2))
    
    screen.blit(popup_surface, popup_rect)
    return popup_rect

def main():
    running = True
    # 初始化游戏状态
    board, current_color, game_over, winning_pieces = reset_game()
    
    # 弹窗相关变量
    popup_rect = None
    popup_position = None
    dragging_popup = False
    drag_offset = (0, 0)
    
    # 查找并加载支持中文的字体
    chinese_font = find_chinese_font()
    
    if chinese_font:
        # 使用找到的支持中文的字体
        font = pygame.font.SysFont(chinese_font, 74)
        small_font = pygame.font.SysFont(chinese_font, 36)  # 添加小号字体用于提示
        use_chinese = True
    else:
        # 如果没有找到支持中文的字体，使用默认字体并显示英文
        font = pygame.font.Font(None, 74)
        small_font = pygame.font.Font(None, 36)
        use_chinese = False
        print("将使用英文显示")
    
    # 根据字体支持情况选择语言
    if use_chinese:
        winner_text = lambda color: "黑方获胜!" if color == BLACK else "白方获胜!"
        restart_text = "按空格键开始新游戏"
    else:
        winner_text = lambda color: "Black Wins!" if color == BLACK else "White Wins!"
        restart_text = "Press SPACE to start a new game"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # 检测空格键按下事件
                if event.key == pygame.K_SPACE and game_over:
                    # 重置游戏
                    board, current_color, game_over, winning_pieces = reset_game()
                    popup_rect = None
                    popup_position = None
                    dragging_popup = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over and popup_rect and popup_rect.collidepoint(event.pos):
                    # 开始拖拽弹窗
                    dragging_popup = True
                    mouse_x, mouse_y = event.pos
                    drag_offset = (mouse_x - popup_rect.x, mouse_y - popup_rect.y)
                elif not game_over:  # 只有在游戏未结束时才能落子
                    mouse_x, mouse_y = event.pos
                    grid_pos = get_grid_pos(mouse_x, mouse_y)
                    
                    if grid_pos:
                        grid_x, grid_y = grid_pos
                        if board[grid_y][grid_x] is None:
                            place_piece(grid_x, grid_y, current_color)
                            board[grid_y][grid_x] = current_color
                            
                            has_won, win_pieces = check_win(board, grid_x, grid_y, current_color)
                            if has_won:
                                game_over = True
                                winning_pieces = win_pieces
                            else:
                                current_color = WHITE if current_color == BLACK else BLACK
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # 结束拖拽
                dragging_popup = False
            elif event.type == pygame.MOUSEMOTION:
                # 拖拽弹窗
                if dragging_popup:
                    mouse_x, mouse_y = event.pos
                    popup_position = (mouse_x - drag_offset[0], mouse_y - drag_offset[1])
        
        # 更新屏幕
        draw_board()
        # 重绘所有已放置的棋子
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if board[y][x]:
                    place_piece(x, y, board[y][x])
        
        # 如果游戏结束，高亮显示获胜棋子并显示弹窗
        if game_over and winning_pieces:
            highlight_winning_pieces(winning_pieces, current_color)
            # 显示弹出窗口
            popup_rect = draw_popup(screen, winner_text(current_color), restart_text, 
                                   font, small_font, popup_position)
        
        pygame.display.flip()

if __name__ == "__main__":
    main()        