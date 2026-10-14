# THE SPOTTER - this is your file!
#
# The HuskyLens camera sends back a list of boxes it can see.
# Each box is a list of 5 numbers:   [x, y, width, height, id]
#   x, y   = the middle of the box (x: 0-320 left to right, y: 0-240 top to bottom)
#   id     = which learned object it is (the football is 1)
#
# So `blocks` is a 2D list, for example:
#   [[ 50, 200, 30, 30, 2],      <- something else (id 2)
#    [160, 120, 40, 40, 1]]      <- the football (id 1)
#
# Save this file and the Pico restarts with your new code. The console
# shows a ✓ or ✗ for each function.

# Positions in each box list, so you can write box[ID] instead of box[4]
X = 0
Y = 1
WIDTH = 2
HEIGHT = 3
ID = 4

BALL_ID = 1


# ---------------- STAGE 3 ----------------
def find_ball(blocks):
    """Look through every box in `blocks` with a loop.
    If a box's ID is BALL_ID, give back that box.
    If no box is the ball, give back None (Python's word for "nothing")."""
    return None


# ---------------- STAGE 4 ----------------
def describe(x):
    """Say where the ball is, for the console.
    Split the 320-wide picture into three equal parts:
      x less than 107         -> "left"
      x less than 214         -> "middle"
      otherwise               -> "right"
    """
    return "?"
