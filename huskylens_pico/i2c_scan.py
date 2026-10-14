# HuskyLens role - STAGE 1: check the wiring. (Given)
# Copy this to CIRCUITPY/code.py. It lists every I2C device it can find.
# The HuskyLens should appear as 0x32.

import time

import board
import busio

while True:
    try:
        i2c = busio.I2C(scl=board.GP17, sda=board.GP16)
    except RuntimeError as e:
        # "No pull up found on SDA or SCL" = HuskyLens not powered or wires on the wrong pins
        print("I2C error:", e)
        time.sleep(2)
        continue
    while not i2c.try_lock():
        pass
    found = [hex(address) for address in i2c.scan()]
    i2c.unlock()
    i2c.deinit()
    print("I2C devices found:", found)
    if "0x32" in found:
        print("HuskyLens found! Move on to stage 2.")
    time.sleep(2)
