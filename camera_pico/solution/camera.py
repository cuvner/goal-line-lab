# THE SPOTTER - SOLUTION
# Copy over camera.py on the Pico to use it.

X = 0
Y = 1
WIDTH = 2
HEIGHT = 3
ID = 4

BALL_ID = 1


def find_ball(blocks):
    for box in blocks:
        if box[ID] == BALL_ID:
            return box
    return None


def describe(x):
    if x < 107:
        return "left"
    elif x < 214:
        return "middle"
    else:
        return "right"


# Extension: if the camera sees more than one ball, pick the biggest one
def find_biggest_ball(blocks):
    biggest = None
    for box in blocks:
        if box[ID] == BALL_ID:
            if biggest is None or box[WIDTH] * box[HEIGHT] > biggest[WIDTH] * biggest[HEIGHT]:
                biggest = box
    return biggest
