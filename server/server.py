#!/usr/bin/env python3
"""Goal-line Lab server. GIVEN: students don't need to edit this file.

The Referee student edits referee.py. This server reloads referee.py as
soon as it's saved, so there's no need to restart anything.

Run:  python3 server.py               then open http://<pi-ip>:8080/
      python3 server.py --http 8081   (on another port)

How it works (for the curious):
The Picos talk to this server with HTTP, the same language web browsers use.
    POST /data/<channel>   a Pico sends a JSON message, which is stored
    GET  /data/<channel>   a Pico asks for the latest message
    GET  /data             every channel
    GET  /stats            everything the dashboard shows
    GET  /                 the dashboard web page
referee.py's who_is() says which device each IP address belongs to (from
devices.txt). Only the "camera" may send to the "ball" channel, and only
the "scoreboard" may read the "referee" channel. When the camera sends
the ball, the server asks referee.py for a decision and stores it on
the "referee" channel.
"""

import argparse
import importlib.util
import json
import os
import re
import threading
import time
import traceback
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE_FILE = os.path.join(HERE, "dashboard.html")
REFEREE_FILE = os.path.join(HERE, "referee.py")
DEVICES_FILE = os.path.join(HERE, "devices.txt")

CHANNEL = re.compile(r"^/data/([A-Za-z0-9_-]{1,32})$")
MAX_BODY = 4096
GOAL_SHOW_SECONDS = 3.0  # how long GOAL stays on the dashboard and scoreboard after a goal
# Who may send to / read from which channel (who_is() decides who's who)
SEND_ONLY = {"ball": "camera"}
READ_ONLY = {"referee": "scoreboard"}
RATE_WINDOW = 5.0  # seconds used to work out messages per second
QUIET_AFTER = 5.0  # seconds of silence before a returning client is logged

started = time.time()
channels = {}        # name -> (data, time received)
channel_times = {}   # name -> recent update times
channel_counts = {}  # name -> total updates
clients = {}         # ip -> stats dict
events = deque(maxlen=50)
lock = threading.RLock()
referee_lock = threading.Lock()  # one referee decision at a time


def log_event(text):
    with lock:
        events.append((time.time(), text))
    print(time.strftime("%H:%M:%S"), text, flush=True)


def store(name, data):
    now = time.time()
    with lock:
        if name not in channels:
            log_event(f"new channel '{name}'")
            channel_times[name] = deque(maxlen=200)
            channel_counts[name] = 0
        channels[name] = (data, now)
        channel_times[name].append(now)
        channel_counts[name] += 1


# ---------------------------------------------------------------- referee

