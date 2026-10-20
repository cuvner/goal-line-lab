# Cosmic Unicorn scoreboard - GIVEN: you don't need to edit this file. Edit scoreboard.py!
#
# Runs by itself whenever the board has power. Gets the referee's decision
# from the server over Wi-Fi, then uses YOUR functions in scoreboard.py to
# draw on the 32x32 panel. The bottom rows scroll the referee's commentary.
#
#   GOAL          -> your draw_goal()  (GOAL and the score)
#   anything else -> your draw_score() (just the score)
#   no camera     -> your draw_test() drawing, with a blinking blue corner
#   no server     -> an orange corner (the message line says why)
#
# Buttons: the two on the left marked with a sun make it brighter/dimmer.
# Sound: plays GOAL_TUNE on the built-in speaker when a goal is scored.

import time

print("Scoreboard starting in 3 seconds... (press Ctrl-C in the Shell to stop it)")
time.sleep(3)

from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN
from pico_coms import PicoComs

import scoreboard

ROWS, COLS = 32, 32
MESSAGE_ROW = 25          # the commentary scrolls along rows 25-31
STALE_AFTER = 4.0         # seconds without camera data = camera offline
brightness = 0.3

# The goal sound: (frequency in Hz, length in seconds) for each note. Change the tune!
# Middle C = 262, D = 294, E = 330, F = 349, G = 392, A = 440, B = 494, high C = 523
GOAL_TUNE = [(392, 0.12), (523, 0.12), (659, 0.12), (784, 0.35)]
GOAL_TUNE_REPEAT = 2.0    # seconds between repeats while GOAL is showing (0 = play once)
VOLUME = 0.5              # 0 = silent, 1 = loudest

cu = CosmicUnicorn()
g = PicoGraphics(DISPLAY_COSMIC_UNICORN)
g.set_font("bitmap6")
PENS = {0: g.create_pen(0, 0, 0), 1: g.create_pen(0, 255, 0), 2: g.create_pen(255, 180, 0),
        3: g.create_pen(255, 0, 0), 4: g.create_pen(0, 0, 255), 5: g.create_pen(255, 255, 255)}
cu.set_brightness(brightness)
cu.set_volume(VOLUME)
channel = cu.synth_channel(0)
channel.configure(waveforms=channel.TRIANGLE | channel.SQUARE, attack=0.01, decay=0.05,
                  sustain=0.8, release=0.1, volume=1.0)


def play_tune(tune):
    """Play a list of (frequency, seconds) notes on the speaker."""
    cu.play_synth()
    for frequency, seconds in tune:
        channel.frequency(frequency)
        channel.trigger_attack()
        time.sleep(seconds)
        channel.trigger_release()
        time.sleep(0.03)
    cu.stop_playing()


def show(grid, message="", offset=0):
    """Light the panel to match a grid of colour numbers, plus a scrolling message."""
    g.set_pen(PENS[0])
    g.clear()
    for row in range(min(ROWS, len(grid))):
        line = grid[row]
        for col in range(min(COLS, len(line))):
            value = line[col]
            if value:
                g.set_pen(PENS.get(value, PENS[5]))
                g.pixel(col, row)
    if message:
        g.set_pen(PENS[5])
        g.text(message, COLS - offset, MESSAGE_ROW, -1, 1)
    cu.update(g)


def buttons():
    global brightness
    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        brightness = min(1.0, brightness + 0.05)
        cu.set_brightness(brightness)
cu.set_volume(VOLUME)
channel = cu.synth_channel(0)
channel.configure(waveforms=channel.TRIANGLE | channel.SQUARE, attack=0.01, decay=0.05,
                  sustain=0.8, release=0.1, volume=1.0)


