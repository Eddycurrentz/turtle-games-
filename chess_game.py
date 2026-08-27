"""
CHESS - Python turtle module only
--------------------------------------------------------------------
A dedicated human-vs-human (hot-seat) chess game.

Rules implemented:
    - All standard piece movement (pawn, knight, bishop, rook, queen, king)
    - Legal-move filtering (you may not make a move that leaves your own
      king in check)
    - Check / Checkmate / Stalemate detection
    - Castling (kingside & queenside), including the "king may not castle
      through or into check" rule
    - En passant capture
    - Pawn promotion (auto-promotes to Queen for simplicity)

Controls:
    Click a piece of your color to select it - legal destination squares
    light up. Click a highlighted square to move there. Click a different
    piece of your own color to change your selection.

    R - restart a fresh game at any time.

Run: python chess_game.py
"""

import turtle

# ----------------------------- CONFIG ---------------------------------
CELL = 60
BOARD_PIX = CELL * 8
ORIGIN = (-BOARD_PIX / 2, BOARD_PIX / 2)     # top-left corner of the board
WIDTH, HEIGHT = 640, 720

LIGHT_SQUARE = "#EEEED2"
DARK_SQUARE = "#769656"
HIGHLIGHT_SELECTED = "#F6F669"
HIGHLIGHT_MOVE = "#8CA9E0"

UNICODE_PIECES = {
    "wK": "\u2654", "wQ": "\u2655", "wR": "\u2656",
    "wB": "\u2657", "wN": "\u2658", "wP": "\u2659",
    "bK": "\u265A", "bQ": "\u265B", "bR": "\u265C",
    "bB": "\u265D", "bN": "\u265E", "bP": "\u265F",
}

KNIGHT_OFFSETS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2), (1, 2), (2, -1), (2, 1)]
DIAG_DIRS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
STRAIGHT_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# ----------------------------- SCREEN ----------------------------------
screen = turtle.Screen()
screen.title("Chess - Python Turtle")
screen.bgcolor("#312E2B")
screen.setup(width=WIDTH, height=HEIGHT)
screen.tracer(0)

square_layer = turtle.Turtle()
square_layer.hideturtle()
square_layer.penup()
square_layer.speed(0)

highlight_layer = turtle.Turtle()
highlight_layer.hideturtle()
highlight_layer.penup()
highlight_layer.speed(0)

piece_layer = turtle.Turtle()
piece_layer.hideturtle()
piece_layer.penup()
piece_layer.speed(0)
piece_layer.color("black")

status_pen = turtle.Turtle()
status_pen.hideturtle()
status_pen.penup()
status_pen.color("white")
status_pen.goto(0, BOARD_PIX / 2 + 40)


# ----------------------------- GAME STATE -------------------------------
def initial_board():
    board = {}
    back_rank = ["R", "N", "B", "Q", "K", "B", "N", "R"]
    for c in range(8):
        board[(0, c)] = "b" + back_rank[c]
        board[(1, c)] = "bP"
        board[(6, c)] = "wP"
        board[(7, c)] = "w" + back_rank[c]
    return board


game = {
    "board": initial_board(),
    "turn": "w",
    "castling": {"wK": True, "wQ": True, "bK": True, "bQ": True},
    "ep_target": None,
    "selected": None,
    "legal_for_selected": [],
    "over": False,
}


# ----------------------------- HELPERS ----------------------------------
def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def cell_center(row, col):
    ox, oy = ORIGIN
    return ox + col * CELL + CELL / 2, oy - row * CELL - CELL / 2


