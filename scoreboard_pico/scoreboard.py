# THE SCOREBOARD - this is your file!
#
# The LED panel is 8 rows tall and 32 columns wide. You draw on it with a
# GRID: a 2D list of numbers, one number per LED.
#   grid[row][col]    row 0 is the top,   col 0 is the left
#
# The number says what colour the LED is:
#   0 = off   1 = green   2 = yellow   3 = red   4 = blue   5 = white
#
# Save this file and the Pico restarts with your new code. The console
# shows a ✓ or ✗ for each function.

# STAGE 1: True = just show your draw_test() drawing.
# Change to False when you get to stage 2.
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


# ---------------- STAGE 1 (have fun) ----------------
def draw_test(grid):
    """Change some numbers in grid to draw something - your initials, a
    smiley face, a flag... e.g. grid[0][0] = RED makes the top-left LED red."""
    pass


# ---------------- STAGE 2 ----------------
def draw_ball(grid, x, y):
    """Draw the ball on the grid in GREEN.
    x and y are where the ball is in the CAMERA's picture, which is
    320 wide and 240 tall. The panel is 32 wide and 8 tall, so:
        col = x // 10          (320 / 32 = 10)
        row = y // 30          (240 / 8 = 30)
    Make sure col and row aren't too big for the grid (x can be 320!)."""
    pass


# ---------------- STAGE 3 ----------------
def load_picture(filename):
    """Read a picture from a text file and give back a 2D list of characters.
    Each line of the file is one row, and each character is one LED:
    "#" means lit and "." means off. Remember to remove the newline from
    the end of each line (line.strip())."""
    picture = []
    return picture


def draw_picture(grid, picture, colour):
    """Copy the picture onto the grid: everywhere the picture has a "#",
    set that place in the grid to `colour`.
    Hint: loop over every row and column of the picture."""
    pass
