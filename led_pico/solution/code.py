# LED panel Pico 2 W - SOLUTION (CircuitPython)
# Reads the ball channel from the server using PicoComs and shows it on an
# 8x32 NeoPixel panel.
#
#   Green box   = ball detected (position and size match the camera view)
#   Red dot     = camera working, no ball
#   Blue blink  = server reachable but camera offline
#   Orange dot  = can't reach the server / Wi-Fi
#
# CIRCUITPY/lib needs: everything in pico_lib/, neopixel.mpy, adafruit_pixelbuf.mpy,
#                      adafruit_requests.mpy, adafruit_connection_manager.mpy
# CIRCUITPY/settings.toml needs: WIFI_SSID, WIFI_PASSWORD, SERVER_URL

import math
import time

import board
import neopixel
from pico_coms import PicoComs

# "chase"        stage 1: light pixels 0, 1, 2... in order to see how the panel is wired
# "test_pattern" stage 1: check index(x, y) - see docs/role_led_panel.md
# "fake_ball"    stage 2: draw made-up balls without needing the server
# "server"       stage 3+: show the real ball from the server
MODE = "server"

WIDTH, HEIGHT = 32, 8
PIXEL_PIN = board.GP0
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
    """Pixel number for column x (0-31, left to right) and row y (0-7, top
    to bottom). This panel runs down column 0, up column 1, down column 2...
    If your panel is wired differently, the chase test shows how."""
    if x % 2 == 0:
        return x * HEIGHT + y
    return x * HEIGHT + (HEIGHT - 1 - y)


def set_xy(x, y, colour):
    pixels[index(x, y)] = colour


def chase():
    for i in range(WIDTH * HEIGHT):
        pixels.fill(OFF)
        pixels[i] = WHITE
        pixels.show()
        print("pixel", i)
        time.sleep(0.15)


def test_pattern():
    """Top row red, left column blue, bottom-right corner green."""
    pixels.fill(OFF)
    for x in range(WIDTH):
        set_xy(x, 0, RED)
    for y in range(HEIGHT):
        set_xy(0, y, BLUE)
    set_xy(WIDTH - 1, HEIGHT - 1, GREEN)
    pixels.show()


def to_range(centre, size, cam_size, cells):
    """Which panel cells (as a range) cover a box edge-to-edge on the camera.
    e.g. centre 160, size 64, cam_size 320, cells 32 -> range(12, 20)"""
    start = int((centre - size / 2) * cells / cam_size)
    end = math.ceil((centre + size / 2) * cells / cam_size)
    start = max(0, min(cells - 1, start))
    end = max(start + 1, min(cells, end))
    return range(start, end)


def draw_ball(ball):
    for x in to_range(ball["x"], ball["w"], CAM_W, WIDTH):
        for y in to_range(ball["y"], ball["h"], CAM_H, HEIGHT):
            set_xy(x, y, GREEN)


def show(ball, age, blink):
    """Draw the right picture for what the server told us."""
    pixels.fill(OFF)
    if ball is None:
        set_xy(0, 0, ORANGE)
    elif age is None or age > STALE_AFTER:
        if blink:
            set_xy(0, 0, BLUE)
    elif ball.get("seen"):
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
    coms = PicoComs(name="led_panel")
    pixels.fill(OFF)
    set_xy(0, 0, ORANGE)
    pixels.show()
    coms.connect()
    blink = False
    while True:
        ball = coms.get(CHANNEL)
        if ball is None:
            print("Get failed:", coms.last_error)
        blink = not blink
        show(ball, coms.age, blink)
        time.sleep(POLL_INTERVAL if ball is not None else 1)
