#!/usr/bin/env python3
"""Check the functions in referee.py.   Run:  python3 test_referee.py
GIVEN: you don't need to edit this file."""

import os
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))
passed = failed = 0


def check(what, got, expected):
    global passed, failed
    if got == expected:
        passed += 1
        print(f"  ✓ {what}")
    else:
        failed += 1
        print(f"  ✗ {what}\n      expected {expected!r} but got {got!r}")


def run(what, function):
    try:
        function()
    except Exception as e:
        global failed
        failed += 1
        line = [f for f in traceback.extract_tb(e.__traceback__) if f.filename.endswith("referee.py")]
        where = f" (referee.py line {line[-1].lineno})" if line else ""
        print(f"  ✗ {what} crashed{where}: {type(e).__name__}: {e}")


try:
    import referee
except SyntaxError as e:
    print(f"referee.py has a typo on line {e.lineno}: {e.msg}")
    raise SystemExit(1)

print("Stage 1: load_devices() and who_is()")


def stage1():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("camera,10.0.0.5\nscoreboard,10.0.0.6\n\n")
    book = referee.load_devices(f.name)
    os.remove(f.name)
    check("load_devices reads a 2-line file into a 2D list", book,
          [["camera", "10.0.0.5"], ["scoreboard", "10.0.0.6"]])
    check("who_is finds the camera", referee.who_is("10.0.0.5", book), "camera")
    check("who_is finds the scoreboard", referee.who_is("10.0.0.6", book), "scoreboard")
    check("who_is says unknown for a stranger", referee.who_is("10.0.0.99", book), "unknown")
    mine = referee.load_devices("devices.txt")
    print("      your devices.txt says:", mine)
    if any(len(d) > 1 and d[1] == "0.0.0.0" for d in mine):
        print("      (remember to put your team's real IP addresses in devices.txt!)")


run("load_devices/who_is", stage1)

line = referee.GOAL_LINE
print(f"Stage 2: decide()   (GOAL_LINE is {line})")
run("decide", lambda: (
    check("no ball seen -> NO BALL", referee.decide(False, 0), "NO BALL"),
    check(f"ball at x={line + 50} -> GOAL", referee.decide(True, line + 50), "GOAL"),
    check(f"ball at x={line - 50} -> NO GOAL", referee.decide(True, line - 50), "NO GOAL"),
    check(f"ball exactly on the line (x={line}) -> NO GOAL", referee.decide(True, line), "NO GOAL"),
))

print("Stage 3: new_score()")
run("new_score", lambda: (
    check("a new goal adds 1", referee.new_score(0, "NO GOAL", "GOAL"), 1),
    check("still GOAL from last time: no change", referee.new_score(1, "GOAL", "GOAL"), 1),
    check("no goal: no change", referee.new_score(1, "NO GOAL", "NO GOAL"), 1),
    check("goal from NO BALL adds 1", referee.new_score(3, "NO BALL", "GOAL"), 4),
))

print("Stage 4 (extra): commentary()")


def stage3():
    text = referee.commentary("GOAL", 1)
    check("GOAL gives some text", isinstance(text, str) and len(text) > 0, True)
    check("unknown decision gives \"\"", referee.commentary("TEA BREAK", 0), "")
    print(f"      (it said: {text!r})")


run("commentary", stage3)
print(f"\n{passed} passed, {failed} to fix." if failed else f"\nAll {passed} checks passed!")
