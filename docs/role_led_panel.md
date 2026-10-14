# Role: LED panel (display client)

You're building the **scoreboard**. A Pico 2 W drives an 8 x 32 NeoPixel panel (256 RGB LEDs), asks the server where the ball is, and draws it.

**You'll work on:** a Pico 2 W with CircuitPython and a panel that's already wired. Edit `CIRCUITPY/code.py` with Thonny or Mu, starting from `led_pico/code.py`.
**Your spec:** [protocol.md](protocol.md), especially the `ball` channel and the staleness rule.
**Given to you:** `pico_lib/pico_coms.py` (the Wi-Fi comms), already in `CIRCUITPY/lib`.

Until your server teammate is ready, read from the **reference server** on port **8081**. Your teacher has set `SERVER_URL` in `CIRCUITPY/settings.toml`.

> **Keep `BRIGHTNESS` low (0.05).** At full brightness, 256 LEDs can draw over 10 A, and they're painful to look at.

---

## Stage 1: How is the panel wired? (target: 15 min)
The panel is one long chain of 256 LEDs, numbered 0-255. You want to draw at **(x, y)**: column 0-31 from the left, row 0-7 from the top. So you need a function `index(x, y)` that returns the right LED number.

1. Copy `led_pico/code.py` onto the Pico as `code.py`, with `MODE = "chase"`. Watch the white dot move, and read the numbers it prints.
2. Sketch an 8 x 32 grid and write the numbers of the first 20 or so pixels in it. Where does pixel 0 start? Which way does pixel 8 go?
3. Write `index(x, y)`. Hint: the formula is different for **even** and **odd** columns.
4. Change to `MODE = "test_pattern"`.

**Checkpoint:** a **red top row**, a **blue left column** and **one green pixel in the bottom-right corner**.

<details><summary>Hint</summary>

If the chain runs down column 0, up column 1, down column 2 and so on (a "serpentine" or zig-zag), then each column starts at `x * 8`. In even columns `y` counts down from the top. In odd columns it counts up from the bottom, so use `7 - y`.
</details>

## Stage 2: Draw a ball (target: 15 min)
The camera is 320 x 240 pixels, and the panel is 32 x 8. So you need to **scale** camera coordinates to panel coordinates.

1. Write `to_range(centre, size, cam_size, cells)`. The box runs from `centre - size/2` to `centre + size/2` in camera pixels. Multiply both ends by `cells / cam_size`, round the start down and the end up (`int`, `math.ceil`), keep both inside `0..cells`, and return `range(start, end)`.
2. Write `draw_ball(ball)`, which uses `to_range` for the columns and the rows, with two nested loops, and calls `set_xy(x, y, GREEN)`.
3. Set `MODE = "fake_ball"`.

**Checkpoint:** in turn, a box in the middle, one top-left, one bottom-right, the whole panel lit, then a single red dot (no ball).

**Test it on paper first:** `to_range(160, 64, 320, 32)` should give `range(12, 20)`. What should `to_range(0, 0, 320, 32)` give? Why must the range never be empty?

## Stage 3: Get the ball from the server (target: 10 min)
Fill in the `else:` block at the bottom, then set `MODE = "server"`:
```python
coms = PicoComs(name="led_panel")
coms.connect()
blink = False
while True:
    ball = coms.get(CHANNEL)
    blink = not blink
    show(ball, coms.age, blink)
    time.sleep(POLL_INTERVAL)
```
To test without the real camera, ask your server teammate to run `tools/fake_camera.py` against the server you're using, or run it yourself on your computer:
```bash
python3 fake_camera.py --url http://<pi-ip>:8081
```

**Checkpoint:** the panel shows the ball bouncing around, matching the CAMERA panel on the dashboard.

## Stage 4: Show what's going wrong (target: 10 min)
A display that shows nothing could mean "no ball" or "everything is broken". You need to show the difference. Update `show()`:

| Situation | How you know | Show |
|---|---|---|
| Can't reach the server | `ball is None` | orange dot at (0, 0) |
| Camera offline | `age is None` or `age > STALE_AFTER` | **blinking** blue dot at (0, 0) |
| Ball seen | `ball["seen"]` | green box |
| No ball | otherwise | red dot at (0, 0) |

**Checkpoint:** stop `fake_camera.py` and the dot blinks blue after 2 s. Ask the server person to stop the server, and it turns orange. Restart both, and it recovers by itself.

**Think:** why must the order of these checks be exactly this? What goes wrong if you check `ball["seen"]` first?

## Extensions
- **Distance:** make the box brighter or a different colour as `w` gets bigger (the ball is closer).
- **Trail:** fade the last few positions instead of clearing the screen each time.
- **Text:** scroll `GOAL!` across the panel. Design a 3 x 5 pixel font as a Python dictionary.
- **Efficiency:** the panel redraws 5 times a second, even when nothing changes. Only call `pixels.show()` when the picture changes. How would you tell?
