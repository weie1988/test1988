import pygame
import sys
import random
import time
import os
from pygame import mixer

# 初始化Pygame
pygame.init()
mixer.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 方块形状和颜色
SHAPES = {
    'I': [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)]
    ],
    'O': [
        [(0, 0), (1, 0), (0, 1), (1, 1)]
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)]
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)]
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)]
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)]
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)]
    ]
}

SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': MAGENTA,
    'L': ORANGE,
    'J': BLUE,
    'S': GREEN,
    'Z': RED
}

# 游戏状态
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 加载字体
try:
    font_path = os.path.join('assets', 'fonts', 'arial.ttf')
    if not os.path.exists(font_path):
        font = pygame.font.SysFont('arial', 24)
        large_font = pygame.font.SysFont('arial', 48)
    else:
        font = pygame.font.Font(font_path, 24)
        large_font = pygame.font.Font(font_path, 48)
except:
    font = pygame.font.SysFont('arial', 24)
    large_font = pygame.font.SysFont('arial', 48)

# 加载音效
try:
    pygame.mixer.music.load(os.path.join('assets', 'sounds', 'background.mp3'))
    clear_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'clear.wav'))
    game_over_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'gameover.wav'))
    rotate_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'rotate.wav'))
    drop_sound = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'drop.wav'))
except:
    # 如果音效文件不存在，创建空的音效对象
    clear_sound = pygame.mixer.Sound(pygame.mixer.Sound(bytes(0)))
    game_over_sound = pygame.mixer.Sound(pygame.mixer.Sound(bytes(0)))
    rotate_sound = pygame.mixer.Sound(pygame.mixer.Sound(bytes(0)))
    drop_sound = pygame.mixer.Sound(pygame.mixer.Sound(bytes(0)))

