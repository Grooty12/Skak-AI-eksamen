import chess
import chess.svg
import chess.pgn
import pygame
import time
import sys
import io
import os
from AIs.random import ai_random
from button import Button

width = 1280
height = 720
board_starting_pos = [0, 0]
board_size = 390
board = chess.Board()
symbol_size = int(45/390 * board_size)
selected_square = None
turn = 0
click_turn = 0 # Kræver to klik på musen at spille spillet: første til at vælge en brik, anden til at vælge, hvor brikken skal flyttes hen
prev_moves = []
moves_for_square = []
selected_piece = None
mouse_pos = [0, 0]
is_moving_brick = False
start_mouse_pos = mouse_pos
offset = [0, 0]
opponent = 0

symbol = {
    a: pygame.image.load(io.BytesIO(str(
            chess.svg.piece(chess.Piece.from_symbol(a), size=symbol_size)).encode('utf-8'))) for a in ["R", "N", "B", "Q", "K", "P", "r", "n", "b", "q", "k", "p"]
}
positions = {}
board_image = pygame.image.load(io.BytesIO(str(
        chess.svg.board(board=None, size=board_size)).encode('utf-8')))

border = [(board_size - 8 * symbol_size) // 2 for i in range(2)]
buttons = []
screen = pygame.display.set_mode((width, height))
is_pawn_promotion = False
pawn_promote_square = None


def setup():
    global buttons
    pygame.init()
    pygame.display.set_caption("Chess")
    buttons.append(Button(board_starting_pos[0]+board_size+50, 100, 100, 50, "#a6a6a6", "Spiller", False, 0))
    buttons.append(Button(board_starting_pos[0]+board_size+50, 200, 100, 50, "#a6a6a6", "Random", True, 1))
    update_board(False)


def draw_board(special_drawing, square, piece_pos):
    screen.fill((200, 200, 200))
    screen.blit(board_image, board_starting_pos)
    draw_bricks(special_drawing, square, piece_pos)
    for a in buttons:
        a.show(screen)
    if is_pawn_promotion:
        draw_pawn_promotion()
    pygame.display.update()


def draw_bricks(special_drawing, square, piece_pos):
    global positions
    positions = {"R": [], "N": [], "B": [], "Q": [], "K": [], "P": [], "r": [], "n": [], "b": [], "q": [], "k": [], "p": []}
    x, y = 0, 0
    file, rank = -10, -10
    draw_square = chess.square(x, y)
    for c in str(board):
        if c == '\n':
            y += 1
            x = 0
        elif c == special_drawing:
            file = chess.square_file(square)
            rank = 7 - chess.square_rank(square)
        draw_square = chess.square(x, 7 - y)
        if c in symbol and square != draw_square:
            screen.blit(symbol[c], (symbol_size * x + border[0],
                                    symbol_size * y + border[1]))
            positions[c].append(draw_square)
        elif c in symbol and c == special_drawing:
            screen.blit(symbol[c], piece_pos)
        if c in symbol or c == '.':
            x += 1


def draw_pawn_promotion():
    global is_pawn_promotion
    rect = pygame.Rect(board_starting_pos, [board_size, board_size])
    translucent_surface = pygame.Surface((board_size, board_size), pygame.SRCALPHA)
    pygame.draw.rect(translucent_surface, (0, 0, 0, 170), rect)
    screen.blit(translucent_surface, board_starting_pos)
    center_coordinates = get_coordinates(pawn_promote_square)
    starting_position = pygame.Rect(center_coordinates, [board_size, board_size])
    way = 1 if board.turn else -1
    drawings = ["q", "n", "r", "b"]
    for i in range(4):
        pygame.draw.circle(screen, "Grey", (starting_position.x + symbol_size/2, starting_position.y + (i * symbol_size * way) + symbol_size/2), symbol_size/2.1)
        drawing_type = drawings[i].upper() if way == 1 else drawings[i]
        drawing = pygame.transform.scale_by(symbol[drawing_type], 0.9)
        screen.blit(drawing, (starting_position.x + symbol_size*0.05, starting_position.y + (i*symbol_size*way)+symbol_size*0.05))


def find_legal_moves(square):
    global moves_for_square
    legal_moves = board.legal_moves
    moves_for_square = [move.to_square for move in legal_moves if move.from_square == selected_piece]


def get_coordinates(number):
    file = chess.square_file(number)
    rank = chess.square_rank(number)
    pos = [board_starting_pos[i] + border[i] + symbol_size * x for i, x in enumerate([file, 7 - rank])]
    return pos


def find_square(x, y):
    global offset
    relative_x, relative_y = x - border[0], y - border[1]
    file = relative_x // symbol_size
    rank = 7 - (relative_y // symbol_size)
    if offset == [0, 0]:
        offset = [0.5*symbol_size - (relative_x - file * symbol_size + border[0]), 0.5 * symbol_size - (relative_y - (7 - rank) * symbol_size + border[1])]
    return chess.square(file, rank)


def select_square(pos):
    global selected_square, selected_piece, click_turn, offset, is_moving_brick, is_pawn_promotion, moves_for_square, pawn_promote_square
    prev_square = selected_square
    selected_square = int(find_square(pos[0], pos[1]))
    piece = str(board.piece_at(selected_square))
    if (piece == piece.upper()) == board.turn and piece != "None" and prev_square != selected_square and not is_moving_brick:
        selected_piece = selected_square
        find_legal_moves(selected_square)
        update_board(True)
        click_turn = 1 if len(moves_for_square) > 0 else 0
        is_moving_brick = True
    elif click_turn == 1 and selected_square in moves_for_square:
        rank = chess.square_rank(selected_square)
        piece_moved = str(board.piece_at(selected_piece))
        if piece_moved.upper() == "P" and rank in [0, 7]:
            is_pawn_promotion = True
            moves_for_square = [selected_square]
            pawn_promote_square = selected_square
            update_board(True)
            return
        move = chess.Move(from_square=selected_piece, to_square=selected_square)
        prev_moves.append(move)
        board.push(move)
        click_turn = 0
        update_board(False)
        find_opponent()
    else:
        click_turn = 0
        selected_square = None
        selected_piece = None
        update_board(False)


def update_board(is_move):
    global board_image, click_turn, moves_for_square
    square_colours = {}

    if is_move:
        square_colours = {
            move: "#cc0000cc" for move in moves_for_square
        }
        square_colours[selected_piece] = "#90ff33"
    variables = {
        'board': None,
        'size': board_size,
        'lastmove': prev_moves[-1] if len(prev_moves) > 0 else None,
        'fill': square_colours,
    }
    board_image = pygame.image.load(io.BytesIO(str(
        chess.svg.board(**variables)).encode('utf-8')))
    draw_board(None, None, None)


def move_piece():
    mouse_pos = pygame.mouse.get_pos()
    if not start_mouse_pos[0] - 5 <= mouse_pos[0] <= start_mouse_pos[0] + 5 or not start_mouse_pos[1] - 5 <= mouse_pos[1] <= start_mouse_pos[1] + 5:
        moved_piece = str(board.piece_at(selected_piece))
        draw_position = [mouse_pos[0] + offset[0], mouse_pos[1] + offset[1]]
        draw_board(moved_piece, selected_piece, draw_position)


def is_pressing_button(pos):
    global opponent
    for i in buttons:
        if i.x <= pos[0] <= i.x + i.width and i.y <= pos[1] <= i.y + i.height:
            opponent = i.is_pressed()
            return True


def find_opponent():
    if opponent == 1:
        move_uci = ai_random(list(board.legal_moves))
        move = chess.Move.from_uci(f"{move_uci}")
        prev_moves.append(move)
        board.push(move)
        update_board(False)


setup()

running = True
while running:
    clock = pygame.time.Clock()
    clock.tick(60)
    for event in pygame.event.get():
        if is_moving_brick:
            move_piece()
        elif is_pawn_promotion:
            ...
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not is_pawn_promotion:
            mouse_pos = pygame.mouse.get_pos()
            if border[0] <= mouse_pos[0] <= board_size - border[0] and border[1] <= mouse_pos[1] <= board_size - border[1]:
                start_mouse_pos = mouse_pos
                select_square(mouse_pos)
            else:
                is_pressing_button(mouse_pos)
        elif event.type == pygame.MOUSEBUTTONUP and not is_pawn_promotion:
            offset = [0, 0]
            mouse_pos_old = mouse_pos
            mouse_pos = pygame.mouse.get_pos()
            if (border[0] <= mouse_pos[0] <= board_size - border[0] and
                    border[1] <= mouse_pos[1] <= board_size - border[1] and not
                    ((mouse_pos_old[0]-5 <= mouse_pos[0] <= mouse_pos_old[0]+5) and
                     (mouse_pos_old[1]-5 <= mouse_pos[0] <= mouse_pos_old[1]+5))):
                select_square(mouse_pos)
                mouse_pos *= 100
            is_moving_brick = False
        elif event.type == pygame.MOUSEBUTTONUP and is_pawn_promotion:
            ...

if __name__ == "__main__":
    pass

pygame.quit()