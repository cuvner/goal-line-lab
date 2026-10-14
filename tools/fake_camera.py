#!/usr/bin/env python3
"""Pretend to be the HuskyLens Pico: sends a ball bouncing around the
camera view to a server, 10 times a second. Use it to test the server or
the LED panel before the real camera is ready.

    python3 fake_camera.py --url http://<server-ip>:8080
    python3 fake_camera.py --url http://<server-ip>:8081 --channel ball

Every 8 seconds the ball "disappears" for 2 seconds. Ctrl+C to stop.
Standard library only.
"""

import argparse
import json
import time
import urllib.error
import urllib.request

CAM_W, CAM_H = 320, 240
SIZE = 50


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8080")
    parser.add_argument("--channel", default="ball")
    args = parser.parse_args()
    url = f"{args.url.rstrip('/')}/data/{args.channel}"

    x, y, dx, dy = 160.0, 120.0, 9.0, 5.0
    start = time.time()
    print(f"Sending to {url}  (Ctrl+C to stop)")
    while True:
        x += dx
        y += dy
        if not SIZE / 2 <= x <= CAM_W - SIZE / 2:
            dx = -dx
        if not SIZE / 2 <= y <= CAM_H - SIZE / 2:
            dy = -dy
        seen = (time.time() - start) % 10 < 8
        reading = {"seen": True, "x": int(x), "y": int(y), "w": SIZE, "h": SIZE, "id": 1} if seen else {"seen": False}
        req = urllib.request.Request(url, data=json.dumps(reading).encode(), method="POST",
                                     headers={"Content-Type": "application/json", "X-Pico-Name": "fake_camera"})
        try:
            with urllib.request.urlopen(req, timeout=2) as r:
                r.read()
            print("\rsent", json.dumps(reading).ljust(70), end="", flush=True)
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            print("\rsend failed:", str(e).ljust(60), end="", flush=True)
            time.sleep(1)
        time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