# 游戏类
class Tetris:
    def __init__(self):
        self.reset_game()
        self.high_scores = self.load_high_scores()
        self.game_state = GameState.MENU
        self.sound_enabled = True
        
    def reset_game(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 0.5  # 初始下落速度（秒）
        
    def new_piece(self):
        shape = random.choice(list(SHAPES.keys()))
        return {
            'shape': shape,
            'rotation': 0,
            'x': GRID_WIDTH // 2 - 2,
            'y': 0
        }
        
    def get_piece_positions(self, piece=None):
        if piece is None:
            piece = self.current_piece
        shape_name = piece['shape']
        rotation = piece['rotation']
        shape = SHAPES[shape_name][rotation % len(SHAPES[shape_name])]
        return [(piece['x'] + x, piece['y'] + y) for x, y in shape]
        
    def is_valid_position(self, piece=None):
        positions = self.get_piece_positions(piece)
        for x, y in positions:
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.board[y][x]:
                return False
        return True
        
    def merge_piece(self):
        positions = self.get_piece_positions()
        for x, y in positions:
            if y >= 0:
                self.board[y][x] = self.current_piece['shape']
                
    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.board[y]):
                lines_to_clear.append(y)
                
        if lines_to_clear:
            if self.sound_enabled:
                clear_sound.play()
                
            # 计算分数
            if len(lines_to_clear) == 1:
                self.score += 100 * self.level
            elif len(lines_to_clear) == 2:
                self.score += 300 * self.level
            elif len(lines_to_clear) == 3:
                self.score += 500 * self.level
            elif len(lines_to_clear) == 4:
                self.score += 800 * self.level
                
            self.lines_cleared += len(lines_to_clear)
            
            # 更新等级
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
            
            # 清除行并下移
            for line in sorted(lines_to_clear):
                del self.board[line]
                self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
                
    def move(self, dx, dy):
        new_piece = self.current_piece.copy()
        new_piece['x'] += dx
        new_piece['y'] += dy
        
        if self.is_valid_position(new_piece):
            self.current_piece = new_piece
            return True
        return False
        
    def rotate(self):
        new_piece = self.current_piece.copy()
        new_piece['rotation'] = (new_piece['rotation'] + 1) % len(SHAPES[new_piece['shape']])
        
        # 尝试旋转，如果不行则尝试墙踢
        if self.is_valid_position(new_piece):
            self.current_piece = new_piece
            if self.sound_enabled:
                rotate_sound.play()
            return True
            
        # 尝试墙踢（左右移动以适应旋转）
        for dx in [-1, 1, -2, 2]:
            kicked_piece = new_piece.copy()
            kicked_piece['x'] += dx
            if self.is_valid_position(kicked_piece):
                self.current_piece = kicked_piece
                if self.sound_enabled:
                    rotate_sound.play()
                return True
                
        return False
        
    def drop(self):
        if not self.move(0, 1):
            self.merge_piece()
            if self.sound_enabled:
                drop_sound.play()
            self.clear_lines()
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            
            # 检查游戏是否结束
            if not self.is_valid_position():
                self.game_over = True
                self.game_state = GameState.GAME_OVER
                if self.sound_enabled:
                    game_over_sound.play()
                self.update_high_scores()
                
    def hard_drop(self):
        while self.move(0, 1):
            pass
        self.drop()
        
    def update_high_scores(self):
        self.high_scores.append(self.score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:5]  # 只保留前5名
        self.save_high_scores()
        
    def load_high_scores(self):
        try:
            with open('high_scores.txt', 'r') as f:
                return [int(line.strip()) for line in f.readlines()]
        except:
            return []
            
    def save_high_scores(self):
        with open('high_scores.txt', 'w') as f:
            for score in self.high_scores:
                f.write(f"{score}\n")
                
    def draw_board(self):
        # 绘制游戏区域背景
        pygame.draw.rect(screen, BLACK, (0, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
        pygame.draw.rect(screen, WHITE, (0, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE), 2)
        
        # 绘制网格线
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
                
        # 绘制已放置的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    pygame.draw.rect(screen, SHAPE_COLORS[self.board[y][x]], 
                                    (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(screen, WHITE, 
                                    (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
                                    
        # 绘制当前方块
        if not self.game_over:
            positions = self.get_piece_positions()
            for x, y in positions:
                if y >= 0:  # 只绘制在游戏区域内的部分
                    pygame.draw.rect(screen, SHAPE_COLORS[self.current_piece['shape']], 
                                    (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(screen, WHITE, 
                                    (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
                                    
    def draw_sidebar(self):
        sidebar_x = GRID_WIDTH * GRID_SIZE + 10
        
        # 绘制侧边栏背景
        pygame.draw.rect(screen, BLACK, (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        
        # 绘制下一个方块预览
        preview_text = font.render("下一个方块:", True, WHITE)
        screen.blit(preview_text, (sidebar_x + 10, 20))
        
        preview_x = sidebar_x + SIDEBAR_WIDTH // 2 - GRID_SIZE * 2
        preview_y = 60
        
        # 获取下一个方块的形状
        shape_name = self.next_piece['shape']
        shape = SHAPES[shape_name][0]  # 使用第一个旋转状态
        
        # 绘制预览方块
        for x, y in shape:
            pygame.draw.rect(screen, SHAPE_COLORS[shape_name], 
                            (preview_x + x * GRID_SIZE, preview_y + y * GRID_SIZE, 
                            GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, WHITE, 
                            (preview_x + x * GRID_SIZE, preview_y + y * GRID_SIZE, 
                            GRID_SIZE, GRID_SIZE), 1)
                            
        # 绘制分数
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (sidebar_x + 10, 150))
        
        # 绘制等级
        level_text = font.render(f"等级: {self.level}", True, WHITE)
        screen.blit(level_text, (sidebar_x + 10, 180))
        
        # 绘制已消除行数
        lines_text = font.render(f"已消除行数: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (sidebar_x + 10, 210))
        
        # 绘制控制提示
        controls_y = 280
        controls = [
            "控制:",
            "← → : 左右移动",
            "↑ : 旋转",
            "↓ : 加速下落",
            "空格 : 硬下落",
            "P : 暂停游戏",
            "M : 静音/取消静音"
        ]
        
        for i, text in enumerate(controls):
            control_text = font.render(text, True, WHITE)
            screen.blit(control_text, (sidebar_x + 10, controls_y + i * 30))
            
    def draw_menu(self):
        screen.fill(BLACK)
        
        # 绘制游戏标题
        title_text = large_font.render("俄罗斯方块", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        # 绘制菜单选项
        menu_items = [
            "开始游戏",
            "排行榜",
            "退出游戏"
        ]
        
        for i, item in enumerate(menu_items):
            item_text = font.render(item, True, WHITE)
            item_rect = item_text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 50))
            pygame.draw.rect(screen, BLUE, (item_rect.x - 10, item_rect.y - 10, 
                                          item_rect.width + 20, item_rect.height + 20))
            screen.blit(item_text, item_rect)
            
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_text = large_font.render("游戏结束", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(game_over_text, game_over_rect)
        
        score_text = font.render(f"最终分数: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        screen.blit(score_text, score_rect)
        
        # 显示排行榜
        high_score_text = font.render("最高分:", True, YELLOW)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, 330))
        screen.blit(high_score_text, high_score_rect)
        
        for i, score in enumerate(self.high_scores[:5]):
            text = font.render(f"{i+1}. {score}", True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 370 + i * 30))
            screen.blit(text, rect)
            
        # 绘制按钮
        restart_text = font.render("重新开始", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        pygame.draw.rect(screen, GREEN, (restart_rect.x - 10, restart_rect.y - 10, 
                                       restart_rect.width + 20, restart_rect.height + 20))
        screen.blit(restart_text, restart_rect)
        
        menu_text = font.render("返回主菜单", True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 600))
        pygame.draw.rect(screen, BLUE, (menu_rect.x - 10, menu_rect.y - 10, 
                                      menu_rect.width + 20, menu_rect.height + 20))
        screen.blit(menu_text, menu_rect)
        
        return restart_rect, menu_rect
        
    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        pause_text = large_font.render("游戏暂停", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(pause_text, pause_rect)
        
        resume_text = font.render("按 P 继续游戏", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        screen.blit(resume_text, resume_rect)
        
        menu_text = font.render("返回主菜单", True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        pygame.draw.rect(screen, BLUE, (menu_rect.x - 10, menu_rect.y - 10, 
                                      menu_rect.width + 20, menu_rect.height + 20))
        screen.blit(menu_text, menu_rect)
        
        return menu_rect
        
    def draw_high_scores(self):
        screen.fill(BLACK)
        
        title_text = large_font.render("排行榜", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)
        
        if not self.high_scores:
            no_scores_text = font.render("暂无记录", True, WHITE)
            no_scores_rect = no_scores_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
            screen.blit(no_scores_text, no_scores_rect)
        else:
            for i, score in enumerate(self.high_scores):
                score_text = font.render(f"{i+1}. {score}", True, WHITE)
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 180 + i * 40))
                screen.blit(score_text, score_rect)
                
        back_text = font.render("返回", True, WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        pygame.draw.rect(screen, BLUE, (back_rect.x - 10, back_rect.y - 10, 
                                      back_rect.width + 20, back_rect.height + 20))
        screen.blit(back_text, back_rect)
        
        return back_rect
        
    def handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查是否点击了"开始游戏"按钮
            start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 290, 200, 40)
            if start_rect.collidepoint(mouse_pos):
                self.reset_game()
                self.game_state = GameState.PLAYING
                if self.sound_enabled:
                    try:
                        pygame.mixer.music.play(-1)  # 循环播放背景音乐
                    except:
                        pass
                        
            # 检查是否点击了"排行榜"按钮
            high_scores_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 340, 200, 40)
            if high_scores_rect.collidepoint(mouse_pos):
                self.showing_high_scores = True
                
            # 检查是否点击了"退出游戏"按钮
            exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 390, 200, 40)
            if exit_rect.collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()
                
    def handle_high_scores_events(self, event, back_rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if back_rect.collidepoint(mouse_pos):
                self.showing_high_scores = False
                
    def handle_game_over_events(self, event, restart_rect, menu_rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if restart_rect.collidepoint(mouse_pos):
                self.reset_game()
                self.game_state = GameState.PLAYING
                if self.sound_enabled:
                    try:
                        pygame.mixer.music.play(-1)
                    except:
                        pass
                        
            elif menu_rect.collidepoint(mouse_pos):
                self.game_state = GameState.MENU
                
    def handle_pause_events(self, event, menu_rect):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.game_state = GameState.PLAYING
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if menu_rect.collidepoint(mouse_pos):
                self.game_state = GameState.MENU
                
    def handle_playing_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.move(1, 0)
            elif event.key == pygame.K_DOWN:
                self.move(0, 1)
            elif event.key == pygame.K_UP:
                self.rotate()
            elif event.key == pygame.K_SPACE:
                self.hard_drop()
            elif event.key == pygame.K_p:
                self.game_state = GameState.PAUSED
            elif event.key == pygame.K_m:
                self.sound_enabled = not self.sound_enabled
                if self.sound_enabled:
                    try:
                        pygame.mixer.music.play(-1)
                    except:
                        pass
                else:
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass

# 主游戏循环
def main():
    game = Tetris()
    clock = pygame.time.Clock()
    last_fall_time = time.time()
    game.showing_high_scores = False
    
    # 尝试播放背景音乐
    try:
        pygame.mixer.music.play(-1)
    except:
        pass
        
    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if game.game_state == GameState.MENU:
                if game.showing_high_scores:
                    back_rect = game.draw_high_scores()
                    game.handle_high_scores_events(event, back_rect)
                else:
                    game.handle_menu_events(event)
                    
            elif game.game_state == GameState.PLAYING:
                game.handle_playing_events(event)
                
            elif game.game_state == GameState.PAUSED:
                menu_rect = game.draw_pause_screen()
                game.handle_pause_events(event, menu_rect)
                
            elif game.game_state == GameState.GAME_OVER:
                restart_rect, menu_rect = game.draw_game_over()
                game.handle_game_over_events(event, restart_rect, menu_rect)
                
        # 游戏逻辑更新
        if game.game_state == GameState.PLAYING:
            current_time = time.time()
            if current_time - last_fall_time > game.fall_speed:
                game.drop()
                last_fall_time = current_time
                
        # 绘制
        screen.fill(BLACK)
        
        if game.game_state == GameState.MENU:
            if game.showing_high_scores:
                game.draw_high_scores()
            else:
                game.draw_menu()
                
        elif game.game_state == GameState.PLAYING or game.game_state == GameState.PAUSED:
            game.draw_board()
            game.draw_sidebar()
            
            if game.game_state == GameState.PAUSED:
                game.draw_pause_screen()
                
        elif game.game_state == GameState.GAME_OVER:
            game.draw_board()
            game.draw_sidebar()
            game.draw_game_over()
            
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 