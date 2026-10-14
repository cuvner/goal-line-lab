# LED panel Pico 2 W - STARTER (LED panel role)
# Work through the stages in docs/role_led_panel.md.
#
# CIRCUITPY/lib needs: everything in pico_lib/, neopixel.mpy, adafruit_pixelbuf.mpy,
#                      adafruit_requests.mpy, adafruit_connection_manager.mpy
# CIRCUITPY/settings.toml needs: WIFI_SSID, WIFI_PASSWORD, SERVER_URL

import math
import time

import board
import neopixel
from pico_coms import PicoComs

# Change this as you move through the stages:
# "chase"        stage 1: light pixels 0, 1, 2... in order to see how the panel is wired
# "test_pattern" stage 1: check your index(x, y)
# "fake_ball"    stage 2: draw made-up balls without needing the server
# "server"       stage 3+: show the real ball from the server
MODE = "chase"

WIDTH, HEIGHT = 32, 8
PIXEL_PIN = board.GP0    # change if your panel's DIN wire is on another pin
BRIGHTNESS = 0.05        # 256 LEDs get very bright and draw a lot of current
CAM_W, CAM_H = 320, 240  # HuskyLens screen size

CHANNEL = "ball"
POLL_INTERVAL = 0.2
STALE_AFTER = 2.0  # seconds without camera data before it counts as offline

GREEN = (0, 255, 0)
RED = (80, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 80, 0)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

pixels = neopixel.NeoPixel(PIXEL_PIN, WIDTH * HEIGHT, brightness=BRIGHTNESS, auto_write=False)


def index(x, y):
    """STAGE 1: return the pixel number for column x (0-31, left to right)
    and row y (0-7, top to bottom).
    Use the "chase" mode to see the order the pixels are wired in, then
    work out the formula. Hint: it is different for even and odd columns."""
    # TODO
    return 0


def set_xy(x, y, colour):
    pixels[index(x, y)] = colour


def chase():
    """Given: lights each pixel in turn and prints its number."""
    for i in range(WIDTH * HEIGHT):
        pixels.fill(OFF)
        pixels[i] = WHITE
        pixels.show()
        print("pixel", i)
        time.sleep(0.15)


def test_pattern():
    """Given: if index() is right you get a red top row, a blue left
    column and one green pixel in the bottom-right corner."""
    pixels.fill(OFF)
    for x in range(WIDTH):
        set_xy(x, 0, RED)
    for y in range(HEIGHT):
        set_xy(0, y, BLUE)
    set_xy(WIDTH - 1, HEIGHT - 1, GREEN)
    pixels.show()


def to_range(centre, size, cam_size, cells):
    """STAGE 2: which panel cells cover a box on the camera, as a range.
    The box goes from centre - size/2 to centre + size/2 in camera pixels.
    Scale both ends by cells / cam_size, then return range(start, end).
    e.g. centre 160, size 64, cam_size 320, cells 32 -> range(12, 20)
    Make sure start and end stay inside 0..cells and the range is never empty."""
    # TODO
    return range(0, 1)


def draw_ball(ball):
    """STAGE 2: light every cell the ball's box covers in GREEN.
    Use to_range() for the columns (x, w, CAM_W, WIDTH) and the rows
    (y, h, CAM_H, HEIGHT) and two nested for loops."""
    # TODO
    pass


def show(ball, age, blink):
    """Draw the right picture for what the server told us.
    STAGE 2: draws the ball, or a red dot if not seen.
    STAGE 4: add the other states from docs/role_led_panel.md:
      ball is None              -> orange dot (server unreachable)
      age is None or too old    -> blinking blue dot (camera offline)"""
    pixels.fill(OFF)
    if ball.get("seen"):
        draw_ball(ball)
    else:
        set_xy(0, 0, RED)
    pixels.show()


FAKE_BALLS = [
    {"seen": True, "x": 160, "y": 120, "w": 64, "h": 60},  # middle
    {"seen": True, "x": 20, "y": 20, "w": 40, "h": 40},    # top-left
    {"seen": True, "x": 300, "y": 220, "w": 40, "h": 40},  # bottom-right
    {"seen": True, "x": 160, "y": 120, "w": 320, "h": 240},  # fills the screen
    {"seen": False},
]

if MODE == "chase":
    while True:
        chase()

elif MODE == "test_pattern":
    test_pattern()
    while True:
        time.sleep(1)

elif MODE == "fake_ball":
    while True:
        for fake in FAKE_BALLS:
            print(fake)
            show(fake, 0, True)
            time.sleep(2)

else:
    # STAGE 3: create a PicoComs called "led_panel" and connect to Wi-Fi.
    # Then, forever:
    #   ball = coms.get(CHANNEL)     -> dict, or None if the server can't be reached
    #   show(ball, coms.age, blink)  -> coms.age is how old the data is
    #   flip `blink` between True and False each time round
    #   time.sleep(POLL_INTERVAL)
    pass
