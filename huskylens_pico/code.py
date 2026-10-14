# HuskyLens Pico 2 W - STARTER (HuskyLens role)
# Work through stages 3-5 in docs/role_huskylens.md.
#
# Wiring (HuskyLens "I2C" 4-pin cable):
#   HuskyLens T (SDA, green) -> GP16 (pin 21)
#   HuskyLens R (SCL, blue)  -> GP17 (pin 22)
#   HuskyLens -  (black)     -> GND  (pin 23)
#   HuskyLens +  (red)       -> 3V3(OUT) (pin 36)
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
    """STAGE 4: return the ball's block, or None if it isn't there.
    `blocks` is a list of dicts like {"x": 160, "y": 120, "w": 40, "h": 40, "id": 1}.
    Only blocks with id == BALL_ID are the ball. If there are several,
    return the biggest (largest w * h)."""
    # TODO
    return None


def make_reading(ball):
    """STAGE 4: build the JSON object to send (see docs/protocol.md):
      no ball  -> {"seen": False}
      ball     -> {"seen": True, "x": ..., "y": ..., "w": ..., "h": ..., "id": ...}"""
    # TODO
    return {"seen": False}


# STAGE 4: create a PicoComs called "huskylens" and connect it to the Wi-Fi
#   coms = PicoComs(name="huskylens")
#   coms.connect()

camera.connect(HuskyLens.OBJECT_TRACKING)

while True:
    # STAGE 5: if the HuskyLens is unplugged, get_blocks() raises OSError or
    # ValueError and the program crashes. Catch it, print the error, turn the
    # LED off, wait 0.5 s and `continue` the loop instead.
    blocks = camera.get_blocks()

    # STAGE 3: watch these numbers as you move the ball around.
    print(blocks)

    reading = make_reading(choose_ball(blocks))

    # STAGE 4: send `reading` to CHANNEL with coms.send(...).
    #          It returns False if it fails: print coms.last_error if so.

    # STAGE 5: turn the onboard LED on while the ball is seen (led.value = ...)

    time.sleep(READ_INTERVAL)