class Referee:
    """Loads referee.py (again whenever it changes) and runs it safely, so a
    mistake in the student's code shows up on the dashboard instead of
    crashing the server."""

    def __init__(self):
        self.module = None
        self.mtime = None
        self.devices = []
        self.devices_mtime = None
        self.rejected = set()  # (ip, channel) pairs already logged
        self.problem = None  # last problem text, so it's only logged once
        self.decision = "NO BALL"   # what's shown (GOAL only for GOAL_SHOW_SECONDS)
        self.raw_decision = "NO BALL"  # what decide() last said (used for scoring)
        self.goal_time = 0.0
        self.score = 0
        self.commentary = ""

    def report(self, text):
        if text != self.problem:
            self.problem = text
            log_event("referee.py problem: " + text)

    def reload_if_changed(self):
        try:
            mtime = os.path.getmtime(REFEREE_FILE)
        except OSError:
            self.report("referee.py is missing")
            self.module = None
            return
        if mtime == self.mtime:
            return
        self.mtime = mtime
        try:
            spec = importlib.util.spec_from_file_location("referee", REFEREE_FILE)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except SyntaxError as e:
            self.module = None
            self.report(f"line {e.lineno}: {e.msg}")
            return
        except Exception as e:
            self.module = None
            self.report(explain(e))
            return
        self.module = module
        self.problem = None
        self.devices_mtime = None  # reload the address book with the new code
        log_event("referee.py loaded")

    def reload_devices_if_changed(self):
        try:
            mtime = os.path.getmtime(DEVICES_FILE)
        except OSError:
            mtime = None
        if mtime == self.devices_mtime or self.module is None:
            return
        self.devices_mtime = mtime
        try:
            devices = self.module.load_devices("devices.txt")
            if not isinstance(devices, list):
                raise TypeError(f"load_devices gave back {devices!r}, but it should be a list")
        except Exception as e:
            self.report(explain(e))
            return
        self.devices = devices
        self.rejected.clear()
        log_event(f"address book: {len(devices)} device(s) loaded from devices.txt")

    def who_is(self, ip):
        """The device name for an IP address, using the student's who_is()."""
        self.reload_if_changed()
        self.reload_devices_if_changed()
        if self.module is None:
            return "unknown"
        try:
            name = self.module.who_is(ip, self.devices)
        except Exception as e:
            self.report(explain(e))
            return "unknown"
        return str(name)

    def allowed(self, ip, channel, rules, verb):
        """Is `ip` allowed to send to / read from `channel`? Logs refusals once."""
        needed = rules.get(channel)
        if needed is None:
            return True
        name = self.who_is(ip)
        if name == needed:
            return True
        if (ip, channel) not in self.rejected:
            self.rejected.add((ip, channel))
            log_event(f"turned away {ip}: only the {needed} may {verb} '{channel}', "
                      f"but who_is() says it's {name!r}. Is it in devices.txt?")
        return False

    def run(self, ball):
        """Called for every message on the "ball" channel."""
        seen = bool(ball.get("seen")) if isinstance(ball, dict) else False
        x = ball.get("x", 0) if seen else 0
        y = ball.get("y", 0) if seen else 0
        line = getattr(self.module, "GOAL_LINE", None)
        if self.module is None:
            decision = "REFEREE ERROR"
        else:
            try:
                decision = self.module.decide(seen, x)
                score = self.module.new_score(self.score, self.raw_decision, decision)
                if not isinstance(score, int):
                    raise TypeError(f"new_score gave back {score!r}, but it should be a whole number")
                if decision != self.raw_decision:
                    self.commentary = self.module.commentary(decision, score)
                if score > self.score:
                    self.goal_time = time.time()
                self.score = score
                self.raw_decision = decision
                # Show GOAL for a few seconds, then go back to the score even if the ball stays over the line
                if decision == "GOAL" and time.time() - self.goal_time > GOAL_SHOW_SECONDS:
                    decision = "NO GOAL"
                if self.problem:
                    self.problem = None
                    log_event("referee.py working again")
            except Exception as e:
                decision = "REFEREE ERROR"
                self.report(explain(e))
        if decision != self.decision:
            log_event(f"referee: {decision}" + (f" (score {self.score})" if decision == "GOAL" else ""))
        self.decision = decision
        store("referee", {
            "decision": str(decision), "score": self.score, "commentary": str(self.commentary or ""),
            "seen": seen, "x": x, "y": y, "line": line if isinstance(line, (int, float)) else None,
        })


def explain(error):
    """A short, friendly description of an error in referee.py, with its line number."""
    line = ""
    for frame in traceback.extract_tb(error.__traceback__):
        if os.path.abspath(frame.filename) == REFEREE_FILE:
            line = f"line {frame.lineno}: "
    return f"{line}{type(error).__name__}: {error}"


referee = Referee()


def who_is(ip):
    with referee_lock:
        return referee.who_is(ip)


def allowed(ip, channel, rules, verb):
    with referee_lock:
        return referee.allowed(ip, channel, rules, verb)


# ---------------------------------------------------------------- stats

def rate(times, now):
    return sum(1 for t in times if now - t < RATE_WINDOW) / RATE_WINDOW


def record_request(handler, status):
    ip = handler.client_address[0]
    name = who_is(ip)
    if name == "unknown":
        name = "unknown (" + (handler.headers.get("X-Pico-Name") or "?") + ")"
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
        if status not in (200, 403):  # 403s are explained once by Referee.allowed()
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


# ---------------------------------------------------------------- web

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
            name = match.group(1)
            if not allowed(self.client_address[0], name, READ_ONLY, "read"):
                self.send_body({"error": "the server doesn't know who you are"}, status=403)
                record_request(self, 403)
                return
            self.send_body(read_channel(name))
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
        if not allowed(self.client_address[0], name, SEND_ONLY, "send to"):
            self.send_body({"error": "the server doesn't know who you are"}, status=403)
            record_request(self, 403)
            return
        store(name, data)
        if name == "ball":
            with referee_lock:
                referee.run(data)
        self.send_body({"ok": True})
        record_request(self, 200)

    def log_message(self, *args):
        pass  # the Picos send several messages a second; keep the console quiet


class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        """A Pico dropping a connection mid-request (Wi-Fi blip) isn't worth a traceback."""
        import sys
        error = sys.exc_info()[1]
        if isinstance(error, (ConnectionResetError, BrokenPipeError, TimeoutError)):
            return
        super().handle_error(request, client_address)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", type=int, default=8080, help="port")
    args = parser.parse_args()
    os.chdir(HERE)  # so referee.py can open devices.txt and commentary.txt
    who_is("127.0.0.1")  # load referee.py and devices.txt now
    server = QuietServer(("0.0.0.0", args.http), Handler)
    print(f"Goal-line Lab server on port {args.http}. Find the Pi's address with: hostname -I")
    server.serve_forever()


if __name__ == "__main__":
    main()
