import pygame
import chess
import random
import sys

BOARD_SIZE = 640
STATUS_HEIGHT = 60
WIDTH, HEIGHT = BOARD_SIZE, BOARD_SIZE + STATUS_HEIGHT
SQUARE_SIZE = BOARD_SIZE // 8
FPS = 60

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
SELECT = (186, 202, 68)
LEGAL_MOVE_DOT = (50, 150, 50)
WHITE_PIECE_COLOR = (245, 245, 245)
BLACK_PIECE_COLOR = (30, 30, 30)
TEXT_COLOR = (10, 10, 10)
CHECK_COLOR = (200, 50, 50)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Milestone 1 - Chess (Human vs Random AI)")
clock = pygame.time.Clock()

# Fonts
STATUS_FONT = pygame.font.SysFont(None, 22)
PIECE_FONT = pygame.font.SysFont(None, 36, bold=True)

# Game state
board = chess.Board()
selected_square = None
legal_moves = []
ai_thinking = False
ai_delay_ms = 400  
ai_move_time = 0

# Utility: square -> top-left pixel coords (a8 top-left)
def square_coords(square):
    file = chess.square_file(square)    # 0..7 for a..h
    rank = chess.square_rank(square)    # 0..7 for 1..8
    x = file * SQUARE_SIZE
    y = (7 - rank) * SQUARE_SIZE
    return x, y

def draw_board():
    # Draw squares
    for r in range(8):
        for c in range(8):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    # Highlight selected square
    if selected_square is not None:
        sx, sy = square_coords(selected_square)
        pygame.draw.rect(screen, SELECT, (sx, sy, SQUARE_SIZE, SQUARE_SIZE), 0)
    # Highlight king if in check
    if board.is_check():
        king_sq = board.king(board.turn)
        if king_sq is not None:
            kx, ky = square_coords(king_sq)
            pygame.draw.rect(screen, CHECK_COLOR, (kx, ky, SQUARE_SIZE, SQUARE_SIZE), 4)

def draw_pieces():
    # Draw pieces as circles with letter inside 
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if not piece:
            continue
        x, y = square_coords(sq)
        cx = x + SQUARE_SIZE // 2
        cy = y + SQUARE_SIZE // 2
        radius = SQUARE_SIZE // 2 - 8
        if piece.color == chess.WHITE:
            pygame.draw.circle(screen, WHITE_PIECE_COLOR, (cx, cy), radius)
            pygame.draw.circle(screen, TEXT_COLOR, (cx, cy), radius, 2)
            text = piece.symbol().upper()    # 'P','N','B','R','Q','K'
            text_surf = PIECE_FONT.render(text, True, TEXT_COLOR)
        else:
            pygame.draw.circle(screen, BLACK_PIECE_COLOR, (cx, cy), radius)
            pygame.draw.circle(screen, TEXT_COLOR, (cx, cy), radius, 2)
            text = piece.symbol().lower()    # 'p','n','b','r','q','k'
            text_surf = PIECE_FONT.render(text, True, WHITE_PIECE_COLOR)
        rect = text_surf.get_rect(center=(cx, cy))
        screen.blit(text_surf, rect)

def draw_legal_moves():
    for dest in legal_moves:
        x, y = square_coords(dest)
        cx = x + SQUARE_SIZE//2
        cy = y + SQUARE_SIZE//2
        # If there's an enemy piece there, show red capture ring
        target_piece = board.piece_at(dest)
        if target_piece is not None and target_piece.color != board.turn:
            pygame.draw.circle(screen, (200, 50, 50), (cx, cy), SQUARE_SIZE//2 - 6, 4)
        else:
            pygame.draw.circle(screen, LEGAL_MOVE_DOT, (cx, cy), 8)


def get_square_under_mouse(pos):
    mx, my = pos
    if mx < 0 or mx >= BOARD_SIZE or my < 0 or my >= BOARD_SIZE:
        return None
    col = mx // SQUARE_SIZE
    row = my // SQUARE_SIZE
    rank = 7 - row
    return chess.square(col, rank)

def ai_random_move():
    global ai_thinking
    moves = list(board.legal_moves)
    if not moves:
        ai_thinking = False
        return
    mv = random.choice(moves)

    if board.piece_type_at(mv.from_square) == chess.PAWN and chess.square_rank(mv.to_square) in (0, 7) and mv.promotion is None:
        mv = chess.Move(mv.from_square, mv.to_square, promotion=chess.QUEEN)
    board.push(mv)
    ai_thinking = False

def draw_status():
   
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        status = f"Checkmate! Winner: {winner}  —  Press R to restart"
    elif board.is_stalemate():
        status = "Stalemate (Draw)  —  Press R to restart"
    elif board.is_insufficient_material():
        status = "Draw (Insufficient material)  —  Press R to restart"
    elif board.is_game_over():
        status = f"Game over: {board.result()}  —  Press R to restart"
    else:
        status = ("White to move" if board.turn == chess.WHITE else "Black to move (AI)") + "  —  Press R to restart"
        if board.is_check():
            status += "  —  Check!"
    s = STATUS_FONT.render(status, True, TEXT_COLOR)

    pygame.draw.rect(screen, (230,230,230), (0, BOARD_SIZE, WIDTH, STATUS_HEIGHT))
    screen.blit(s, (10, BOARD_SIZE + 18))

def reset_game():
    global board, selected_square, legal_moves, ai_thinking
    board = chess.Board()
    selected_square = None
    legal_moves = []
    ai_thinking = False

# main loop
running = True
selected_square = None
legal_moves = []
ai_thinking = False
ai_move_time = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()

        elif event.type == pygame.MOUSEBUTTONDOWN and not ai_thinking:
        
            if board.turn != chess.WHITE:
                continue
            pos = pygame.mouse.get_pos()
            sq = get_square_under_mouse(pos)
            if sq is None:
                continue
            piece = board.piece_at(sq)
            if selected_square is None:
                # Select a white piece
                if piece is not None and piece.color == chess.WHITE:
                    selected_square = sq
                    legal_moves = [m.to_square for m in board.legal_moves if m.from_square == sq]
            else:
                # Try to make a move from selected_square to clicked sq
                mv = None
                for m in board.legal_moves:
                    if m.from_square == selected_square and m.to_square == sq:
                        mv = m
                        break
                if mv is not None:
                    # Auto-promote pawns to Queen
                    if board.piece_type_at(mv.from_square) == chess.PAWN and chess.square_rank(mv.to_square) in (0, 7) and mv.promotion is None:
                        mv = chess.Move(mv.from_square, mv.to_square, promotion=chess.QUEEN)
                    board.push(mv)
                    selected_square = None
                    legal_moves = []
                    # schedule AI move if game not over
                    if not board.is_game_over():
                        ai_thinking = True
                        ai_move_time = pygame.time.get_ticks() + ai_delay_ms
                else:
         
                    if piece is not None and piece.color == chess.WHITE:
                        selected_square = sq
                        legal_moves = [m.to_square for m in board.legal_moves if m.from_square == sq]
                    else:
                        selected_square = None
                        legal_moves = []


    if ai_thinking and pygame.time.get_ticks() >= ai_move_time and not board.is_game_over():
        ai_random_move()

    # Drawing
    screen.fill((200, 200, 200))
    draw_board()
    draw_legal_moves()
    draw_pieces()
    draw_status()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
