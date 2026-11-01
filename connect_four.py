import math
import random
import pygame
import time

BG_COLOR = (44, 62, 80)
BOARD_COLOR = (41, 128, 185)
SLOT_COLOR = (30, 43, 56)

RED = (231, 76, 60)
RED_SHADOW = (192, 57, 43)

YELLOW = (241, 196, 15)
YELLOW_SHADOW = (243, 156, 18)

WHITE = (255, 255, 255)

SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)
MARGIN = 50

# toggle: True = minimax dengan alpha-beta pruning, False = minimax biasa
USE_ALPHA_BETA = True
AI_DEPTH = 5

class connect4:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.board = [[0 for i in range(cols)] for j in range (rows)]

    def draw_board(self, screen):
        PADDING = 20
        
        board_x = MARGIN - PADDING
        board_y = SQUARESIZE + MARGIN - PADDING
        board_w = self.cols * SQUARESIZE + (2 * PADDING)
        board_h = self.rows * SQUARESIZE + (2 * PADDING)
        
        board_rect = (board_x, board_y, board_w, board_h)
        pygame.draw.rect(screen, BOARD_COLOR, board_rect, border_radius=25)

        for i in range(self.cols):
            for j in range(self.rows):
                center_x = int(i * SQUARESIZE + MARGIN + SQUARESIZE / 2)
                center_y = int(j * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2 + MARGIN)

                if self.board[j][i] == 0:
                    pygame.draw.circle(screen, BG_COLOR, (center_x, center_y), RADIUS)
                    pygame.draw.circle(screen, SLOT_COLOR, (center_x, center_y), RADIUS, 4)
                
                elif self.board[j][i] == 1:
                    pygame.draw.circle(screen, RED_SHADOW, (center_x, center_y + 4), RADIUS) 
                    pygame.draw.circle(screen, RED, (center_x, center_y), RADIUS)
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), RADIUS - 6, 2)
                
                elif self.board[j][i] == 2:
                    pygame.draw.circle(screen, YELLOW_SHADOW, (center_x, center_y + 4), RADIUS)
                    pygame.draw.circle(screen, YELLOW, (center_x, center_y), RADIUS)
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), RADIUS - 6, 2)

        pygame.display.update()

    def is_full(self, col):
        return self.board[0][col] != 0 

    def get_valid_cols(self):
        valid_cols = []
        for i in range(self.cols):
            if not self.is_full(i):
                valid_cols.append(i)
        return valid_cols

    def get_lowest_empty_row(self, col):
        for i in range(self.rows - 1, -1, -1):
            if self.board[i][col] == 0:
                return i
        return None

    def drop_piece(self, board, col, piece):
        row = self.get_lowest_empty_row(col)
        if row is not None:
            board[row][col] = piece

    def check_win(self, board, piece):
        # horizontal
        for i in range(self.rows):
            for j in range(self.cols - 3):
                if all(board[i][j + k] == piece for k in range(4)):
                    return True
        # vertical    
        for i in range(self.rows - 3):
            for j in range(self.cols):
                if all(board[i + k][j] == piece for k in range(4)):
                    return True
        # diagonal pos
        for i in range(3, self.rows):
            for j in range(self.cols - 3):
                if all(board[i - k][j + k] == piece for k in range(4)):
                    return True
        # diagonal neg
        for i in range(self.rows - 3):
            for j in range(self.cols - 3):
                if all(board[i + k][j + k] == piece for k in range(4)):
                    return True

class human:
    def __init__(self, piece=1):
        self.piece = piece