def play_tune(tune):
    """Play a list of (frequency, seconds) notes on the speaker."""
    cu.play_synth()
    for frequency, seconds in tune:
        channel.frequency(frequency)
        channel.trigger_attack()
        time.sleep(seconds)
        channel.trigger_release()
        time.sleep(0.03)
    cu.stop_playing()
    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        brightness = max(0.05, brightness - 0.05)
        cu.set_brightness(brightness)
cu.set_volume(VOLUME)
channel = cu.synth_channel(0)
channel.configure(waveforms=channel.TRIANGLE | channel.SQUARE, attack=0.01, decay=0.05,
                  sustain=0.8, release=0.1, volume=1.0)


def play_tune(tune):
    """Play a list of (frequency, seconds) notes on the speaker."""
    cu.play_synth()
    for frequency, seconds in tune:
        channel.frequency(frequency)
        channel.trigger_attack()
        time.sleep(seconds)
        channel.trigger_release()
        time.sleep(0.03)
    cu.stop_playing()


def blank_grid():
    return [[0] * COLS for _ in range(ROWS)]


def good_grid(grid):
    return (isinstance(grid, list) and len(grid) == ROWS and
            all(isinstance(r, list) and len(r) == COLS for r in grid))


def good_letter(letter):
    return (isinstance(letter, list) and len(letter) == 7 and
            all(isinstance(r, list) and len(r) == 5 for r in letter))


def explain_problem(coms, name):
    """Turn a failed get into advice a person can act on."""
    if coms.last_status == 403:
        return ("The server doesn't know this board yet. Ask the Server person to add\n"
                "this line to devices.txt:   " + name + "," + str(coms.ip))
    if coms.last_status is not None:
        return "The server replied with an error: " + str(coms.last_error)
    return ("Can't reach the server at " + coms.server_url + " (" + str(coms.last_error) + ").\n"
            "Check SERVER_URL in settings.py has the Pi's IP address, and the server is on.")


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


def lit(grid):
    return sum(1 for r in grid for v in r if v != 0)


def self_check():
    print("\nChecking scoreboard.py...")
    try:
        grid = scoreboard.make_grid()
        check("make_grid gives 32 rows of 32", good_grid(grid),
              "loop 32 times; each time make a row by looping 32 times")
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
              "only set grid[r][c] when r is 0-31 and c is 0-31")
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
show(grid, "connecting...")
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
        buttons()
        time.sleep(0.1)

# ---- main loop: about 5 times a second ----

tick = 0
offset = 0
message = ""
last_decision = None
last_problem = None
info = None
age = None
fails = 0
next_tune_at = None
while True:
    tick += 1
    buttons()
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
        new_message = "Waiting for the server..."
    elif age is None or age > STALE_AFTER:  # camera not sending
        safely("draw_test", grid)
        if tick % 2:
            grid[0][0] = 4
        decision = "NO CAMERA"
        new_message = "Waiting for the camera..."
    else:
        decision = info.get("decision")
        score = info.get("score", 0)
        new_message = info.get("commentary", "") or ""
        if decision == "GOAL":
            safely("draw_goal", grid, score, tick)
        else:
            safely("draw_score", grid, score)
            if decision not in ("NO GOAL", "NO BALL"):  # e.g. REFEREE ERROR
                grid[0][0] = 3
                new_message = "Referee error - see the dashboard"

    if new_message != message:
        message = new_message
        offset = 0
    offset += 2
    if message and offset > COLS + g.measure_text(message, 1):
        offset = 0

    if decision != last_decision:
        print("now showing:", decision, "| score:", info.get("score") if info else "-")
        last_decision = decision
        next_tune_at = time.ticks_ms() if decision == "GOAL" else None
    show(grid, message, offset)
    if next_tune_at is not None and time.ticks_diff(time.ticks_ms(), next_tune_at) >= 0:
        play_tune(GOAL_TUNE)
        next_tune_at = time.ticks_add(time.ticks_ms(), int(GOAL_TUNE_REPEAT * 1000)) if GOAL_TUNE_REPEAT else None
    time.sleep(0.2 if info is not None else 1)
