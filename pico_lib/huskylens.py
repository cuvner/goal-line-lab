# HuskyLens (v1) I2C driver for CircuitPython. GIVEN FILE: copy to CIRCUITPY/lib/
#
# Usage:
#   import board, busio
#   from huskylens import HuskyLens
#   i2c = busio.I2C(scl=board.GP17, sda=board.GP16)
#   camera = HuskyLens(i2c)
#   camera.connect(HuskyLens.OBJECT_TRACKING)
#   camera.get_blocks()   # [{"x": 160, "y": 120, "w": 40, "h": 40, "id": 1}, ...]
#
# x, y are the CENTRE of the box on the HuskyLens screen, which is 320 x 240
# pixels with (0, 0) at the top-left. w, h are the box's width and height.
#
# How the protocol works (for the curious):
# every message is a "frame" of bytes:
#   55 AA 11 <length> <command> <data...> <checksum>
# checksum = sum of all the earlier bytes, keeping only the lowest 8 bits.
# Numbers in the data are 16-bit little-endian (low byte first).

import struct
import time

_REQUEST_BLOCKS = 0x21
_RETURN_INFO = 0x29
_RETURN_BLOCK = 0x2A
_REQUEST_KNOCK = 0x2C
_REQUEST_ALGORITHM = 0x2D
_RETURN_OK = 0x2E


class HuskyLens:
    FACE_RECOGNITION = 0
    OBJECT_TRACKING = 1
    OBJECT_RECOGNITION = 2
    LINE_TRACKING = 3
    COLOR_RECOGNITION = 4
    TAG_RECOGNITION = 5
    OBJECT_CLASSIFICATION = 6

    WIDTH = 320
    HEIGHT = 240

    def __init__(self, i2c, address=0x32):
        self.i2c = i2c
        self.address = address

    def connect(self, algorithm, retries=None):
        """Check the HuskyLens answers and switch it to an algorithm.
        Keeps retrying (retries=None) until it works."""
        attempt = 0
        while True:
            try:
                self._transaction(_REQUEST_KNOCK)
                self._transaction(_REQUEST_ALGORITHM, struct.pack("<H", algorithm))
                print("HuskyLens connected")
                return True
            except (OSError, ValueError) as e:
                attempt += 1
                print("HuskyLens connect failed:", e)
                if retries is not None and attempt > retries:
                    return False
                time.sleep(1)

    def get_blocks(self):
        """Every box the HuskyLens can see right now, as a list of dicts.
        Raises OSError or ValueError if the HuskyLens doesn't answer."""
        blocks = []
        for command, data in self._transaction(_REQUEST_BLOCKS, reply=_RETURN_INFO)[1:]:
            if command == _RETURN_BLOCK and len(data) >= 10:
                x, y, w, h, obj_id = struct.unpack("<5H", data[:10])
                blocks.append({"x": x, "y": y, "w": w, "h": h, "id": obj_id})
        return blocks

    # ---- protocol details ----

    def _packet(self, command, data=b""):
        packet = bytes([0x55, 0xAA, 0x11, len(data), command]) + data
        return packet + bytes([sum(packet) & 0xFF])

    def _read_frame(self, timeout=1.0):
        """Read one reply frame -> (command, data). Skips bytes until the
        55 AA header, because the HuskyLens can take a moment to answer."""
        deadline = time.monotonic() + timeout
        byte = bytearray(1)
        previous = 0
        while not (previous == 0x55 and byte[0] == 0xAA):
            if time.monotonic() > deadline:
                raise ValueError("no reply")
            previous = byte[0]
            self.i2c.readfrom_into(self.address, byte)
        header = bytearray(3)  # address, length, command
        self.i2c.readfrom_into(self.address, header)
        length, command = header[1], header[2]
        rest = bytearray(length + 1)  # data + checksum
        self.i2c.readfrom_into(self.address, rest)
        if (0x55 + 0xAA + sum(header) + sum(rest[:-1])) & 0xFF != rest[-1]:
            raise ValueError("bad checksum")
        return command, bytes(rest[:-1])

    def _transaction(self, command, data=b"", reply=_RETURN_OK):
        """Send a command and return its reply frames, skipping stale frames
        left over from an earlier command."""
        while not self.i2c.try_lock():
            pass
        try:
            self.i2c.writeto(self.address, self._packet(command, data))
            first = self._read_frame()
            while first[0] != reply:
                first = self._read_frame()
            frames = [first]
            if reply == _RETURN_INFO:
                count = first[1][0] | (first[1][1] << 8)
                for _ in range(min(count, 10)):
                    frames.append(self._read_frame())
            return frames
        finally:
            self.i2c.unlock()
