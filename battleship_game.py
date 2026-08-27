"""
BATTLESHIP - Python turtle module only
------------------------------------------
Two human players, hot-seat, mouse-click controlled.

Setup:
    Each player's 5 ships are placed RANDOMLY and kept hidden.
    (No peeking needed between turns - ships are invisible until hit.)

How to play:
    - Two 8x8 grids are shown: LEFT board = Player 1's fleet,
      RIGHT board = Player 2's fleet.
    - It is always Player 1's turn to fire on the RIGHT board,
      then Player 2's turn to fire on the LEFT board, alternating.
    - Click a cell on the board you're allowed to fire on.
    - Red X = hit, white dot = miss.
    - First to sink all enemy ships wins.

Run: python battleship_game.py
"""

import turtle
import random

# ----------------------------- CONFIG ---------------------------------
GRID_SIZE = 8
CELL = 40
SHIP_SIZES = [4, 3, 3, 2, 2]          # 5 ships per player

BOARD1_ORIGIN = (-380, 180)            # top-left pixel corner, Player 1's board
BOARD2_ORIGIN = (40, 180)              # top-left pixel corner, Player 2's board

WIDTH, HEIGHT = 900, 560

# ----------------------------- SCREEN ----------------------------------
screen = turtle.Screen()
screen.title("Battleship - Python Turtle")
screen.bgcolor("#0b2545")
screen.setup(width=WIDTH, height=HEIGHT)
screen.tracer(0)

drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)
drawer.penup()

pen = turtle.Turtle()
pen.hideturtle()
pen.penup()
pen.color("white")


# ----------------------------- BOARD MODEL -----------------------------
def new_board():
    return {
        "ships": [],                     # list of sets of (r, c)
        "hits": set(),                    # (r, c) that were hit (ship present)
        "misses": set(),                  # (r, c) that were missed
        "sunk": set(),                    # indices of ships fully sunk
    }


def place_ships(board):
    for size in SHIP_SIZES:
        placed = False
        while not placed:
            horizontal = random.choice([True, False])
            if horizontal:
                r = random.randint(0, GRID_SIZE - 1)
                c = random.randint(0, GRID_SIZE - size)
                cells = {(r, c + i) for i in range(size)}
            else:
                r = random.randint(0, GRID_SIZE - size)
                c = random.randint(0, GRID_SIZE - 1)
                cells = {(r + i, c) for i in range(size)}

            occupied = set()
            for ship in board["ships"]:
                occupied |= ship
            if not (cells & occupied):
                board["ships"].append(cells)
                placed = True


board1 = new_board()
board2 = new_board()
place_ships(board1)
place_ships(board2)

state = {"turn": 1, "over": False}


# ----------------------------- DRAWING ----------------------------------
def cell_center(origin, row, col):
    ox, oy = origin
    x = ox + col * CELL + CELL / 2
    y = oy - row * CELL - CELL / 2
    return x, y


def draw_grid(origin, label):
    ox, oy = origin
    drawer.color("white")
    drawer.pensize(2)
    drawer.penup()
    drawer.goto(ox, oy)
    for r in range(GRID_SIZE + 1):
        drawer.goto(ox, oy - r * CELL)
        drawer.pendown()
        drawer.goto(ox + GRID_SIZE * CELL, oy - r * CELL)
        drawer.penup()
    for c in range(GRID_SIZE + 1):
        drawer.goto(ox + c * CELL, oy)
        drawer.pendown()
        drawer.goto(ox + c * CELL, oy - GRID_SIZE * CELL)
        drawer.penup()

    drawer.goto(ox + GRID_SIZE * CELL / 2, oy + 30)
    drawer.write(label, align="center", font=("Courier", 16, "bold"))


def mark_cell(origin, row, col, hit):
    x, y = cell_center(origin, row, col)
    marker = turtle.Turtle()
    marker.hideturtle()
    marker.penup()
    marker.speed(0)
    if hit:
        marker.color("red")
        marker.goto(x - 10, y - 10)
        marker.pendown()
        marker.setheading(45)
        marker.pensize(4)
        marker.forward(28)
        marker.penup()
        marker.goto(x - 10, y + 10)
        marker.pendown()
        marker.setheading(-45)
        marker.forward(28)
        marker.penup()
    else:
        marker.shape("circle")
        marker.color("white")
        marker.shapesize(0.4)
        marker.goto(x, y)
        marker.showturtle()


def reveal_sunk_ship(origin, cells):
    for (r, c) in cells:
        x, y = cell_center(origin, r, c)
        m = turtle.Turtle()
        m.hideturtle()
        m.penup()
        m.shape("square")
        m.color("orange")
        m.shapesize(1.6)
        m.goto(x, y)
        m.showturtle()


def status(text):
    pen.clear()
    pen.goto(0, 250)
    pen.write(text, align="center", font=("Courier", 18, "bold"))


draw_grid(BOARD1_ORIGIN, "Player 1's Fleet")
draw_grid(BOARD2_ORIGIN, "Player 2's Fleet")
status("Player 1's turn: fire on the RIGHT board")


# ----------------------------- GAME LOGIC --------------------------------
def cell_from_click(origin, x, y):
    ox, oy = origin
    if not (ox <= x <= ox + GRID_SIZE * CELL and oy - GRID_SIZE * CELL <= y <= oy):
        return None
    col = int((x - ox) // CELL)
    row = int((oy - y) // CELL)
    row = min(max(row, 0), GRID_SIZE - 1)
    col = min(max(col, 0), GRID_SIZE - 1)
    return row, col


def fire(board, origin, row, col):
    if (row, col) in board["hits"] or (row, col) in board["misses"]:
        return  # already fired here

    hit_ship = None
    for ship in board["ships"]:
        if (row, col) in ship:
            hit_ship = ship
            break

    if hit_ship:
        board["hits"].add((row, col))
        mark_cell(origin, row, col, hit=True)
        if hit_ship <= board["hits"]:
            reveal_sunk_ship(origin, hit_ship)
    else:
        board["misses"].add((row, col))
        mark_cell(origin, row, col, hit=False)

    return hit_ship is not None


def all_sunk(board):
    return all(ship <= board["hits"] for ship in board["ships"])


def on_click(x, y):
    if state["over"]:
        return

    if state["turn"] == 1:
        target_board, target_origin, defender_name = board2, BOARD2_ORIGIN, "Player 2"
    else:
        target_board, target_origin, defender_name = board1, BOARD1_ORIGIN, "Player 1"

    cell = cell_from_click(target_origin, x, y)
    if cell is None:
        return  # clicked outside the legal board for this turn

    row, col = cell
    if (row, col) in target_board["hits"] or (row, col) in target_board["misses"]:
        status("Already fired there - choose another cell")
        return

    hit = fire(target_board, target_origin, row, col)
    screen.update()

    if all_sunk(target_board):
        state["over"] = True
        winner = "Player 1" if state["turn"] == 1 else "Player 2"
        status(f"{winner} WINS! All enemy ships sunk!")
        return

    result_text = "HIT!" if hit else "Miss."
    state["turn"] = 2 if state["turn"] == 1 else 1
    next_side = "RIGHT" if state["turn"] == 1 else "LEFT"
    status(f"{result_text}  Player {state['turn']}'s turn: fire on the {next_side} board")


screen.onclick(on_click)

# ----------------------------- MAIN LOOP -----------------------------------
while True:
    screen.update()
