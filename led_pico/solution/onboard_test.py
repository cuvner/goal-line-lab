# LED Pico 2 W - onboard LED test (CircuitPython)
# Copy to CIRCUITPY/code.py to test comms before the NeoPixel panel is wired.
# Reads the "ball" channel from the Pi server using PicoComs.
#
#   LED on          = ball detected
#   LED off         = camera working, no ball
#   Slow blink      = server reachable but camera offline
#   Fast blink      = can't reach the server / Wi-Fi
#
# CIRCUITPY/lib needs: pico_coms.py, adafruit_requests.mpy, adafruit_connection_manager.mpy

import time

import board
import digitalio
from pico_coms import PicoComs

POLL_INTERVAL = 0.2
STALE_AFTER = 2.0

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


def blink(times, delay):
    for _ in range(times):
        led.value = True
        time.sleep(delay)
        led.value = False
        time.sleep(delay)


coms = PicoComs(name="led_panel")
coms.connect()
last_state = None

while True:
    ball = coms.get("ball")
    if ball is None:
        state = "server unreachable: " + str(coms.last_error)
        blink(5, 0.1)
    elif coms.age is None or coms.age > STALE_AFTER:
        state = "camera offline"
        blink(1, 0.5)
    else:
        state = "ball seen" if ball.get("seen") else "no ball"
        led.value = bool(ball.get("seen"))
        time.sleep(POLL_INTERVAL)
    if state != last_state:
        print(state, ball)
        last_state = state
