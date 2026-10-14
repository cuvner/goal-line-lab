# Camera Pico - GIVEN: you don't need to edit this file. Edit camera.py!
#
# Reads the HuskyLens, uses YOUR find_ball() to spot the football, and
# sends it to the server over Wi-Fi.
#
# Wiring (HuskyLens 4-pin cable):
#   green (T)  -> GP16 (pin 21)      black (-) -> GND (pin 23)
#   blue  (R)  -> GP17 (pin 22)      red   (+) -> 3V3(OUT) (pin 36)

import time

import board
import busio
import digitalio
from huskylens import HuskyLens
from pico_coms import PicoComs

import camera

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


def explain_problem(coms, name):
    """Turn a failed send/get into advice a person can act on."""
    if coms.last_status == 403:
        return ("The server doesn't know this Pico yet. Ask the Server person to add\n"
                "this line to devices.txt:   " + name + "," + str(coms.ip))
    if coms.last_status is not None:
        return "The server replied with an error: " + str(coms.last_error)
    return ("Can't reach the server at " + coms.server_url + " (" + str(coms.last_error) + ").\n"
            "Check SERVER_URL in settings.toml has the Pi's IP address, and the server is on.")


# ---- check the student's functions ----

def check(what, got, expected, hint):
    if got == expected:
        print("  ✓", what)
    else:
        print("  ✗", what, "- expected", repr(expected), "but got", repr(got))
        print("     hint:", hint)


def self_check():
    print("\nChecking camera.py...")
    ball = [160, 120, 40, 40, 1]
    other = [50, 200, 30, 30, 2]
    try:
        check("find_ball finds the ball", camera.find_ball([other, ball]), ball,
              "loop through blocks; if box[ID] == BALL_ID, return box")
        check("find_ball gives None when there's no ball", camera.find_ball([other]), None,
              "after the loop has finished, return None")
        check("find_ball copes with an empty list", camera.find_ball([]), None,
              "the loop doesn't run at all when blocks is empty")
        check("describe(50) is left", camera.describe(50), "left", "use if / elif / else")
        check("describe(160) is middle", camera.describe(160), "middle", "use if / elif / else")
        check("describe(300) is right", camera.describe(300), "right", "use if / elif / else")
    except Exception as e:
        print("  ✗ one of your functions crashed:", repr(e))
    print()


self_check()

# ---- connect ----

def find_huskylens():
    """Wait until the HuskyLens is wired up, explaining what's wrong."""
    while True:
        try:
            i2c = busio.I2C(scl=board.GP17, sda=board.GP16)
        except (RuntimeError, ValueError):
            print("Can't find the HuskyLens: check it has power (red/black) and")
            print("the green wire is on GP16 and the blue wire is on GP17.")
            time.sleep(2)
            continue
        while not i2c.try_lock():
            pass
        found = i2c.scan()
        i2c.unlock()
        if 0x32 in found:
            print("  ✓ HuskyLens found")
            return i2c
        print("Something is wired up, but it isn't answering like a HuskyLens.")
        print("On the HuskyLens: General Settings > Protocol Type > I2C.")
        print("If that's already set, try swapping the green and blue wires.")
        i2c.deinit()
        time.sleep(2)


coms = PicoComs(name="camera")
coms.connect()
coms.announce("camera")
husky = HuskyLens(find_huskylens())
husky.connect(HuskyLens.OBJECT_TRACKING)

# ---- main loop: about 10 times a second ----

last_said = None
last_problem = None
failures = 0
while True:
    try:
        blocks = [[b["x"], b["y"], b["w"], b["h"], b["id"]] for b in husky.get_blocks()]
    except (OSError, ValueError) as e:
        print("Can't read the HuskyLens:", e)
        led.value = False
        time.sleep(0.5)
        continue

    try:
        ball = camera.find_ball(blocks)
        where = camera.describe(ball[camera.X]) if ball else None
    except Exception as e:
        print("Problem in camera.py:", repr(e))
        ball, where = None, None
        time.sleep(1)

    if ball:
        reading = {"seen": True, "x": ball[0], "y": ball[1], "w": ball[2], "h": ball[3], "id": ball[4]}
    else:
        reading = {"seen": False}
    led.value = reading["seen"]

    said = "ball: " + str(where) if ball else "no ball"
    if said != last_said:
        print(said)
        last_said = said

    if coms.send("ball", reading):
        if last_problem:
            print("  ✓ the server is accepting the ball now")
        last_problem = None
        failures = 0
    else:
        failures += 1
        if failures >= 3:  # one failure is just a Wi-Fi blip; three in a row is a problem
            problem = explain_problem(coms, "camera")
            if problem != last_problem:
                print(problem)
                last_problem = problem
    time.sleep(0.1)