def pixel_to_square(x, y):
    ox, oy = ORIGIN
    if not (ox <= x <= ox + BOARD_PIX and oy - BOARD_PIX <= y <= oy):
        return None
    col = int((x - ox) // CELL)
    row = int((oy - y) // CELL)
    row = min(max(row, 0), 7)
    col = min(max(col, 0), 7)
    return (row, col)


# ----------------------------- MOVE GENERATION ---------------------------
def generate_pseudo_moves(board, pos, color, castling, ep_target):
    moves = []
    piece = board[pos]
    ptype = piece[1]
    r, c = pos

    if ptype == "P":
        direction = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1
        promo_row = 0 if color == "w" else 7

        one = (r + direction, c)
        if in_bounds(*one) and board.get(one) is None:
            mtype = "promotion" if one[0] == promo_row else "normal"
            moves.append({"from": pos, "to": one, "type": mtype})
            two = (r + 2 * direction, c)
            if r == start_row and board.get(two) is None:
                moves.append({"from": pos, "to": two, "type": "double"})

        for dc in (-1, 1):
            diag = (r + direction, c + dc)
            if not in_bounds(*diag):
                continue
            target = board.get(diag)
            if target and target[0] != color:
                mtype = "promotion" if diag[0] == promo_row else "capture"
                moves.append({"from": pos, "to": diag, "type": mtype})
            elif target is None and ep_target == diag:
                moves.append({"from": pos, "to": diag, "type": "en_passant"})

    elif ptype == "N":
        for dr, dc in KNIGHT_OFFSETS:
            dest = (r + dr, c + dc)
            if in_bounds(*dest):
                target = board.get(dest)
                if target is None:
                    moves.append({"from": pos, "to": dest, "type": "normal"})
                elif target[0] != color:
                    moves.append({"from": pos, "to": dest, "type": "capture"})

    elif ptype in ("B", "R", "Q"):
        dirs = []
        if ptype in ("B", "Q"):
            dirs += DIAG_DIRS
        if ptype in ("R", "Q"):
            dirs += STRAIGHT_DIRS
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            while in_bounds(nr, nc):
                target = board.get((nr, nc))
                if target is None:
                    moves.append({"from": pos, "to": (nr, nc), "type": "normal"})
                else:
                    if target[0] != color:
                        moves.append({"from": pos, "to": (nr, nc), "type": "capture"})
                    break
                nr += dr
                nc += dc

    elif ptype == "K":
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                dest = (r + dr, c + dc)
                if in_bounds(*dest):
                    target = board.get(dest)
                    if target is None:
                        moves.append({"from": pos, "to": dest, "type": "normal"})
                    elif target[0] != color:
                        moves.append({"from": pos, "to": dest, "type": "capture"})

        row = 7 if color == "w" else 0
        if pos == (row, 4):
            if (castling.get(color + "K") and board.get((row, 5)) is None
                    and board.get((row, 6)) is None
                    and board.get((row, 7)) == color + "R"):
                moves.append({"from": pos, "to": (row, 6), "type": "castle_k"})
            if (castling.get(color + "Q") and board.get((row, 3)) is None
                    and board.get((row, 2)) is None and board.get((row, 1)) is None
                    and board.get((row, 0)) == color + "R"):
                moves.append({"from": pos, "to": (row, 2), "type": "castle_q"})

    return moves


def get_attacked_squares(board, color):
    """All squares 'color' attacks - used purely for check / castling safety."""
    attacked = set()
    for pos, piece in board.items():
        if piece[0] != color:
            continue
        ptype = piece[1]
        r, c = pos
        if ptype == "P":
            direction = -1 if color == "w" else 1
            for dc in (-1, 1):
                dest = (r + direction, c + dc)
                if in_bounds(*dest):
                    attacked.add(dest)
        elif ptype == "N":
            for dr, dc in KNIGHT_OFFSETS:
                dest = (r + dr, c + dc)
                if in_bounds(*dest):
                    attacked.add(dest)
        elif ptype in ("B", "R", "Q"):
            dirs = []
            if ptype in ("B", "Q"):
                dirs += DIAG_DIRS
            if ptype in ("R", "Q"):
                dirs += STRAIGHT_DIRS
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while in_bounds(nr, nc):
                    attacked.add((nr, nc))
                    if board.get((nr, nc)) is not None:
                        break
                    nr += dr
                    nc += dc
        elif ptype == "K":
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    dest = (r + dr, c + dc)
                    if in_bounds(*dest):
                        attacked.add(dest)
    return attacked


def find_king(board, color):
    for pos, piece in board.items():
        if piece == color + "K":
            return pos
    return None


def is_in_check(board, color):
    king_pos = find_king(board, color)
    if king_pos is None:
        return False
    enemy = "b" if color == "w" else "w"
    return king_pos in get_attacked_squares(board, enemy)


def make_move(board, move, castling):
    """Mutates board & castling in place. Returns new en-passant target."""
    frm, to, mtype = move["from"], move["to"], move["type"]
    piece = board[frm]
    color = piece[0]
    ep_target = None
    captured = board.get(to)

    if mtype == "en_passant":
        board[to] = piece
        del board[frm]
        captured_pos = (frm[0], to[1])
        captured = board.get(captured_pos)
        del board[captured_pos]
    elif mtype == "castle_k":
        row = frm[0]
        board[to] = piece
        del board[frm]
        rook = board.pop((row, 7))
        board[(row, 5)] = rook
    elif mtype == "castle_q":
        row = frm[0]
        board[to] = piece
        del board[frm]
        rook = board.pop((row, 0))
        board[(row, 3)] = rook
    elif mtype == "promotion":
        board[to] = color + "Q"
        del board[frm]
    elif mtype == "double":
        board[to] = piece
        del board[frm]
        ep_target = ((frm[0] + to[0]) // 2, frm[1])
    else:  # normal / capture
        board[to] = piece
        del board[frm]

    if piece[1] == "K":
        castling[color + "K"] = False
        castling[color + "Q"] = False
    if piece[1] == "R":
        home_row = 7 if color == "w" else 0
        if frm == (home_row, 0):
            castling[color + "Q"] = False
        if frm == (home_row, 7):
            castling[color + "K"] = False

    if captured and captured[1] == "R":
        ccolor = captured[0]
        home_row = 7 if ccolor == "w" else 0
        if to == (home_row, 0):
            castling[ccolor + "Q"] = False
        if to == (home_row, 7):
            castling[ccolor + "K"] = False

    return ep_target


def get_legal_moves(board, color, castling, ep_target):
    legal = []
    enemy = "b" if color == "w" else "w"
    for pos in list(board.keys()):
        piece = board[pos]
        if piece[0] != color:
            continue
        for m in generate_pseudo_moves(board, pos, color, castling, ep_target):
            if m["type"] in ("castle_k", "castle_q"):
                attacked_now = get_attacked_squares(board, enemy)
                if pos in attacked_now:
                    continue
                row = pos[0]
                path = [(row, 5), (row, 6)] if m["type"] == "castle_k" else [(row, 3), (row, 2)]
                if any(sq in attacked_now for sq in path):
                    continue

            board_copy = dict(board)
            castling_copy = dict(castling)
            make_move(board_copy, m, castling_copy)
            if not is_in_check(board_copy, color):
                legal.append(m)
    return legal


# ----------------------------- DRAWING ------------------------------------
def draw_squares():
    ox, oy = ORIGIN
    for r in range(8):
        for c in range(8):
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            square_layer.color(color)
            square_layer.goto(ox + c * CELL, oy - r * CELL)
            square_layer.setheading(0)
            square_layer.pendown()
            square_layer.begin_fill()
            for _ in range(4):
                square_layer.forward(CELL)
                square_layer.right(90)
            square_layer.end_fill()
            square_layer.penup()

    # file/rank labels
    ox, oy = ORIGIN
    for c in range(8):
        square_layer.goto(ox + c * CELL + 4, oy - BOARD_PIX + 2)
        square_layer.color("gray")
        square_layer.write(chr(ord('a') + c), font=("Arial", 8, "normal"))
    for r in range(8):
        square_layer.goto(ox - 14, oy - r * CELL - CELL + 4)
        square_layer.color("gray")
        square_layer.write(str(8 - r), font=("Arial", 8, "normal"))


def redraw_pieces():
    piece_layer.clear()
    for pos, piece in game["board"].items():
        x, y = cell_center(*pos)
        piece_layer.goto(x, y - 22)
        symbol = UNICODE_PIECES[piece]
        color = "white" if piece[0] == "w" else "black"
        piece_layer.color(color)
        piece_layer.write(symbol, align="center", font=("Arial", 34, "normal"))


def draw_highlights():
    highlight_layer.clear()
    sel = game["selected"]
    if sel is None:
        return
    x, y = cell_center(*sel)
    highlight_layer.color(HIGHLIGHT_SELECTED)
    highlight_layer.goto(x - CELL / 2, y - CELL / 2)
    highlight_layer.pendown()
    highlight_layer.begin_fill()
    for _ in range(4):
        highlight_layer.forward(CELL)
        highlight_layer.left(90)
    highlight_layer.end_fill()
    highlight_layer.penup()

    for m in game["legal_for_selected"]:
        x, y = cell_center(*m["to"])
        highlight_layer.goto(x, y - 6)
        highlight_layer.color(HIGHLIGHT_MOVE)
        highlight_layer.dot(18)


def set_status(text):
    status_pen.clear()
    status_pen.goto(0, BOARD_PIX / 2 + 40)
    status_pen.write(text, align="center", font=("Arial", 16, "bold"))


def color_name(c):
    return "White" if c == "w" else "Black"


def refresh_status():
    color = game["turn"]
    legal = get_legal_moves(game["board"], color, game["castling"], game["ep_target"])
    if not legal:
        game["over"] = True
        if is_in_check(game["board"], color):
            winner = "Black" if color == "w" else "White"
            set_status(f"Checkmate! {winner} wins.  (Press R to play again)")
        else:
            set_status("Stalemate! It's a draw.  (Press R to play again)")
    else:
        check_note = "  -  Check!" if is_in_check(game["board"], color) else ""
        set_status(f"{color_name(color)} to move{check_note}")


# ----------------------------- INTERACTION ---------------------------------
def on_click(x, y):
    if game["over"]:
        return
    pos = pixel_to_square(x, y)
    if pos is None:
        return

    board = game["board"]
    piece = board.get(pos)
    turn = game["turn"]

    if game["selected"] is None:
        if piece and piece[0] == turn:
            game["selected"] = pos
            all_legal = get_legal_moves(board, turn, game["castling"], game["ep_target"])
            game["legal_for_selected"] = [m for m in all_legal if m["from"] == pos]
            draw_highlights()
        return

    # a piece is already selected
    if piece and piece[0] == turn and pos != game["selected"]:
        game["selected"] = pos
        all_legal = get_legal_moves(board, turn, game["castling"], game["ep_target"])
        game["legal_for_selected"] = [m for m in all_legal if m["from"] == pos]
        draw_highlights()
        return

    chosen = None
    for m in game["legal_for_selected"]:
        if m["to"] == pos:
            chosen = m
            break

    if chosen:
        game["ep_target"] = make_move(board, chosen, game["castling"])
        game["turn"] = "b" if turn == "w" else "w"
        game["selected"] = None
        game["legal_for_selected"] = []
        redraw_pieces()
        highlight_layer.clear()
        refresh_status()
    else:
        game["selected"] = None
        game["legal_for_selected"] = []
        highlight_layer.clear()

    screen.update()


def restart(x=None, y=None):
    game["board"] = initial_board()
    game["turn"] = "w"
    game["castling"] = {"wK": True, "wQ": True, "bK": True, "bQ": True}
    game["ep_target"] = None
    game["selected"] = None
    game["legal_for_selected"] = []
    game["over"] = False
    redraw_pieces()
    highlight_layer.clear()
    set_status("White to move")
    screen.update()


# ----------------------------- SETUP ---------------------------------------
draw_squares()
redraw_pieces()
set_status("White to move")

screen.onclick(on_click)
screen.listen()
screen.onkeypress(restart, "r")

screen.update()
turtle.mainloop()
