# Scoreboard Pico - GIVEN: you don't need to edit this file. Edit scoreboard.py!
#
# Gets the referee's decision from the server over Wi-Fi, then uses YOUR
# functions in scoreboard.py to draw on the 8x32 LED panel.
#
#   GOAL          -> your draw_goal()  (GOAL and the score)
#   anything else -> your draw_score() (just the score)
#   no camera     -> your draw_test() drawing, with a blinking blue corner
#   no server     -> an orange corner (the Shell says why)

import time

import board
import neopixel
from pico_coms import PicoComs

import scoreboard

# ---- panel set-up (teacher: check these once with the test pattern) ----
PIXEL_PIN = board.GP0
BRIGHTNESS = 0.05    # keep it low: 256 LEDs get very bright and power-hungry
COLUMN_MAJOR = True  # the LED chain runs down the columns
SERPENTINE = True    # ...zig-zagging: down column 0, up column 1, ...
FLIP_X = False
FLIP_Y = False

ROWS, COLS = 8, 32
COLOURS = {0: (0, 0, 0), 1: (0, 255, 0), 2: (255, 180, 0), 3: (255, 0, 0),
           4: (0, 0, 255), 5: (255, 255, 255)}
STALE_AFTER = 4.0  # seconds without camera data = camera offline (school Wi-Fi has short dropouts)

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


def good_letter(letter):
    return (isinstance(letter, list) and len(letter) == 7 and
            all(isinstance(r, list) and len(r) == 5 for r in letter))


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


def lit(grid, colour=None):
    return sum(1 for r in grid for v in r if v != 0 and (colour is None or v == colour))


def self_check():
    print("\nChecking scoreboard.py...")
    try:
        grid = scoreboard.make_grid()
        check("make_grid gives 8 rows of 32", good_grid(grid),
              "loop 8 times; each time make a row by looping 32 times")
        if not good_grid(grid):
            print("  (fix make_grid first - the other checks need it)\n")
            return
        check("make_grid is all zeros", lit(grid) == 0, "start every LED at 0")
        grid[0][0] = 5
        check("make_grid's rows are separate lists", grid[1][0] == 0,
              "make a NEW row list inside the loop each time")

        for name in ("O", "A", "L"):
            letter = getattr(scoreboard, name, None)
            check("letter " + name + " is drawn", good_letter(letter) and lit(letter) > 0,
                  "change some 0s to 1s in " + name + " (7 rows of 5)")

        G = scoreboard.G
        grid = scoreboard.make_grid()
        scoreboard.draw_letter(grid, G, 0, 0, 3)
        check("draw_letter draws G at the top-left", grid[0][1] == 3 and grid[0][0] == 0,
              "where letter[row][col] == 1, set grid[top + row][left + col] = colour")
        grid = scoreboard.make_grid()
        scoreboard.draw_letter(grid, G, 1, 10, 2)
        check("draw_letter puts it where you say (row 1, col 10)", grid[1][11] == 2,
              "add `top` to the row and `left` to the column")
        grid = scoreboard.make_grid()
        scoreboard.draw_letter(grid, G, 0, 30, 1)
        check("draw_letter copes with a letter hanging off the right edge", grid[0][31] == 1,
              "only set grid[r][c] when r is 0-7 and c is 0-31")
        grid = scoreboard.make_grid()
        scoreboard.draw_letter(grid, G, 0, -3, 1)
        check("draw_letter copes with a letter hanging off the left edge", grid[0][0] == 1,
              "a column below 0 is off the panel too")

        grid = scoreboard.make_grid()
        scoreboard.draw_goal(grid, 3, 0)
        check("draw_goal lights up GOAL and the score", lit(grid) > 30,
              "call draw_letter for G, O, A, L and DIGITS[score % 10]")
        grid = scoreboard.make_grid()
        scoreboard.draw_score(grid, 3)
        check("draw_score shows the number", lit(grid) > 0, "draw_letter(grid, DIGITS[score % 10], ...)")
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

# ---- main loop: about 5 times a second ----

tick = 0
last_decision = None
last_problem = None
info = None
age = None
fails = 0
while True:
    tick += 1
    got = coms.get("referee")
    if got is not None:
        info, age, fails = got, coms.age, 0
    else:
        fails += 1
        if fails >= 3 or info is None:  # three misses in a row: really can't reach it
            info, age = None, None
        elif age is not None:
            age += 0.25  # one Wi-Fi blip: keep showing the last decision for now
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
    elif age is None or age > STALE_AFTER:  # camera not sending
        safely("draw_test", grid)
        if tick % 2:
            grid[0][0] = 4
        decision = "NO CAMERA"
    else:
        decision = info.get("decision")
        score = info.get("score", 0)
        if decision == "GOAL":
            safely("draw_goal", grid, score, tick)
        else:
            safely("draw_score", grid, score)
            if decision not in ("NO GOAL", "NO BALL"):  # e.g. REFEREE ERROR
                grid[0][0] = 3

    if decision != last_decision:
        print("now showing:", decision, "| score:", info.get("score") if info else "-")
        last_decision = decision
    show(grid)
    time.sleep(0.2 if info is not None else 1)
