# THE REFEREE - SOLUTION
# Copy over server/referee.py to use it.

import random

GOAL_LINE = 220


def load_devices(filename):
    devices = []
    with open(filename) as file:
        for line in file:
            line = line.strip()
            if line != "":
                parts = line.split(",")
                devices.append([parts[0].strip(), parts[1].strip()])
    return devices


def who_is(ip, devices):
    for device in devices:
        if device[1] == ip:
            return device[0]
    return "unknown"


def decide(seen, x):
    if not seen:
        return "NO BALL"
    if x > GOAL_LINE:
        return "GOAL"
    return "NO GOAL"


def new_score(score, previous, decision):
    if decision == "GOAL" and previous != "GOAL":
        return score + 1
    return score


def commentary(decision, score):
    comments = []
    with open("commentary.txt") as file:
        for line in file:
            line = line.strip()
            if "|" in line:
                parts = line.split("|")
                if parts[0] == decision:
                    comments.append(parts[1])
    if len(comments) == 0:
        return ""
    text = random.choice(comments)
    if decision == "GOAL":
        text = text + " That's " + str(score) + "!"
    return text
