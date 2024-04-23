import chess
import chess.svg
import chess.pgn
import pygame
import time
import sys
import io
import cairosvg


width = 1280
height = 720
board_starting_pos = [0,0]
board_size = 600
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

symbol = {
    a: pygame.image.load(io.BytesIO(str(
            chess.svg.piece(chess.Piece.from_symbol(a), size=symbol_size)).encode('utf-8'))) for a in ["R", "N", "B", "Q", "K", "P", "r", "n", "b", "q", "k", "p"]
}

board_image = pygame.image.load(io.BytesIO(cairosvg.svg2png(bytestring=bytes(
    chess.svg.board(board=None, size=board_size), "utf8"))), "png")


border = [(board_image.get_size()[i] - 8 * symbol_size) // 2 for i in range(2)]
positions = {}


def draw_board(special_drawing, square, pos):
    screen.fill((200, 200, 200))
    screen.blit(board_image, board_starting_pos)
    draw_bricks(special_drawing, square, pos)
    pygame.display.update()


def draw_bricks(special_drawing, square, pos):
    global positions
    positions = {"R": [], "N": [], "B": [], "Q": [], "K": [], "P": [], "r": [], "n": [], "b": [], "q": [], "k": [], "p": []}
    x, y = 0, 0
    file, rank = -10, -10
    for c in str(board):
        if c == '\n':
            y += 1
            x = 0
        elif c == special_drawing:
            file = chess.square_file(square)
            rank = 7 - chess.square_rank(square)
        if c in symbol and x != file and y != rank:
            screen.blit(symbol[c], (symbol_size * x + border[0],
                                    symbol_size * y + border[1]))
            pos = chess.square(x, 7-y)
            positions[c].append(pos)
        elif c in symbol and c == special_drawing:
            screen.blit(symbol[c], (pos[0], pos[1]))


        if c in symbol or c == '.':
            x += 1


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
        offset = [file * symbol_size + border[0] - relative_x, (7 - rank) * symbol_size + border[1] - relative_y]
    return chess.square(file, rank)


def select_square(pos):
    global selected_square, selected_piece, click_turn
    prev_square = selected_square
    selected_square = int(find_square(pos[0], pos[1]))
    piece = str(board.piece_at(selected_square))

    if (piece == piece.upper()) == board.turn and piece != "None" and prev_square != selected_square:
        selected_piece = selected_square
        find_legal_moves(selected_square)
        update_board(True)
        click_turn = 1 if len(moves_for_square) > 0 else 0
    elif click_turn == 1 and selected_square in moves_for_square:
        move = chess.Move(from_square=selected_piece, to_square=selected_square)
        prev_moves.append(move)
        board.push(move)
        click_turn = 0
        update_board(False)
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
    if board.is_check():
        variables['check'] = positions["K" if board.turn else "k"][0]
    board_image = pygame.image.load(io.BytesIO(cairosvg.svg2png(bytestring=bytes(chess.svg.board(**variables), "utf8"))), "png")
    draw_board(None, None, None)

def move_piece():
    ...


pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chess")
# Font til tekst i vinduet
font = pygame.font.SysFont("Arial", 36)
update_board(False)


running = True
while running:
    clock = pygame.time.Clock()
    clock.tick(60)
    for event in pygame.event.get():
        if is_moving_brick:
            move_piece()
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if border[0] <= mouse_pos[0] <= board_size - border[0] and border[1] <= mouse_pos[1] <= board_size - border[1]:
                start_mouse_pos = mouse_pos
                is_moving_brick = True
                select_square(mouse_pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            is_moving_brick = False
            mouse_pos_old = mouse_pos
            mouse_pos = pygame.mouse.get_pos()
            if (border[0] <= mouse_pos[0] <= board_size - border[0] and border[1] <= mouse_pos[1] <= board_size - border[1] and not
                    (mouse_pos_old[0]-5 <= mouse_pos[0] <= mouse_pos_old[0]+5) and not
                    (mouse_pos_old[1]-5 <= mouse_pos[1] <= mouse_pos_old[1]+5)):
                select_square(mouse_pos)
                mouse_pos *= 100

if __name__ == "__main__":
    pass


pygame.quit()