# You are the SPOTTER (the camera)

You're the eyes of the system. A **HuskyLens** is a camera with a tiny AI built in: you teach it what a football looks like, and it tells your Pico where it sees one. Your code then picks out the ball, and the Pico sends it to the Referee over Wi-Fi.

**Your file:** `camera.py` on the camera Pico (the `CIRCUITPY` drive). Open it in **Thonny**.
**When you save it**, the Pico restarts and checks your functions. Look in Thonny's **Shell** for ✓ and ✗.

---

## Stage 0: Swap addresses (10 min, with your team)
1. The Referee tells you the Pi's IP address. Open `settings.toml` on the Pico and change the `SERVER_URL` line to `SERVER_URL = "http://<the Pi's address>:8080"`, then save.
2. The Pico restarts and prints **its own** address in big letters. Write it on the **team card** and give it to the Referee.

## Stage 1: Wire up the camera (10 min)
**Unplug the Pico's USB cable first.** Plug the HuskyLens's 4-wire cable into the "I2C" socket, then connect:

| HuskyLens wire | Pico pin |
|---|---|
| green (T) | GP16 (pin 21) |
| blue (R) | GP17 (pin 22) |
| black (−) | GND (pin 23) |
| red (+) | 3V3(OUT) (pin 36) |

On the HuskyLens screen, turn the dial to **General Settings > Protocol Type** and choose **I2C**.

Plug the Pico back in.

✅ **Checkpoint:** the Shell says `✓ HuskyLens found`. If it doesn't, it tells you what to check.

## Stage 2: Teach it the football (15 min)
1. Turn the dial to **Object Tracking** and press it.
2. If it already knows something, press the **learning button** (top right) twice to forget it.
3. Point it at the ball so the yellow box is around it. **Hold the learning button** while moving the camera slightly around the ball, then let go.
4. The screen now shows a box labelled **ID1** that follows the ball.

✅ **Checkpoint:** move the ball and the box follows it on the HuskyLens screen.

## Stage 3: Find the ball (15 min)
Ten times a second, the camera gives your `find_ball(blocks)` function a **2D list**: one row for every box it can see, with 5 numbers in each row.
```python
blocks = [[ 50, 200, 30, 30, 2],     # something else (id 2)
          [160, 120, 40, 40, 1]]     # the football (id 1)
#          x    y   width height id
```
First, **look at it yourself**: add `print(blocks)` as the first line inside `find_ball`, save, and move the ball around. Watch the numbers change. Where is x = 0? Which way does y go?

Then write the function: **loop** through `blocks`. If a box's id (`box[ID]`) is `BALL_ID`, give back that box. After the loop, give back `None`.

✅ **Checkpoint:** the Shell shows ✓ for `find_ball`, the Pico's LED lights up when it sees the ball, and the **dashboard's CAMERA box shows a green square that follows your ball**.

(Delete the `print(blocks)` line when you're done. It's very chatty.)

## Stage 4: Where is it? (10 min)
Write **`describe(x)`**, which says which third of the picture the ball is in: `"left"` if `x` is less than 107, `"middle"` if it's less than 214, otherwise `"right"`.

✅ **Checkpoint:** the Shell shows ✓ for `describe`, and prints `ball: left` / `ball: middle` / `ball: right` as you move the ball.

## More to try
- Hold the ball exactly on your real goal line and read its `x` on the dashboard. Tell the Referee, so they can set `GOAL_LINE`.
- If there are two balls, pick the **biggest** one (largest width × height).
- How far away can the camera still see the ball? Does it work in different lighting?
