# You are the REFEREE (the server)

The Raspberry Pi is the **server**: the computer in the middle. The camera Pico sends it the ball's position, and the scoreboard Pico asks it what to show. You write the server's brain: **who's allowed to talk to it**, and **is it a goal?**

**Your file:** `referee.py`, in the `goal-line-lab/server` folder on the Pi. Open it in **Thonny**.
**When you save it**, the server uses your new code straight away.
**Check your functions:** open `test_referee.py` in Thonny and press **Run** (the green ▶). Each check shows ✓ or ✗.
**Watch it work:** open the dashboard in the Pi's web browser at `http://localhost:8080/`.

---

## Stage 0: Swap addresses (10 min, with your team)
1. Open a **Terminal** on the Pi and type `hostname -I`. The first number is the Pi's IP address. Write it on the **team card** and tell both Pico people.
2. They'll tell you their Picos' addresses. Open `devices.txt` (same folder) and replace the `0.0.0.0`s:
   ```
   camera,192.168.1.23
   scoreboard,192.168.1.24
   ```
   Save it.

The dashboard's EVENTS box now says the server is **turning away** the Picos. That's because your `who_is()` doesn't work yet.

## Stage 1: Who's who? (20 min)
The server needs to read the address book and match each message to a device.

**`load_devices(filename)`**: read `devices.txt` into a **2D list**, with one `[name, ip]` per line:
```python
[["camera", "192.168.1.23"], ["scoreboard", "192.168.1.24"]]
```
- Open the file and loop through its lines (just like reading any text file).
- `line.strip()` removes the newline, and `line.split(",")` splits `"camera,192.168.1.23"` into `["camera", "192.168.1.23"]`.
- Skip empty lines.

**`who_is(ip, devices)`**: a message came from address `ip`. Loop through `devices`. If a device's address (`device[1]`) matches, give back its name (`device[0]`). If nothing matches, give back `"unknown"`.

✅ **Checkpoint:** `test_referee.py` shows ✓ for stage 1, and on the dashboard **CLIENTS shows `camera` and `scoreboard`**. The Pico people should see "the server is accepting the ball now".

💡 **Think:** what would happen if a stranger's laptop pretended to be the camera? How does your `who_is()` stop it?

## Stage 2: Goal or no goal? (15 min)
**`decide(seen, x)`** gives back one word:
- `"NO BALL"` if `seen` is `False`
- `"GOAL"` if `x` is bigger than `GOAL_LINE`
- `"NO GOAL"` otherwise

✅ **Checkpoint:** the big word on the dashboard changes as the Spotter moves the ball across the dashed goal line.

## Stage 3: Keep the score (10 min)
**`new_score(score, previous, decision)`**: when the ball crosses the line, the decision is `"GOAL"` ten times a second for as long as it stays there. You only want to count it **once**:
- if `decision` is `"GOAL"` **and** `previous` is **not** `"GOAL"`, give back `score + 1`
- otherwise give back `score`

✅ **Checkpoint:** each time the ball goes over the line, "Goals" on the dashboard goes up by exactly 1.

## Stage 4 (extra): Commentary (15 min)
**`commentary(decision, score)`**: read `commentary.txt`, where each line looks like `GOAL|What a strike!`. Keep the lines that start with this `decision`, and give back the text after the `|` of one of them, or `""` if there are none.
- `line.split("|")` gives `["GOAL", "What a strike!"]`.
- For a different comment each time, add `import random` at the top and use `random.choice(your_list)`.

Then write your own commentary lines in `commentary.txt`.

## More to try
- Ask the Spotter to hold the ball exactly on the real goal line and read `x` off the dashboard. Set `GOAL_LINE` to that number.
- Add a `"CLOSE!"` decision for when the ball is within 20 of the line but not over it.
- Add `"FINAL SCORE"` commentary when the score reaches 5.
