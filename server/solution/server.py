#!/usr/bin/env python3
"""Goal-line Lab Pi server (SOLUTION).

A general-purpose data store for Pico W clients using PicoComs.
Any client can write to or read from a named channel:

    POST /data/<channel>   body: JSON      -> {"ok": true}
    GET  /data/<channel>                   -> {"data": <JSON or null>, "age": <seconds or null>}
    GET  /data                             -> every channel and its age
    GET  /stats                            -> comms stats for dashboard.html / terminal_dashboard.py
    GET  /                                 -> live web dashboard (camera, clients, channels, events)

Run:  python3 server.py              (standard library only, port 8080)
      python3 server.py --http 8081  (as the reference server during lessons)
"""

import argparse
import json
import os
import re
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CHANNEL = re.compile(r"^/data/([A-Za-z0-9_-]{1,32})$")
MAX_BODY = 4096
RATE_WINDOW = 5.0  # seconds used to work out requests per second
QUIET_AFTER = 5.0  # seconds of silence before a returning client is logged

started = time.time()
channels = {}       # name -> (data, time received)
channel_times = {}  # name -> recent update times
channel_counts = {}  # name -> total updates
clients = {}        # ip -> stats dict
events = deque(maxlen=50)
lock = threading.Lock()


def log_event(text):
    """Must be called with lock held."""
    events.append((time.time(), text))
    print(time.strftime("%H:%M:%S"), text, flush=True)


def rate(times, now):
    return sum(1 for t in times if now - t < RATE_WINDOW) / RATE_WINDOW


def record_request(handler, status):
    ip = handler.client_address[0]
    name = handler.headers.get("X-Pico-Name", "")
    now = time.time()
    with lock:
        client = clients.get(ip)
        if client is None:
            client = clients[ip] = {
                "name": name, "ip": ip, "last": now, "posts": 0, "gets": 0,
                "errors": 0, "times": deque(maxlen=200),
            }
            log_event(f"new client {name or ip} ({ip})")
        elif now - client["last"] > QUIET_AFTER:
            log_event(f"{client['name'] or ip} back after {now - client['last']:.0f}s")
        client["name"] = name or client["name"]
        client["last"] = now
        client["times"].append(now)
        client["posts" if handler.command == "POST" else "gets"] += 1
        if status != 200:
            client["errors"] += 1
            log_event(f"{client['name'] or ip} {handler.command} {handler.path} -> {status}")


def stats():
    now = time.time()
    with lock:
        return {
            "uptime": round(now - started),
            "clients": [
                {
                    "name": c["name"], "ip": c["ip"], "age": round(now - c["last"], 2),
                    "rate": rate(c["times"], now), "posts": c["posts"],
                    "gets": c["gets"], "errors": c["errors"],
                }
                for c in clients.values()
            ],
            "channels": [
                {
                    "name": name, "age": round(now - received, 2),
                    "rate": rate(channel_times[name], now),
                    "updates": channel_counts[name], "data": data,
                }
                for name, (data, received) in channels.items()
            ],
            "events": list(events)[-20:],
        }


def read_channel(name):
    with lock:
        if name not in channels:
            return {"data": None, "age": None}
        data, received = channels[name]
    return {"data": data, "age": round(time.time() - received, 2)}


def find_page():
    """dashboard.html sits next to server.py, or one folder up (from solution/)."""
    here = os.path.dirname(os.path.abspath(__file__))
    for folder in (here, os.path.dirname(here)):
        path = os.path.join(folder, "dashboard.html")
        if os.path.exists(path):
            return path
    raise FileNotFoundError("dashboard.html not found next to server.py")


PAGE_FILE = find_page()


class Handler(BaseHTTPRequestHandler):
    def send_body(self, body, content_type="application/json", status=200):
        if not isinstance(body, bytes):
            body = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            with open(PAGE_FILE, "rb") as f:
                self.send_body(f.read(), "text/html")
        elif self.path == "/stats":
            self.send_body(stats())
        elif self.path == "/data":
            with lock:
                names = list(channels)
            self.send_body({name: read_channel(name) for name in names})
        elif match := CHANNEL.match(self.path):
            self.send_body(read_channel(match.group(1)))
            record_request(self, 200)
        else:
            self.send_body({"error": "not found"}, status=404)

    def do_POST(self):
        match = CHANNEL.match(self.path)
        if not match:
            self.send_body({"error": "not found"}, status=404)
            return
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY:
            self.send_body({"error": "too large"}, status=413)
            record_request(self, 413)
            return
        try:
            data = json.loads(self.rfile.read(length))
        except ValueError:
            self.send_body({"error": "invalid JSON"}, status=400)
            record_request(self, 400)
            return
        name = match.group(1)
        now = time.time()
        with lock:
            if name not in channels:
                log_event(f"new channel '{name}'")
                channel_times[name] = deque(maxlen=200)
                channel_counts[name] = 0
            channels[name] = (data, now)
            channel_times[name].append(now)
            channel_counts[name] += 1
        self.send_body({"ok": True})
        record_request(self, 200)

    def log_message(self, *args):
        pass  # the Picos send several requests a second; keep the console quiet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", type=int, default=8080, help="HTTP port")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.http), Handler)
    print(f"Serving on http://0.0.0.0:{args.http}  (find the Pi's IP with: hostname -I)")
    server.serve_forever()


if __name__ == "__main__":
    main()
