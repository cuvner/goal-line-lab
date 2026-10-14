#!/usr/bin/env python3
"""Goal-line Lab server - STARTER (Server role).

Work through the stages in docs/role_server.md. After each stage, restart
the server and check your work:

    python3 server.py                                   (Ctrl+C to stop)
    python3 ../tools/check_server.py --stage 1          (in a second terminal)

The full API this server must provide is in docs/protocol.md.
"""

import json
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080
PAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")

# Matches paths like /data/ball and captures the channel name ("ball")
CHANNEL = re.compile(r"^/data/([A-Za-z0-9_-]{1,32})$")

# The latest data on each channel: name -> (data, time.time() when received)
# One test channel is already filled in so you can try GET before POST works.
channels = {"test": ({"hello": "world"}, time.time())}

# Requests are handled on several threads at once, so use this lock
# whenever you read or change `channels`:   with lock: ...
lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):

    def send_json(self, obj, status=200):
        """Send any JSON-able Python value back to the client. (Given)"""
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            # ---------------- STAGE 1 ----------------
            # Send dashboard.html to the browser:
            #   1. read PAGE_FILE as bytes  (open(PAGE_FILE, "rb"))
            #   2. self.send_response(200)
            #   3. self.send_header("Content-Type", "text/html")
            #   4. self.send_header("Content-Length", <number of bytes>)
            #   5. self.end_headers()
            #   6. self.wfile.write(<the bytes>)
            self.send_json({"error": "TODO: stage 1"}, status=501)

        elif self.path == "/data":
            # ---------------- STAGE 4 ----------------
            # Reply with EVERY channel, e.g.
            #   {"ball": {"data": {...}, "age": 0.12}, "test": {...}}
            # Tip: write a helper that builds {"data": ..., "age": ...} for one
            # channel name, and use it here and in stage 2.
            self.send_json({"error": "TODO: stage 4"}, status=501)

        elif (match := CHANNEL.match(self.path)):
            name = match.group(1)
            # ---------------- STAGE 2 ----------------
            # Reply with the latest data on channel `name` and its age:
            #   {"data": <the data>, "age": <seconds since it arrived, 2 d.p.>}
            # If nothing has been sent to that channel yet:
            #   {"data": None, "age": None}      (json.dumps turns None into null)
            self.send_json({"error": "TODO: stage 2"}, status=501)

        else:
            self.send_json({"error": "not found"}, status=404)

    def do_POST(self):
        match = CHANNEL.match(self.path)
        if not match:
            self.send_json({"error": "not found"}, status=404)
            return
        name = match.group(1)
        # ---------------- STAGE 3 ----------------
        # Store the JSON a client sends to /data/<name>:
        #   1. length = int(self.headers.get("Content-Length", 0))
        #   2. body = self.rfile.read(length)
        #   3. data = json.loads(body)  -> if it raises ValueError, reply
        #      {"error": "invalid JSON"} with status 400 and stop
        #   4. store (data, time.time()) in channels[name]  (use the lock!)
        #   5. reply {"ok": True}
        self.send_json({"error": "TODO: stage 3"}, status=501)

    # ---------------- STAGE 5 (extension) ----------------
    # Add GET /stats so the dashboard can show CLIENTS and EVENTS.
    # The exact format is in docs/protocol.md.

    # Once everything works, uncomment this to stop every request being
    # printed (the Picos send several a second):
    # def log_message(self, *args):
    #     pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Serving on port {PORT}. Find this computer's IP address with: hostname -I")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
