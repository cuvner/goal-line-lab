# THE REFEREE (the server) - this is your file!
#
# The server is the middle of the system. The camera Pico sends it the
# ball's position, and the scoreboard Pico asks it for the decision.
# Your functions decide WHO is allowed to send and receive, and WHAT the
# decision is. Save this file and the server uses your new code straight away.
#
# Check your functions:   python3 test_referee.py
# See them working:       the dashboard, http://<this Pi's IP address>:8080/

# Where is the goal line? The camera's picture is 320 wide:
# x = 0 is the left edge and x = 320 is the right edge.
# The ball has crossed the line when its x is BIGGER than this.
GOAL_LINE = 220


# ---------------- STAGE 1: who's who ----------------
# Every device on a network has an IP address, like a house number.
# devices.txt is the server's address book: one device per line,
#     camera,192.168.1.23
#     scoreboard,192.168.1.24
# Put in your team's real addresses (each Pico prints its own when it starts).

def load_devices(filename):
    """Read the address book into a 2D list, one [name, ip] per line, e.g.
        [["camera", "192.168.1.23"], ["scoreboard", "192.168.1.24"]]
    Use line.strip() to remove the newline, and line.split(",") to split
    a line at the comma. Skip any empty lines."""
    devices = []
    return devices


def who_is(ip, devices):
    """A message has arrived from address `ip`. Who sent it?
    Loop through `devices` (the 2D list from load_devices). If a device's
    ip matches, give back its name. If none match, give back "unknown".
    The server only accepts the ball from "camera" and only sends the
    decision to "scoreboard"."""
    return "unknown"


# ---------------- STAGE 2: the decision ----------------
def decide(seen, x):
    """seen is True if the camera can see the ball, False if it can't.
    x    is how far across the picture the ball is (0 to 320).
    Give back one of these words:
      "NO BALL"  if the camera can't see the ball
      "GOAL"     if x is bigger than GOAL_LINE
      "NO GOAL"  otherwise
    """
    return "NO GOAL"


# ---------------- STAGE 3: the score ----------------
def new_score(score, previous, decision):
    """score     is the number of goals so far.
    previous  is the decision last time (e.g. "NO GOAL").
    decision  is the decision now.
    The ball stays over the line for a while, so the decision is "GOAL"
    many times in a row. It's only a NEW goal when the decision is "GOAL"
    now AND previous was NOT "GOAL".
    Give back the new score: score + 1 for a new goal, otherwise score."""
    return score


# ---------------- STAGE 4 (extra): commentary ----------------
def commentary(decision, score):
    """Say something exciting! The dashboard shows it under the decision.
    This runs every time the decision changes.
    commentary.txt has one comment per line, like  GOAL|What a strike!
    The word before the | is the decision it's for.
      1. Read every line of commentary.txt.
      2. Keep the lines whose decision matches `decision`.
      3. Give back the text after the | of one of them.
    Give back "" if there aren't any."""
    return ""
