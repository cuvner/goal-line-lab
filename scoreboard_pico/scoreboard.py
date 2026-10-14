# THE SCOREBOARD - this is your file!
#
# The LED panel is 8 rows tall and 32 columns wide. You draw on it with a
# GRID: a 2D list of numbers, one number per light.
#   grid[row][col]    row 0 is the top,   col 0 is the left
#   0 = off   1 = green   2 = yellow   3 = red   4 = blue   5 = white
#
# Letters are little grids too: 7 rows of 5 numbers, where 1 = lit.
#
# Save this file and the Pico restarts with your new code. The Shell
# shows a ✓ or ✗ for each function.

from digits import DIGITS  # DIGITS[3] is the number 3, drawn like the letters below

# STAGE 1: True = just show your draw_test() drawing.
# Change to False when you get to stage 3.
TEST_MODE = True

OFF = 0
GREEN = 1
YELLOW = 2
RED = 3
BLUE = 4
WHITE = 5

ROWS = 8
COLS = 32


# ---------------- STAGE 1 ----------------
def make_grid():
    """Make an empty grid: a list of 8 rows, where each row is a list of
    32 zeros. Use loops, so that every row is its own separate list."""
    grid = []
    return grid


def draw_test(grid):
    """Have fun: change some numbers in grid to draw something - your
    initials, a smiley, a flag... e.g. grid[0][0] = RED lights the
    top-left LED red. Loops are good for lines."""
    pass


# ---------------- STAGE 2: your letters ----------------
# G is done for you. Draw O, A and L by changing 0s to 1s.

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
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]

A = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]

L = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]


def draw_letter(grid, letter, top, left, colour):
    """Copy a letter onto the grid, with its top-left corner at row `top`
    and column `left`.
    Loop over every row and column of `letter`. Where it's a 1, set
        grid[top + row][left + col] = colour
    Only draw lights that are really on the panel (row 0-7, col 0-31),
    so a letter can hang off the edge without crashing."""
    pass


# ---------------- STAGE 3 ----------------
def draw_goal(grid, score, tick):
    """GOAL! Draw G, O, A, L and the score with draw_letter().
    Letters are 5 wide, so leave a gap: columns 0, 6, 12, 18 for the
    letters and 26 for the number. DIGITS[score % 10] is the number.
    Pick your own colours!
    (tick goes up by 1 five times a second. Ignore it until stage 4.)"""
    pass


def draw_score(grid, score):
    """Between goals, just show the score in the middle of the panel."""
    pass
