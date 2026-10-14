# Scoreboard Pico - GIVEN: you don't need to edit this file. Edit scoreboard.py!
#
# Gets the referee's decision from the server over Wi-Fi, then uses YOUR
# functions in scoreboard.py to draw on the 8x32 LED panel.
#
#   GOAL         -> the GOAL! picture, flashing
#   NO GOAL      -> the ball, where the camera sees it
#   NO BALL      -> your own picture (my_picture.txt)
#   no camera    -> your draw_test() drawing, with a blinking blue corner
#   no server    -> an orange corner (the console says why)

import time

import board
import neopixel
from pico_coms import PicoComs

import scoreboard

# ---- panel set-up (teacher: check these once with the chase test) ----
PIXEL_PIN = board.GP0
BRIGHTNESS = 0.05   # keep it low: 256 LEDs get very bright and power-hungry
COLUMN_MAJOR = True  # the LED chain runs down the columns
SERPENTINE = True    # ...zig-zagging: down column 0, up column 1, ...
FLIP_X = False
FLIP_Y = False

ROWS, COLS = 8, 32
COLOURS = {0: (0, 0, 0), 1: (0, 255, 0), 2: (255, 180, 0), 3: (255, 0, 0),
           4: (0, 0, 255), 5: (255, 255, 255)}
STALE_AFTER = 2.0  # seconds without camera data = camera offline

pixels = neopixel.NeoPixel(PIXEL_PIN, ROWS * COLS, brightness=BRIGHTNESS, auto_write=False)


def index(row, col):
    x, y = col, row
    if FLIP_X:
        x = COLS - 1 - x
    if FLIP_Y:
        y = ROWS - 1 - y
    if COLUMN_MAJOR:
        if SERPENTINE and x % 2:
            y = ROWS - 1 - y
        return x * ROWS + y
    if SERPENTINE and y % 2:
        x = COLS - 1 - x
    return y * COLS + x


def show(grid):
    """Light the panel to match a grid of colour numbers."""
    pixels.fill((0, 0, 0))
    for row in range(min(ROWS, len(grid))):
        for col in range(min(COLS, len(grid[row]))):
            pixels[index(row, col)] = COLOURS.get(grid[row][col], (255, 255, 255))
    pixels.show()


def blank_grid():
    return [[0] * COLS for _ in range(ROWS)]


def good_grid(grid):
    return (isinstance(grid, list) and len(grid) == ROWS and
            all(isinstance(r, list) and len(r) == COLS for r in grid))


def explain_problem(coms, name):
    """Turn a failed send/get into advice a person can act on."""
    if coms.last_status == 403:
        return ("The server doesn't know this Pico yet. Ask the Server person to add\n"
                "this line to devices.txt:   " + name + "," + str(coms.ip))
    if coms.last_status is not None:
        return "The server replied with an error: " + str(coms.last_error)
    return ("Can't reach the server at " + coms.server_url + " (" + str(coms.last_error) + ").\n"
            "Check SERVER_URL in settings.toml has the Pi's IP address, and the server is on.")


# ---- run the student's functions safely ----

problems = set()


def safely(name, *args):
    """Call scoreboard.<name>(*args); on a crash, say so once and carry on."""
    try:
        return getattr(scoreboard, name)(*args)
    except Exception as e:
        message = name + "(): " + repr(e)
        if message not in problems:
            problems.add(message)
            print("Problem in scoreboard.py ->", message)
        return None


def check(what, ok, hint):
    print("  ✓" if ok else "  ✗", what)
    if not ok:
        print("     hint:", hint)


def self_check():
    print("\nChecking scoreboard.py...")
    try:
        grid = scoreboard.make_grid()
        check("make_grid gives 8 rows of 32", good_grid(grid),
              "loop 8 times; each time make a row by looping 32 times")
        if good_grid(grid):
            check("make_grid is all zeros", all(v == 0 for r in grid for v in r), "start every LED at 0")
            grid[0][0] = 5
            check("make_grid's rows are separate lists", grid[1][0] == 0,
                  "make a NEW row list inside the loop each time")
            grid = scoreboard.make_grid()
            scoreboard.draw_ball(grid, 160, 120)
            check("draw_ball(160, 120) lights row 4, col 16", grid[4][16] == 1,
                  "col = x // 10, row = y // 30, then grid[row][col] = GREEN")
            grid = scoreboard.make_grid()
            scoreboard.draw_ball(grid, 320, 240)
            check("draw_ball copes with the far corner (320, 240)", grid[7][31] == 1,
                  "if col is bigger than 31, make it 31 (and row 7)")
        picture = scoreboard.load_picture("goal.txt")
        check("load_picture reads 8 rows of 32", good_grid(picture),
              "one list per line; use list(line.strip()) to split a line into characters")
        if good_grid(picture) and good_grid(scoreboard.make_grid()):
            grid = scoreboard.make_grid()
            scoreboard.draw_picture(grid, picture, 2)
            lit = sum(1 for r in grid for v in r if v == 2)
            hashes = sum(1 for r in picture for c in r if c == "#")
            check("draw_picture lights every #", lit == hashes and lit > 0,
                  "two loops (rows, then columns); if picture[row][col] == '#': grid[row][col] = colour")
    except Exception as e:
        print("  ✗ one of your functions crashed:", repr(e))
    print()


self_check()

# ---- connect (so the IP address is printed even in TEST_MODE) ----

grid = blank_grid()
grid[0][0] = 2
show(grid)
coms = PicoComs(name="scoreboard")
coms.connect()
coms.announce("scoreboard")

# ---- stage 1: just show draw_test() ----

if getattr(scoreboard, "TEST_MODE", False):
    print("TEST_MODE: showing draw_test(). Set TEST_MODE = False in scoreboard.py when you're done.")
    grid = safely("make_grid")
    if not good_grid(grid):
        grid = blank_grid()
    safely("draw_test", grid)
    show(grid)
    while True:
        time.sleep(1)

goal_picture = safely("load_picture", "goal.txt")
my_picture = safely("load_picture", "my_picture.txt")

# ---- main loop: about 5 times a second ----

tick = 0
last_decision = None
last_problem = None
while True:
    tick += 1
    info = coms.get("referee")
    problem = explain_problem(coms, "scoreboard") if info is None else None
    if problem != last_problem:
        print(problem if problem else "  ✓ getting decisions from the server now")
        last_problem = problem

    grid = safely("make_grid")
    if not good_grid(grid):
        grid = blank_grid()

    if info is None:  # can't reach the server
        grid[0][0] = 2
        decision = "NO SERVER"
    elif coms.age is None or coms.age > STALE_AFTER:  # camera not sending
        safely("draw_test", grid)
        if tick % 2:
            grid[0][0] = 4
        decision = "NO CAMERA"
    else:
        decision = info.get("decision")
        if decision == "GOAL":
            if goal_picture:
                safely("draw_picture", grid, goal_picture, 2 if tick % 4 < 2 else 1)
        elif decision == "NO BALL":
            if my_picture:
                safely("draw_picture", grid, my_picture, 4)
        else:
            if info.get("seen"):
                safely("draw_ball", grid, info.get("x", 0), info.get("y", 0))
            if hasattr(scoreboard, "draw_goal_line") and info.get("line") is not None:
                safely("draw_goal_line", grid, int(info["line"]))
            if decision != "NO GOAL":  # e.g. REFEREE ERROR
                grid[0][0] = 3

    if decision != last_decision:
        print("now showing:", decision, "| score:", info.get("score") if info else "-")
        last_decision = decision
    show(grid)
    time.sleep(0.2 if info is not None else 1)
