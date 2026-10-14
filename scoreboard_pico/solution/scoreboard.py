# THE SCOREBOARD - SOLUTION
# Copy over scoreboard.py on the Pico to use it.

from digits import DIGITS

TEST_MODE = False

OFF = 0
GREEN = 1
YELLOW = 2
RED = 3
BLUE = 4
WHITE = 5

ROWS = 8
COLS = 32


def make_grid():
    grid = []
    for row in range(ROWS):
        new_row = []
        for col in range(COLS):
            new_row.append(OFF)
        grid.append(new_row)
    return grid


def draw_test(grid):
    # A red border
    for col in range(COLS):
        grid[0][col] = RED
        grid[ROWS - 1][col] = RED
    for row in range(ROWS):
        grid[row][0] = RED
        grid[row][COLS - 1] = RED


G = [
    [0, 1, 1, 1, 0],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0],
    [1, 0, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [0, 1, 1, 1, 0],
]

O = [
    [0, 1, 1, 1, 0],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [0, 1, 1, 1, 0],
]

A = [
    [0, 1, 1, 1, 0],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
]

L = [
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1],
]


def draw_letter(grid, letter, top, left, colour):
    for row in range(len(letter)):
        for col in range(len(letter[row])):
            if letter[row][col] == 1:
                r = top + row
                c = left + col
                if r >= 0 and r < ROWS and c >= 0 and c < COLS:
                    grid[r][c] = colour


def draw_goal(grid, score, tick):
    # Flash between red and yellow
    if tick % 2 == 0:
        colour = RED
    else:
        colour = YELLOW
    draw_letter(grid, G, 0, 0, colour)
    draw_letter(grid, O, 0, 6, colour)
    draw_letter(grid, A, 0, 12, colour)
    draw_letter(grid, L, 0, 18, colour)
    draw_letter(grid, DIGITS[score % 10], 0, 26, WHITE)


def draw_score(grid, score):
    draw_letter(grid, DIGITS[score % 10], 0, 14, GREEN)


# Extension: scrolling. Call this from draw_goal instead.
def draw_goal_scrolling(grid, score, tick):
    left = COLS - (tick % 70)   # starts off the right edge, slides left
    draw_letter(grid, G, 0, left, RED)
    draw_letter(grid, O, 0, left + 6, RED)
    draw_letter(grid, A, 0, left + 12, RED)
    draw_letter(grid, L, 0, left + 18, RED)
    draw_letter(grid, DIGITS[score % 10], 0, left + 26, WHITE)


# Extension: two-digit scores
def draw_big_score(grid, score):
    tens = score // 10
    units = score % 10
    draw_letter(grid, DIGITS[tens], 0, 10, GREEN)
    draw_letter(grid, DIGITS[units], 0, 16, GREEN)
