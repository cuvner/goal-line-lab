# Role: HuskyLens (camera client)

You're building the **eyes** of the system. A Pico 2 W reads the HuskyLens AI camera over **I2C**, decides whether the football is in view, and sends the result to the server over Wi-Fi.

**You'll work on:** a Pico 2 W with CircuitPython, plugged into your computer. Edit the files on the `CIRCUITPY` drive with Thonny or Mu.
**Your spec:** [protocol.md](protocol.md), especially the `ball` channel.
**Given to you:** `pico_lib/huskylens.py` (the camera driver) and `pico_lib/pico_coms.py` (the Wi-Fi comms). Both should already be in `CIRCUITPY/lib`.

Until your server teammate is ready, send to the **reference server** on port **8081**. Your teacher has set `SERVER_URL` in `CIRCUITPY/settings.toml`.

---

## Stage 1: Wire it and find it (target: 10 min)
**Unplug the Pico from USB before wiring.** Use the HuskyLens 4-pin I2C cable:

| HuskyLens wire | Pico 2 W pin |
|---|---|
| T / SDA (green) | GP16 (pin 21) |
| R / SCL (blue) | GP17 (pin 22) |
| - (black) | GND (pin 23) |
| + (red) | 3V3(OUT) (pin 36) |

On the HuskyLens, go to **General Settings > Protocol Type** and choose **I2C**. Use the dial to move and press the dial to select. Save on the way out.

Copy `huskylens_pico/i2c_scan.py` onto the Pico as `code.py`, then open the serial console.

**Checkpoint:** the console prints `I2C devices found: ['0x32']`.

**Think:** I2C has one controller (the Pico) and many devices on the same two wires. How does the Pico talk to just one of them? Why does every device need a different address?

<details><summary>Problems?</summary>

- `No pull up found on SDA or SCL`: the HuskyLens has no power, or SDA/SCL are on the wrong pins.
- An empty list `[]`: the Protocol Type isn't set to I2C, or SDA and SCL are swapped.
</details>

## Stage 2: Teach it the football (target: 10 min)
1. Turn the dial to **Object Tracking** and press it.
2. If it already knows an object, press the **learning button** twice to forget it.
3. Long-press the dial, then set **Frame Ratio** to **1:1** and turn **Learn Enable** on. Save & Return.
4. Point the camera at the ball so the yellow box frames it. **Hold the learning button** while you move the camera slightly around the ball, then let go.
5. The ball now has a box labelled **ID1** that follows it.

**Checkpoint:** move the ball around, and the box follows it on the HuskyLens screen.

When tracking is good, go back into the settings and turn **Learn Enable off**, so it doesn't slowly drift onto your hand or the background.

## Stage 3: Read the camera (target: 10 min)
Copy `huskylens_pico/code.py` onto the Pico as `code.py`. As it stands, it prints what the camera sees, ten times a second.

**Checkpoint:** with the ball in view you see lines like `[{'x': 158, 'y': 112, 'w': 64, 'h': 60, 'id': 1}]`, and with no ball you see `[]`.

**Investigate and write down:**
- Where is (0, 0)? Move the ball to each corner. What are the biggest values of `x` and `y`?
- Is `x, y` the corner or the centre of the box?
- What happens to `w` and `h` as the ball moves closer?

## Stage 4: Send it to the server (target: 15 min)
1. Write `choose_ball(blocks)`: keep only blocks whose `id` is `BALL_ID`, and return the biggest one (largest `w * h`), or `None`.
2. Write `make_reading(ball)`: return `{"seen": False}`, or the ball's dict with `"seen": True` added. Check it against the `ball` format in [protocol.md](protocol.md).
3. Uncomment the `PicoComs` lines, and call `coms.send(CHANNEL, reading)` in the loop. If it returns `False`, print `coms.last_error`.

**Checkpoint**
- The console shows `PicoComs: connected, IP ...`.
- On the dashboard (`http://<pi-ip>:8081/`), the CAMERA panel shows a box that follows your ball.

<details><summary>Hint: choose_ball</summary>

```python
balls = [b for b in blocks if b["id"] == BALL_ID]
if not balls:
    return None
return max(balls, key=lambda b: b["w"] * b["h"])
```
</details>

## Stage 5: Make it robust (target: 10 min)
Unplug the HuskyLens power wire while the code is running. It crashes. A device in a stadium can't just stop!
- Wrap `camera.get_blocks()` in `try`/`except (OSError, ValueError)`. When it fails, print the error, turn the LED off, `time.sleep(0.5)` and `continue`.
- Turn the onboard LED on whenever the ball is seen (`led.value = reading["seen"]`).

**Checkpoint:** unplug and replug the HuskyLens power. The program keeps running, the dashboard shows **Camera offline** after 2 seconds, and it recovers on its own. **Why** does the dashboard say "offline", when your code never sends that message?

## Extensions
- **Bandwidth:** you send 10 messages a second even when nothing changes. Send only when the reading changes, plus a "heartbeat" at least once a second. Why do you still need the heartbeat?
- **Latency:** time `coms.send()` with `time.monotonic()`. How long does one request take? What limits how fast you could send?
- **Protocol:** read `pico_lib/huskylens.py`. Draw the bytes of one request frame and explain the checksum.
- **Goal-line decision:** add a second channel, `goal`, that's `true` when the ball's centre crosses a line you choose (for example `x > 200`).
