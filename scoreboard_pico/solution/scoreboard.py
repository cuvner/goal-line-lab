# THE SCOREBOARD - SOLUTION
# Copy over scoreboard.py on the Pico to use it.

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


def draw_ball(grid, x, y):
    col = x // 10
    row = y // 30
    if col > COLS - 1:
        col = COLS - 1
    if row > ROWS - 1:
        row = ROWS - 1
    grid[row][col] = GREEN


def load_picture(filename):
    picture = []
    with open(filename) as file:
        for line in file:
            picture.append(list(line.strip()))
    return picture


def draw_picture(grid, picture, colour):
    for row in range(len(picture)):
        for col in range(len(picture[row])):
            if picture[row][col] == "#":
                grid[row][col] = colour


# Extension: show where the goal line is, as a blue column
def draw_goal_line(grid, line_x):
    col = line_x // 10
    if col > COLS - 1:
        col = COLS - 1
    for row in range(ROWS):
        if grid[row][col] == OFF:
            grid[row][col] = BLUE
