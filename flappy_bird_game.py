"""
FLAPPY BIRD - Python turtle module only
-------------------------------------------
Controls:
    Space - flap / jump
    R     - restart after game over

Run: python flappy_bird_game.py
"""

import turtle
import random
import time

# ----------------------------- CONFIG ---------------------------------
WIDTH, HEIGHT = 500, 700
GRAVITY = -0.35
FLAP_STRENGTH = 6.5
PIPE_WIDTH = 60
PIPE_GAP = 170
PIPE_SPEED = 3
PIPE_SPACING = 260          # horizontal distance between pipes
BIRD_X = -150
FRAME_DELAY = 1 / 60        # caps the game loop at ~60 frames per second

# ----------------------------- SCREEN ----------------------------------
screen = turtle.Screen()
screen.title("Flappy Bird - Python Turtle")
screen.bgcolor("skyblue")
screen.setup(width=WIDTH, height=HEIGHT)
screen.tracer(0)

# ----------------------------- GROUND -----------------------------------
ground = turtle.Turtle()
ground.hideturtle()
ground.penup()
ground.color("forestgreen")
ground.goto(-WIDTH / 2, -HEIGHT / 2 + 30)


def draw_ground():
    ground.clear()
    ground.goto(-WIDTH / 2, -HEIGHT / 2 + 30)
    ground.begin_fill()
    for _ in range(2):
        ground.forward(WIDTH)
        ground.right(90)
        ground.forward(30)
        ground.right(90)
    ground.end_fill()


GROUND_Y = -HEIGHT / 2 + 30

# ----------------------------- BIRD ---------------------------------------
bird = turtle.Turtle()
bird.shape("circle")
bird.color("yellow")
bird.shapesize(1.2)
bird.penup()
bird.goto(BIRD_X, 0)

bird_state = {"vy": 0.0, "alive": True, "score": 0, "high_score": 0}

# ----------------------------- PIPES ---------------------------------------
pipes = []          # list of dicts: {top: turtle, bottom: turtle, x, gap_y, scored}


def make_pipe(x):
    gap_y = random.randint(int(-HEIGHT / 2 + 150), int(HEIGHT / 2 - 150))

    top = turtle.Turtle()
    top.shape("square")
    top.color("green")
    top.penup()
    top.shapesize(stretch_wid=1, stretch_len=1)

    bottom = turtle.Turtle()
    bottom.shape("square")
    bottom.color("green")
    bottom.penup()

    pipe = {"top": top, "bottom": bottom, "x": x, "gap_y": gap_y, "scored": False}
    position_pipe(pipe)
    return pipe


def position_pipe(pipe):
    x = pipe["x"]
    gap_y = pipe["gap_y"]

    top_height = (HEIGHT / 2) - (gap_y + PIPE_GAP / 2)
    top_height = max(top_height, 20)
    pipe["top"].shapesize(stretch_wid=top_height / 20, stretch_len=PIPE_WIDTH / 20)
    pipe["top"].goto(x, HEIGHT / 2 - top_height / 2)

    bottom_height = (gap_y - PIPE_GAP / 2) - (-HEIGHT / 2 + 30)
    bottom_height = max(bottom_height, 20)
    pipe["bottom"].shapesize(stretch_wid=bottom_height / 20, stretch_len=PIPE_WIDTH / 20)
    pipe["bottom"].goto(x, -HEIGHT / 2 + 30 + bottom_height / 2)


def reset_pipes():
    for p in pipes:
        p["top"].hideturtle()
        p["bottom"].hideturtle()
    pipes.clear()
    start_x = WIDTH / 2 + 100
    for i in range(4):
        pipes.append(make_pipe(start_x + i * PIPE_SPACING))


reset_pipes()

# ----------------------------- SCORE ---------------------------------------
pen = turtle.Turtle()
pen.hideturtle()
pen.color("white")
pen.penup()
pen.goto(0, HEIGHT / 2 - 60)


def write_score():
    pen.clear()
    pen.write(f"Score: {bird_state['score']}   Best: {bird_state['high_score']}",
               align="center", font=("Courier", 18, "bold"))


write_score()

msg = turtle.Turtle()
msg.hideturtle()
msg.color("white")
msg.penup()
msg.goto(0, 0)

# ----------------------------- CONTROLS -------------------------------------


def flap():
    if bird_state["alive"]:
        bird_state["vy"] = FLAP_STRENGTH
    else:
        restart()


def restart():
    bird.goto(BIRD_X, 0)
    bird_state["vy"] = 0.0
    bird_state["alive"] = True
    bird_state["score"] = 0
    msg.clear()
    reset_pipes()
    write_score()


screen.listen()
screen.onkeypress(flap, "space")
screen.onkeypress(restart, "r")

# ----------------------------- MAIN LOOP -------------------------------------
while True:
    frame_start = time.time()
    screen.update()
    draw_ground()

    if bird_state["alive"]:
        # physics
        bird_state["vy"] += GRAVITY
        bird.sety(bird.ycor() + bird_state["vy"])

        # ceiling / ground collision
        if bird.ycor() > HEIGHT / 2 - 15 or bird.ycor() < GROUND_Y + 15:
            bird_state["alive"] = False

        # move pipes
        for pipe in pipes:
            pipe["x"] -= PIPE_SPEED
            position_pipe(pipe)

            # scoring: pipe passed the bird
            if not pipe["scored"] and pipe["x"] < BIRD_X:
                pipe["scored"] = True
                bird_state["score"] += 1
                if bird_state["score"] > bird_state["high_score"]:
                    bird_state["high_score"] = bird_state["score"]
                write_score()

            # collision detection (bounding-box, bird vs top/bottom pipe)
            bird_x, bird_y = bird.xcor(), bird.ycor()
            within_x = abs(bird_x - pipe["x"]) < (PIPE_WIDTH / 2 + 12)
            if within_x:
                gap_top = pipe["gap_y"] + PIPE_GAP / 2
                gap_bottom = pipe["gap_y"] - PIPE_GAP / 2
                if bird_y > gap_top - 12 or bird_y < gap_bottom + 12:
                    bird_state["alive"] = False

            # recycle pipe once off-screen
            if pipe["x"] < -WIDTH / 2 - PIPE_WIDTH:
                pipe["x"] = max(p["x"] for p in pipes) + PIPE_SPACING
                pipe["gap_y"] = random.randint(int(-HEIGHT / 2 + 150), int(HEIGHT / 2 - 150))
                pipe["scored"] = False

        if not bird_state["alive"]:
            msg.clear()
            msg.goto(0, 0)
            msg.write("GAME OVER\npress R to restart", align="center",
                       font=("Courier", 22, "bold"))

    elapsed = time.time() - frame_start
    if elapsed < FRAME_DELAY:
        time.sleep(FRAME_DELAY - elapsed)
