#!/usr/bin/env python3
"""Check a Goal-line Lab server against docs/protocol.md, stage by stage.

    python3 check_server.py --stage 3
    python3 check_server.py --stage 5 --url http://10.0.0.5:8080

Runs every check up to and including the stage you give. Standard library only.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

NAME = "check_server"


def request(url, method="GET", body=None):
    """-> (status, parsed JSON or raw text)"""
    data = body.encode() if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"X-Pico-Name": NAME, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=3) as r:
            status, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    text = raw.decode(errors="replace")
    try:
        return status, json.loads(text)
    except ValueError:
        return status, text


class Checker:
    def __init__(self, url):
        self.url = url
        self.failed = 0

    def check(self, label, ok, detail=""):
        print(("  PASS  " if ok else "  FAIL  ") + label + ("" if ok else f"\n        {detail}"))
        if not ok:
            self.failed += 1
        return ok


def stage1(c):
    status, body = request(c.url + "/")
    c.check("GET / returns 200", status == 200, f"got HTTP {status}: {str(body)[:100]}")
    c.check("GET / returns the dashboard HTML", isinstance(body, str) and "<html" in body.lower(),
            f"got: {str(body)[:100]}")


def stage2(c):
    status, body = request(c.url + "/data/nothing_sent_here")
    c.check("GET /data/<unused channel> returns 200", status == 200, f"got HTTP {status}: {body}")
    c.check('...with {"data": null, "age": null}', body == {"data": None, "age": None}, f"got: {body}")
    status, body = request(c.url + "/data/test")
    if status == 200 and isinstance(body, dict) and body.get("data") is not None:
        c.check('GET /data/test has a number for "age"', isinstance(body.get("age"), (int, float)), f"got: {body}")


def stage3(c):
    sent = {"seen": True, "x": 123, "y": 45, "w": 10, "h": 12, "id": 1, "stamp": time.time()}
    status, body = request(c.url + "/data/check", "POST", json.dumps(sent))
    c.check("POST /data/check returns 200", status == 200, f"got HTTP {status}: {body}")
    c.check('...with {"ok": true}', body == {"ok": True}, f"got: {body}")
    status, body = request(c.url + "/data/check")
    c.check("GET /data/check returns what was sent", isinstance(body, dict) and body.get("data") == sent,
            f"sent {sent}\n        got  {body}")
    age = body.get("age") if isinstance(body, dict) else None
    c.check("...and its age is a number under 2 seconds", isinstance(age, (int, float)) and 0 <= age < 2,
            f"age was {age!r}")
    status, body = request(c.url + "/data/check", "POST", "this is not json")
    c.check("POST of invalid JSON returns 400", status == 400, f"got HTTP {status}: {body}")
    status, body = request(c.url + "/data/check")
    c.check("...and doesn't overwrite the stored data", isinstance(body, dict) and body.get("data") == sent,
            f"got: {body}")


def stage4(c):
    request(c.url + "/data/check", "POST", json.dumps({"stage": 4}))
    status, body = request(c.url + "/data")
    c.check("GET /data returns 200", status == 200, f"got HTTP {status}: {body}")
    ok = isinstance(body, dict) and isinstance(body.get("check"), dict)
    c.check('GET /data includes the "check" channel', ok, f"got: {str(body)[:200]}")
    if ok:
        ch = body["check"]
        c.check('...as {"data": ..., "age": ...}', ch.get("data") == {"stage": 4} and
                isinstance(ch.get("age"), (int, float)), f"got: {ch}")


def stage5(c):
    status, body = request(c.url + "/stats")
    if not c.check("GET /stats returns 200", status == 200, f"got HTTP {status}: {body}"):
        return
    if not c.check("...with uptime, clients, channels and events",
                   isinstance(body, dict) and {"uptime", "clients", "channels", "events"} <= set(body),
                   f"got keys: {list(body) if isinstance(body, dict) else body}"):
        return
    me = [x for x in body["clients"] if isinstance(x, dict) and x.get("name") == NAME]
    if c.check(f'clients includes "{NAME}" (from the X-Pico-Name header)', bool(me),
               f"clients were: {body['clients']}"):
        keys = {"name", "ip", "age", "rate", "posts", "gets", "errors"}
        c.check("...with " + ", ".join(sorted(keys)), keys <= set(me[0]), f"got: {me[0]}")
        c.check("...and it counted the bad JSON as an error", me[0].get("errors", 0) >= 1, f"got: {me[0]}")
    chans = [x for x in body["channels"] if isinstance(x, dict) and x.get("name") == "check"]
    if c.check('channels includes "check"', bool(chans), f"channels were: {body['channels']}"):
        keys = {"name", "age", "rate", "updates", "data"}
        c.check("...with " + ", ".join(sorted(keys)), keys <= set(chans[0]), f"got: {chans[0]}")
    c.check("events is a list of [time, text] pairs",
            isinstance(body["events"], list) and all(isinstance(e, list) and len(e) == 2 for e in body["events"]),
            f"got: {body['events'][:3]}")


STAGES = [stage1, stage2, stage3, stage4, stage5]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", type=int, default=len(STAGES), choices=range(1, len(STAGES) + 1))
    parser.add_argument("--url", default="http://localhost:8080")
    args = parser.parse_args()
    c = Checker(args.url.rstrip("/"))
    try:
        for number, stage in enumerate(STAGES[:args.stage], start=1):
            print(f"Stage {number}")
            stage(c)
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        print(f"\nCan't reach {c.url}: {e}\nIs the server running?")
        sys.exit(2)
    print("\nAll checks passed!" if not c.failed else f"\n{c.failed} check(s) failed.")
    sys.exit(1 if c.failed else 0)


if __name__ == "__main__":
    main()
