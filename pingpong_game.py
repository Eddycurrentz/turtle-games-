"""
PING PONG (PONG) - Python turtle module only
------------------------------------------------
Two player game, hot-seat, same keyboard.

Controls:
    Player 1 (left paddle):  W = up,   S = down
    Player 2 (right paddle): Up arrow = up, Down arrow = down
    Space - pause / resume

First to 7 points wins. Run: python pingpong_game.py
"""

import turtle
import time

# ----------------------------- CONFIG ---------------------------------
WIDTH, HEIGHT = 800, 600
PADDLE_SPEED = 20
BALL_SPEED_X = 4
BALL_SPEED_Y = 4
WIN_SCORE = 7
FRAME_DELAY = 1 / 60          # caps the game loop at ~60 frames per second

# ----------------------------- SCREEN ----------------------------------
screen = turtle.Screen()
screen.title("Ping Pong - Python Turtle")
screen.bgcolor("black")
screen.setup(width=WIDTH, height=HEIGHT)
screen.tracer(0)

# ----------------------------- BORDER -----------------------------------
border = turtle.Turtle()
border.color("white")
border.penup()
border.goto(-WIDTH / 2 + 5, HEIGHT / 2 - 5)
border.pendown()
border.pensize(3)
for _ in range(2):
    border.forward(WIDTH - 10)
    border.right(90)
    border.forward(HEIGHT - 10)
    border.right(90)
border.hideturtle()

# midline (dashed)
mid = turtle.Turtle()
mid.color("gray")
mid.penup()
mid.goto(0, HEIGHT / 2 - 10)
mid.setheading(270)
mid.hideturtle()
dash = True
y = HEIGHT / 2 - 10
while y > -HEIGHT / 2 + 10:
    if dash:
        mid.pendown()
    else:
        mid.penup()
    mid.forward(15)
    y -= 15
    dash = not dash

# ----------------------------- PADDLES -----------------------------------
paddle_a = turtle.Turtle()
paddle_a.speed(0)
paddle_a.shape("square")
paddle_a.color("white")
paddle_a.shapesize(stretch_wid=5, stretch_len=1)
paddle_a.penup()
paddle_a.goto(-WIDTH / 2 + 40, 0)

paddle_b = turtle.Turtle()
paddle_b.speed(0)
paddle_b.shape("square")
paddle_b.color("white")
paddle_b.shapesize(stretch_wid=5, stretch_len=1)
paddle_b.penup()
paddle_b.goto(WIDTH / 2 - 40, 0)

# ----------------------------- BALL ---------------------------------------
ball = turtle.Turtle()
ball.speed(0)
ball.shape("circle")
ball.color("white")
ball.penup()
ball.goto(0, 0)
ball.dx = BALL_SPEED_X
ball.dy = BALL_SPEED_Y

# ----------------------------- SCORE ---------------------------------------
score_a = 0
score_b = 0
pen = turtle.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, HEIGHT / 2 - 50)


def write_score():
    pen.clear()
    pen.write(f"{score_a}          {score_b}", align="center",
               font=("Courier", 28, "normal"))


write_score()

game_state = {"paused": False, "over": False}

# ----------------------------- CONTROLS -------------------------------------


def paddle_a_up():
    y = paddle_a.ycor()
    if y < HEIGHT / 2 - 60:
        paddle_a.sety(y + PADDLE_SPEED)


def paddle_a_down():
    y = paddle_a.ycor()
    if y > -HEIGHT / 2 + 60:
        paddle_a.sety(y - PADDLE_SPEED)


def paddle_b_up():
    y = paddle_b.ycor()
    if y < HEIGHT / 2 - 60:
        paddle_b.sety(y + PADDLE_SPEED)


def paddle_b_down():
    y = paddle_b.ycor()
    if y > -HEIGHT / 2 + 60:
        paddle_b.sety(y - PADDLE_SPEED)


def toggle_pause():
    game_state["paused"] = not game_state["paused"]


screen.listen()
screen.onkeypress(paddle_a_up, "w")
screen.onkeypress(paddle_a_down, "s")
screen.onkeypress(paddle_b_up, "Up")
screen.onkeypress(paddle_b_down, "Down")
screen.onkeypress(toggle_pause, "space")


def reset_ball(direction):
    ball.goto(0, 0)
    ball.dx = BALL_SPEED_X * direction
    ball.dy = BALL_SPEED_Y


# ----------------------------- MAIN LOOP -------------------------------------
while True:
    frame_start = time.time()
    screen.update()

    if game_state["over"] or game_state["paused"]:
        # keep the delay even while idle so the loop doesn't spin the CPU
        elapsed = time.time() - frame_start
        if elapsed < FRAME_DELAY:
            time.sleep(FRAME_DELAY - elapsed)
        continue

    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # top / bottom wall bounce
    if ball.ycor() > HEIGHT / 2 - 20 or ball.ycor() < -HEIGHT / 2 + 20:
        ball.dy *= -1

    # right wall -> player A scores
    if ball.xcor() > WIDTH / 2 - 10:
        score_a += 1
        write_score()
        reset_ball(-1)

    # left wall -> player B scores
    if ball.xcor() < -WIDTH / 2 + 10:
        score_b += 1
        write_score()
        reset_ball(1)

    # paddle collisions
    if (ball.xcor() > WIDTH / 2 - 50 and ball.xcor() < WIDTH / 2 - 40
            and abs(ball.ycor() - paddle_b.ycor()) < 55):
        ball.setx(WIDTH / 2 - 50)
        ball.dx *= -1

    if (ball.xcor() < -WIDTH / 2 + 50 and ball.xcor() > -WIDTH / 2 + 40
            and abs(ball.ycor() - paddle_a.ycor()) < 55):
        ball.setx(-WIDTH / 2 + 50)
        ball.dx *= -1

    if score_a >= WIN_SCORE or score_b >= WIN_SCORE:
        game_state["over"] = True
        winner = "Player 1 (left)" if score_a > score_b else "Player 2 (right)"
        pen.goto(0, 0)
        pen.write(f"{winner} WINS!", align="center", font=("Courier", 30, "normal"))

    elapsed = time.time() - frame_start
    if elapsed < FRAME_DELAY:
        time.sleep(FRAME_DELAY - elapsed)
