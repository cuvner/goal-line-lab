# HuskyLens Pico 2 W - SOLUTION (CircuitPython)
# Reads the HuskyLens over I2C and sends each reading to the server
# over Wi-Fi using PicoComs.
#
# Wiring (HuskyLens "I2C" 4-pin cable):
#   HuskyLens T (SDA, green) -> GP16 (pin 21)
#   HuskyLens R (SCL, blue)  -> GP17 (pin 22)
#   HuskyLens -  (black)     -> GND  (pin 23)
#   HuskyLens +  (red)       -> 3V3(OUT) (pin 36)
# On the HuskyLens: General Settings > Protocol Type > I2C
# CIRCUITPY/lib needs: everything in pico_lib/, adafruit_requests.mpy, adafruit_connection_manager.mpy
# CIRCUITPY/settings.toml needs: WIFI_SSID, WIFI_PASSWORD, SERVER_URL

import time

import board
import busio
import digitalio
from huskylens import HuskyLens
from pico_coms import PicoComs

BALL_ID = 1          # ID the football was learned as
CHANNEL = "ball"     # server channel to send readings to
READ_INTERVAL = 0.1  # seconds between readings

i2c = busio.I2C(scl=board.GP17, sda=board.GP16)
camera = HuskyLens(i2c)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


def choose_ball(blocks):
    """The ball's block (the biggest one with BALL_ID), or None."""
    balls = [b for b in blocks if b["id"] == BALL_ID]
    if not balls:
        return None
    return max(balls, key=lambda b: b["w"] * b["h"])


def make_reading(ball):
    """The JSON object to send. See docs/protocol.md."""
    if ball is None:
        return {"seen": False}
    reading = dict(ball)
    reading["seen"] = True
    return reading


coms = PicoComs(name="huskylens")
coms.connect()
camera.connect(HuskyLens.OBJECT_TRACKING)

while True:
    try:
        blocks = camera.get_blocks()
    except (OSError, ValueError) as e:
        # Send nothing: the server shows the camera offline when data goes stale
        print("HuskyLens read failed:", e)
        led.value = False
        time.sleep(0.5)
        continue
    reading = make_reading(choose_ball(blocks))
    led.value = reading["seen"]
    if not coms.send(CHANNEL, reading):
        print("Send failed:", coms.last_error)
    time.sleep(READ_INTERVAL)
