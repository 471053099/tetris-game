#!/usr/bin/env python3
"""俄罗斯方块 - Tetris"""

import pygame
import random
import sys

# 初始化 pygame
pygame.init()

# 常量
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + 200
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT + 60

# 颜色
COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
    'BG': (30, 30, 30),
    'GRID': (50, 50, 50),
    'TEXT': (255, 255, 255),
}

# 方块形状定义
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}

# 旋转后的形状
def rotate_piece(shape):
    return [list(row) for row in zip(*shape[::-1])]

# 创建新方块
def new_piece():
    piece_type = random.choice(list(SHAPES.keys()))
    shape = SHAPES[piece_type]
    return {
        'type': piece_type,
        'shape': shape,
        'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
        'y': 0,
        'color': COLORS[piece_type],
    }

# 碰撞检测
def check_collision(board, piece, dx=0, dy=0, shape=None):
    if shape is None:
        shape = piece['shape']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece['x'] + x + dx
                new_y = piece['y'] + y + dy
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                    return True
                if new_y >= 0 and board[new_y][new_x]:
                    return True
    return False

# 锁定方块到_board
def lock_piece(board, piece):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                board[piece['y'] + y][piece['x'] + x] = piece['color']

# 消除行
def clear_lines(board):
    lines_cleared = 0
    y = GRID_HEIGHT - 1
    while y >= 0:
        if all(board[y][x] for x in range(GRID_WIDTH)):
            del board[y]
            board.insert(0, [None] * GRID_WIDTH)
            lines_cleared += 1
        else:
            y -= 1
    return lines_cleared