class ai:
    def __init__(self, piece=2, player_piece=1, depth=3, use_pruning=True):
        self.use_pruning = use_pruning
        self.piece = piece
        self.enemy_piece = player_piece
        self.depth = depth
        self.nodes = 0
        self.history = []  # list of (jumlah_node, waktu) per langkah AI

    def check_window(self, window):
        score = 0
        piece_cnt = window.count(self.piece)
        empty_cnt = window.count(0)
        enemy_cnt = window.count(self.enemy_piece)

        if piece_cnt == 4:
            score += 100
        elif piece_cnt == 3 and empty_cnt == 1:
            score += 5
        elif piece_cnt == 2 and empty_cnt == 2:
            score += 2

        if enemy_cnt == 3 and empty_cnt == 1:
            score -= 4

        return score

    def score_pos(self, game):
        score = 0
        board = game.board

        center_arr = [board[i][game.cols//2] for i in range(game.rows)]
        score += center_arr.count(self.piece)*3 

        # horizontal
        for i in range(game.rows):
            for j in range(game.cols - 3):
                window = board[i][j:j+4]
                score += self.check_window(window)

        # vertical
        for i in range(game.rows - 3):
            for j in range(game.cols):
                window = [board[i+k][j] for k in range(4)]
                score += self.check_window(window)

        # diagonal
        for i in range(game.rows - 3):
            for j in range(game.cols - 3):
                window = [board[i+k][j+k] for k in range(4)]
                score += self.check_window(window)

                window_neg = [board[i+3-k][j+k] for k in range(4)]
                score += self.check_window(window_neg)

        return score

    def is_over(self, game):
        return game.check_win(game.board, self.piece) or game.check_win(game.board, self.enemy_piece) or len(game.get_valid_cols()) == 0

    def minimax(self, game, depth, alpha, beta, maximizing):
        pygame.event.pump()
        self.nodes += 1
        
        valid_cols = game.get_valid_cols()
        is_over = self.is_over(game)

        if maximizing:
            if depth == 0 or is_over:
                if is_over:
                    if game.check_win(game.board, self.piece):                    
                        return (None, 10000000 + depth) 
                    elif game.check_win(game.board, self.enemy_piece):
                        return (None, -10000000 - depth) 
                    else:
                        return (None, 0)
                else:
                    return (None, self.score_pos(game))

            value = -math.inf
            best_col = random.choice(valid_cols)

            for col in valid_cols:
                row = game.get_lowest_empty_row(col)

                game.board[row][col] = self.piece
                new_score = self.minimax(game, depth-1, alpha, beta, False)[1]
                game.board[row][col] = 0
                
                if new_score > value:
                    value = new_score
                    best_col = col
                alpha = max(alpha, value)
                if self.use_pruning and alpha >= beta:
                    break
            return best_col, value
            
        else:
            if depth == 0 or is_over:
                if is_over:
                    if game.check_win(game.board, self.piece):                    
                        return (None, 10000000 + depth) 
                    elif game.check_win(game.board, self.enemy_piece):
                        return (None, -10000000 - depth) 
                    else:
                        return (None, 0)
                else:
                    return (None, self.score_pos(game))
                    
            value = math.inf
            best_col = random.choice(valid_cols)
            
            for col in valid_cols:
                row = game.get_lowest_empty_row(col)

                game.board[row][col] = self.enemy_piece
                new_score = self.minimax(game, depth-1, alpha, beta, True)[1]
                game.board[row][col] = 0

                if new_score < value:
                    value = new_score
                    best_col = col
                beta = min(beta, value)
                if self.use_pruning and alpha >= beta:
                    break
            return best_col, value
        
    def get_best_move(self, game):
        self.nodes = 0
        start_time = time.time()
        col = self.minimax(game, self.depth, -math.inf, math.inf, True)[0]
        elapsed = time.time() - start_time

        self.history.append((self.nodes, elapsed))
        print(f"AI | kolom {col} | {self.nodes:>9} node | {elapsed:.4f} detik")
        return col

    def mode_name(self):
        return "alpha-beta" if self.use_pruning else "minimax biasa"

    def print_summary(self):
        if not self.history:
            return

        n = len(self.history)
        total_node = sum(h[0] for h in self.history)
        total_time = sum(h[1] for h in self.history)
        longest = max(h[1] for h in self.history)
        first_node, first_time = self.history[0]

        print()
        print("=" * 64)
        print(f"RINGKASAN | DEPTH = {self.depth} | {self.mode_name()}")
        print("=" * 64)
        print(f"Seluruh game ({n} langkah AI):")
        print(f"  total node       : {total_node:,}")
        print(f"  total waktu      : {total_time:.4f} detik")
        print(f"  rata2 node/langkah : {total_node // n}")
        print(f"  rata2 waktu/langkah: {total_time / n:.4f} detik")
        print(f"  langkah terlama  : {longest:.4f} detik")
        print("=" * 64)


pygame.init()

temp_game = connect4()
width = temp_game.cols * SQUARESIZE + 2 * MARGIN
height = (temp_game.rows + 1) * SQUARESIZE + 2 * MARGIN
size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect 4")

font_title = pygame.font.SysFont("monospace", 75, bold=True)
font_main = pygame.font.SysFont("monospace", 75)
font_sub = pygame.font.SysFont("monospace", 30)

state = "MENU"
gameover = False

while True:
    if state == "MENU":
        screen.fill(BG_COLOR)
        title = font_title.render("Connect 4", 1, BOARD_COLOR)
        screen.blit(title, (width/2 - title.get_width()/2, height/2 - title.get_height()/2 - 25))

        start = font_sub.render("Click to start", 1, RED)
        screen.blit(start, (width/2 - start.get_width()/2, height/2 - start.get_height()/2 + 25))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                game = connect4()
                player = human()
                enemy = ai(depth=AI_DEPTH, use_pruning=USE_ALPHA_BETA)
                turn = random.randint(1, 2)
                gameover = False
                state = "GAME"
                game.draw_board(screen)
                print(f"\nMulai game | depth={enemy.depth} | mode={enemy.mode_name()} | giliran awal: {'pemain' if turn == 1 else 'AI'}\n")

    elif state == "GAME":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEMOTION and turn == 1:
                pygame.draw.rect(screen, BG_COLOR, (0, 0, width, SQUARESIZE + MARGIN - 20))
                posx = event.pos[0]

                if posx < MARGIN + RADIUS:
                    posx = MARGIN + RADIUS
                elif posx > width - MARGIN - RADIUS:
                    posx = width - MARGIN - RADIUS

                hover_y = int(SQUARESIZE / 2 + 20)
                pygame.draw.circle(screen, RED_SHADOW, (posx, hover_y + 4), RADIUS)
                pygame.draw.circle(screen, RED, (posx, hover_y), RADIUS)
                pygame.draw.circle(screen, WHITE, (posx, hover_y), RADIUS - 6, 2)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and turn == 1:
                pygame.draw.rect(screen, BG_COLOR, (0, 0, width, SQUARESIZE + MARGIN - 20))
                posx = event.pos[0]
                col = int((posx - MARGIN) // SQUARESIZE)

                if 0 <= col < game.cols and not game.is_full(col):
                    game.drop_piece(game.board, col, player.piece)
                    game.draw_board(screen)

                    if game.check_win(game.board, player.piece):
                        label = font_main.render("You won!", 1, RED)
                        screen.blit(label, (screen.get_width()/2 - label.get_width()/2, 20))
                        pygame.display.update()
                        gameover = True
                    turn = 2

                    if len(game.get_valid_cols()) == 0:
                        label = font_main.render("Draw", 1, BOARD_COLOR)
                        screen.blit(label, (screen.get_width()/2 - label.get_width()/2, 20))
                        pygame.display.update()
                        gameover = True

        if turn == 2 and not gameover:
            col = enemy.get_best_move(game)

            if 0 <= col < game.cols and not game.is_full(col):
                game.drop_piece(game.board, col, enemy.piece)
                game.draw_board(screen)

                if game.check_win(game.board, enemy.piece):
                    label = font_main.render("AI won!", 1, YELLOW)
                    screen.blit(label, (screen.get_width()/2 - label.get_width()/2, 20))
                    pygame.display.update()
                    gameover = True
                turn = 1

                if len(game.get_valid_cols()) == 0:
                    label = font_main.render("Draw", 1, BOARD_COLOR)
                    screen.blit(label, (screen.get_width()/2 - label.get_width()/2, 20))
                    pygame.display.update()
                    gameover = True

        if gameover:
            enemy.print_summary()
            pygame.time.wait(2000)
            state = "GAMEOVER"

    elif state == "GAMEOVER":
        restart_text = font_sub.render("Click to go to menu", 1, BOARD_COLOR)
        pygame.draw.rect(screen, BG_COLOR, (width/2 - restart_text.get_width()/2 - 10, height/2 - restart_text.get_height()/2 - 10, restart_text.get_width() + 20, restart_text.get_height() + 20))
        screen.blit(restart_text, (width/2 - restart_text.get_width()/2, height/2 - restart_text.get_height()/2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                state = "MENU"