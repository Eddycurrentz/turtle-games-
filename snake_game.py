"""
SNAKE GAME - Python turtle module only
----------------------------------------
Controls:
    Arrow keys - change direction
    Space      - pause / resume
    R          - restart after game over

Run:  python snake_game.py
"""

import turtle
import random
import time

# ----------------------------- CONFIG ---------------------------------
WIDTH, HEIGHT = 600, 600
CELL = 20                       # size of one grid step
START_DELAY = 0.12              # seconds between moves (speed)
MIN_DELAY = 0.05
SPEEDUP_EVERY = 5               # speed up every N food eaten

# ----------------------------- SCREEN ----------------------------------
screen = turtle.Screen()
screen.title("Snake - Python Turtle")
screen.bgcolor("black")
screen.setup(width=WIDTH, height=HEIGHT)
screen.tracer(0)                # manual screen updates for smooth control

# ----------------------------- PEN (score) ------------------------------
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, HEIGHT / 2 - 40)

game_state = {"score": 0, "high_score": 0, "delay": START_DELAY, "running": True, "paused": False}


def write_score():
    pen.clear()
    pen.write(
        f"Score: {game_state['score']}   High Score: {game_state['high_score']}",
        align="center", font=("Courier", 18, "normal")
    )


# ----------------------------- SNAKE -------------------------------------
segments = []


def create_snake_head():
    head = turtle.Turtle()
    head.speed(0)
    head.shape("square")
    head.color("lime")
    head.penup()
    head.goto(0, 0)
    head.direction = "stop"
    return head


head = create_snake_head()

# ----------------------------- FOOD ---------------------------------------
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()


def place_food():
    half = (WIDTH // 2 // CELL) * CELL
    x = random.randrange(-half, half, CELL)
    y = random.randrange(-half, half, CELL)
    food.goto(x, y)


place_food()

# ----------------------------- MOVEMENT ------------------------------------


def go_up():
    if head.direction != "down":
        head.direction = "up"


def go_down():
    if head.direction != "up":
        head.direction = "down"


def go_left():
    if head.direction != "right":
        head.direction = "left"


def go_right():
    if head.direction != "left":
        head.direction = "right"


def toggle_pause():
    game_state["paused"] = not game_state["paused"]


def move():
    if head.direction == "up":
        head.sety(head.ycor() + CELL)
    elif head.direction == "down":
        head.sety(head.ycor() - CELL)
    elif head.direction == "left":
        head.setx(head.xcor() - CELL)
    elif head.direction == "right":
        head.setx(head.xcor() + CELL)


def reset_game():
    global segments
    for seg in segments:
        seg.hideturtle()
    segments = []
    head.goto(0, 0)
    head.direction = "stop"
    game_state["score"] = 0
    game_state["delay"] = START_DELAY
    game_state["running"] = True
    game_state["paused"] = False
    place_food()
    write_score()


# ----------------------------- KEY BINDINGS --------------------------------
screen.listen()
screen.onkeypress(go_up, "Up")
screen.onkeypress(go_down, "Down")
screen.onkeypress(go_left, "Left")
screen.onkeypress(go_right, "Right")
screen.onkeypress(toggle_pause, "space")
screen.onkeypress(reset_game, "r")

write_score()

# ----------------------------- MAIN LOOP ------------------------------------
while True:
    screen.update()

    if not game_state["running"] or game_state["paused"]:
        time.sleep(0.1)
        continue

    # wall collision
    if (head.xcor() > WIDTH / 2 - CELL or head.xcor() < -WIDTH / 2
            or head.ycor() > HEIGHT / 2 - CELL or head.ycor() < -HEIGHT / 2):
        time.sleep(0.5)
        game_state["running"] = False
        pen.goto(0, 0)
        pen.write("GAME OVER - press R to restart", align="center",
                   font=("Courier", 20, "normal"))
        continue

    # food collision
    if head.distance(food) < CELL:
        place_food()
        new_seg = turtle.Turtle()
        new_seg.speed(0)
        new_seg.shape("square")
        new_seg.color("darkgreen")
        new_seg.penup()
        segments.append(new_seg)

        game_state["score"] += 10
        if game_state["score"] > game_state["high_score"]:
            game_state["high_score"] = game_state["score"]

        if game_state["score"] % (SPEEDUP_EVERY * 10) == 0:
            game_state["delay"] = max(MIN_DELAY, game_state["delay"] - 0.005)

        write_score()

    # move body segments (from tail to head)
    for index in range(len(segments) - 1, 0, -1):
        x = segments[index - 1].xcor()
        y = segments[index - 1].ycor()
        segments[index].goto(x, y)

    if segments:
        segments[0].goto(head.xcor(), head.ycor())

    move()

    # self collision
    for seg in segments:
        if seg.distance(head) < CELL / 2:
            time.sleep(0.5)
            game_state["running"] = False
            pen.goto(0, 0)
            pen.write("GAME OVER - press R to restart", align="center",
                       font=("Courier", 20, "normal"))

    time.sleep(game_state["delay"])