# 主函数
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('俄罗斯方块 - Tetris')
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    # 初始化 board
    board = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    current_piece = new_piece()
    next_piece = new_piece()
    score = 0
    level = 1
    lines_cleared_total = 0
    game_over = False
    paused = False

    fall_time = 0
    fall_speed = 500  # 毫秒
    auto_repeat_delay = 100
    key_hold_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0, pygame.K_DOWN: 0}

    running = True
    while running:
        dt = clock.get_rawtime()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r and game_over:
                    board = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
                    current_piece = new_piece()
                    next_piece = new_piece()
                    score = 0
                    level = 1
                    lines_cleared_total = 0
                    game_over = False
                    fall_speed = 500
                if not game_over and not paused:
                    if event.key == pygame.K_UP:
                        rotated = rotate_piece(current_piece['shape'])
                        if not check_collision(board, current_piece, shape=rotated):
                            current_piece['shape'] = rotated
                    elif event.key == pygame.K_SPACE:
                        while not check_collision(board, current_piece, dy=1):
                            current_piece['y'] += 1
                        lock_piece(board, current_piece)
                        lines = clear_lines(board)
                        lines_cleared_total += lines
                        score += lines * 100 * level
                        level = lines_cleared_total // 10 + 1
                        fall_speed = max(50, 500 - (level - 1) * 30)
                        current_piece = next_piece
                        next_piece = new_piece()
                        if check_collision(board, current_piece):
                            game_over = True

        if not game_over and not paused:
            fall_time += dt
            if fall_time >= fall_speed:
                fall_time = 0
                if not check_collision(board, current_piece, dy=1):
                    current_piece['y'] += 1
                else:
                    lock_piece(board, current_piece)
                    lines = clear_lines(board)
                    lines_cleared_total += lines
                    score += lines * 100 * level
                    level = lines_cleared_total // 10 + 1
                    fall_speed = max(50, 500 - (level - 1) * 30)
                    current_piece = next_piece
                    next_piece = new_piece()
                    if check_collision(board, current_piece):
                        game_over = True

            # 键盘长按处理
            keys = pygame.key.get_pressed()
            now = pygame.time.get_ticks()
            for key, last_time in list(key_hold_time.items()):
                if keys[key]:
                    if last_time == 0:
                        key_hold_time[key] = now
                    elif now - last_time > auto_repeat_delay:
                        if key == pygame.K_LEFT and not check_collision(board, current_piece, dx=-1):
                            current_piece['x'] -= 1
                        elif key == pygame.K_RIGHT and not check_collision(board, current_piece, dx=1):
                            current_piece['x'] += 1
                        elif key == pygame.K_DOWN and not check_collision(board, current_piece, dy=1):
                            current_piece['y'] += 1
                        key_hold_time[key] = now - auto_repeat_delay + 50
                else:
                    key_hold_time[key] = 0

        # 绘制
        screen.fill(COLORS['BG'])

        # 绘制游戏区域背景
        game_rect = pygame.Rect(0, 0, BLOCK_SIZE * GRID_WIDTH, BLOCK_SIZE * GRID_HEIGHT)
        pygame.draw.rect(screen, COLORS['GRID'], game_rect)

        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, (70, 70, 70), 
                           (x * BLOCK_SIZE, 0), 
                           (x * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, (70, 70, 70), 
                           (0, y * BLOCK_SIZE), 
                           (GRID_WIDTH * BLOCK_SIZE, y * BLOCK_SIZE))

        # 绘制已固定的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if board[y][x]:
                    pygame.draw.rect(screen, board[y][x],
                                   (x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1,
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                    pygame.draw.rect(screen, (200, 200, 200),
                                   (x * BLOCK_SIZE + 1, y * BLOCK_SIZE + 1,
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2), 1)

        if not game_over:
            # 绘制当前方块
            for y, row in enumerate(current_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, current_piece['color'],
                                       ((current_piece['x'] + x) * BLOCK_SIZE + 1,
                                        (current_piece['y'] + y) * BLOCK_SIZE + 1,
                                        BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                # 绘制阴影
                shadow_y = current_piece['y']
                while not check_collision(board, current_piece, dy=shadow_y - current_piece['y'] + 1):
                    shadow_y += 1
                if shadow_y > current_piece['y']:
                    for y2, row2 in enumerate(current_piece['shape']):
                        for x2, cell2 in enumerate(row2):
                            if cell2:
                                pygame.draw.rect(screen, (80, 80, 80),
                                               ((current_piece['x'] + x2) * BLOCK_SIZE + 2,
                                                (shadow_y + y2) * BLOCK_SIZE + 2,
                                                BLOCK_SIZE - 4, BLOCK_SIZE - 4), 1)

        # 右侧信息面板
        panel_x = GRID_WIDTH * BLOCK_SIZE + 20
        
        # 下一个方块预览
        next_text = small_font.render('NEXT:', True, COLORS['TEXT'])
        screen.blit(next_text, (panel_x, 20))
        
        next_shape = next_piece['shape']
        for y, row in enumerate(next_shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, next_piece['color'],
                                   (panel_x + x * 25, 45 + y * 25, 23, 23))

        # 分数
        score_text = font.render('SCORE', True, COLORS['TEXT'])
        screen.blit(score_text, (panel_x, 140))
        score_value = small_font.render(str(score), True, (200, 200, 0))
        screen.blit(score_value, (panel_x, 170))

        # 等级
        level_text = font.render('LEVEL', True, COLORS['TEXT'])
        screen.blit(level_text, (panel_x, 220))
        level_value = small_font.render(str(level), True, (0, 200, 200))
        screen.blit(level_value, (panel_x, 250))

        # 游戏结束
        if game_over:
            go_text = font.render('GAME OVER', True, (255, 0, 0))
            screen.blit(go_text, (panel_x, 300))
            restart_text = small_font.render('Press R to restart', True, COLORS['TEXT'])
            screen.blit(restart_text, (panel_x, 340))

        # 提示
        tips = ['P: Pause', 'R: Restart', 'ESC: Quit']
        for i, tip in enumerate(tips):
            t = small_font.render(tip, True, (150, 150, 150))
            screen.blit(t, (panel_x, GRID_HEIGHT * BLOCK_SIZE - 80 + i * 22))

        if paused:
            pause_text = font.render('PAUSED', True, (255, 255, 0))
            pause_rect = pause_text.get_rect(center=(GRID_WIDTH * BLOCK_SIZE // 2, GRID_HEIGHT * BLOCK_SIZE // 2))
            pygame.draw.rect(screen, (0, 0, 0), pause_rect.inflate(20, 20))
            screen.blit(pause_text, pause_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()