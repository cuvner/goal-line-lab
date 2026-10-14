#!/usr/bin/env python3
"""Terminal dashboard for the Goal-line Lab server.

Shows every Pico client, every channel and recent events, updated live.

Run on the Pi:   python3 terminal_dashboard.py
From a laptop:   ssh -t pi@<pi-ip> python3 goal-line-lab/tools/terminal_dashboard.py
Other server:    python3 terminal_dashboard.py --url http://<pi-ip>:8081

Keys: q quit
"""

import argparse
import curses
import json
import time
import urllib.request

REFRESH = 0.5
OK_AGE = 2.0    # green below this many seconds since last heard from
WARN_AGE = 5.0  # yellow below this, red above


def fetch(url):
    with urllib.request.urlopen(url + "/stats", timeout=1) as response:
        return json.load(response)


def fmt_age(age):
    if age < 60:
        return f"{age:.1f}s"
    if age < 3600:
        return f"{age / 60:.0f}m"
    return f"{age / 3600:.0f}h"


def fmt_uptime(seconds):
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


class Screen:
    def __init__(self, win):
        self.win = win
        self.row = 0
        curses.start_color()
        curses.use_default_colors()
        for i, colour in enumerate((curses.COLOR_GREEN, curses.COLOR_YELLOW,
                                    curses.COLOR_RED, curses.COLOR_CYAN), start=1):
            curses.init_pair(i, colour, -1)
        self.GREEN, self.YELLOW, self.RED, self.CYAN = (curses.color_pair(i) for i in range(1, 5))

    def age_colour(self, age):
        return self.GREEN if age < OK_AGE else self.YELLOW if age < WARN_AGE else self.RED

    def line(self, text="", attr=0, col=0):
        height, width = self.win.getmaxyx()
        if self.row < height - 1 and col < width:
            try:
                self.win.addnstr(self.row, col, text, width - col - 1, attr)
            except curses.error:
                pass

    def next(self, text="", attr=0):
        self.line(text, attr)
        self.row += 1

    def cells(self, parts):
        """Write (text, width, attr) parts along one row."""
        col = 0
        for text, width, attr in parts:
            self.line(text.ljust(width), attr, col)
            col += width
        self.row += 1


def draw(scr, url, stats, error):
    win = scr.win
    win.erase()
    scr.row = 0
    bold = curses.A_BOLD

    title = f" Goal-line Lab server  {url}"
    if stats:
        title += f"   up {fmt_uptime(stats['uptime'])}"
    scr.next(title, bold | curses.A_REVERSE)
    scr.next(time.strftime(" %H:%M:%S") + "   q to quit")
    scr.next()

    if error:
        scr.next(f" Server not reachable: {error}", scr.RED | bold)
        win.refresh()
        return

    scr.next(" CLIENTS", scr.CYAN | bold)
    widths = (14, 17, 11, 8, 9, 9, 8)
    scr.cells(zip((" name", "ip", "last seen", "req/s", "sends", "gets", "errors"),
                  widths, [bold] * 7))
    if not stats["clients"]:
        scr.next(" (no Picos have connected yet)")
    for c in sorted(stats["clients"], key=lambda c: c["name"] or c["ip"]):
        colour = scr.age_colour(c["age"])
        scr.cells(zip(
            (" " + (c["name"] or "?"), c["ip"], fmt_age(c["age"]), f"{c['rate']:.1f}",
             str(c["posts"]), str(c["gets"]), str(c["errors"])),
            widths,
            (colour, 0, colour, 0, 0, 0, scr.RED if c["errors"] else 0),
        ))
    scr.next()

    scr.next(" CHANNELS", scr.CYAN | bold)
    widths = (14, 11, 10, 10)
    scr.cells(zip((" channel", "age", "upd/s", "updates", "latest data"),
                  widths + (0,), [bold] * 5))
    if not stats["channels"]:
        scr.next(" (nothing sent yet)")
    for ch in sorted(stats["channels"], key=lambda ch: ch["name"]):
        colour = scr.age_colour(ch["age"])
        scr.cells(zip(
            (" " + ch["name"], fmt_age(ch["age"]), f"{ch['rate']:.1f}",
             str(ch["updates"]), json.dumps(ch["data"])),
            widths + (0,),
            (colour, colour, 0, 0, 0),
        ))
    scr.next()

    scr.next(" EVENTS", scr.CYAN | bold)
    height, _ = win.getmaxyx()
    room = max(0, height - scr.row - 1)
    for when, text in reversed(stats["events"][-room:] if room else []):
        scr.next(" " + time.strftime("%H:%M:%S", time.localtime(when)) + "  " + text)
    win.refresh()


def main(win, url):
    curses.curs_set(0)
    win.timeout(int(REFRESH * 1000))
    scr = Screen(win)
    while True:
        try:
            stats, error = fetch(url), None
        except Exception as e:  # keep the dashboard up while the server restarts
            stats, error = None, e
        draw(scr, url, stats, error)
        if win.getch() in (ord("q"), ord("Q")):
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8080", help="server address")
    args = parser.parse_args()
    try:
        curses.wrapper(main, args.url.rstrip("/"))
    except KeyboardInterrupt:
        pass
