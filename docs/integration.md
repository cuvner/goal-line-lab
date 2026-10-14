# Integration: putting your team's system together

Until now, both Picos have been talking to the **reference server** on port 8081. Now you switch them over to **your team's server** on port 8080. You're ready when:

- [ ] **Server:** `check_server.py --stage 4` passes, and the server is running on the Pi
- [ ] **HuskyLens:** stage 4 is done, and the ball shows on the reference dashboard
- [ ] **LED panel:** stage 3 is done, and the panel follows the ball from the reference server

## Steps (about 10 min)
1. **Server:** start `python3 server.py` on the Pi and open `http://<pi-ip>:8080/` on a screen everyone can see.
2. **Both Pico people:** in `CIRCUITPY/settings.toml`, change `SERVER_URL` from `:8081` to `:8080` and save. The Pico restarts by itself.
3. Watch the dashboard. Once the server has stage 5, `huskylens` and `led_panel` appear in CLIENTS. Either way, `ball` appears in CHANNELS.
4. Move the ball. The HuskyLens box, the dashboard box and the LED panel should all follow it.

## Debugging: find the broken hop
The data takes this path:

**HuskyLens → (I2C) → camera Pico → (Wi-Fi, POST) → server → (Wi-Fi, GET) → LED Pico → panel**

Work out which hop is broken before changing any code:

| Check | If it fails, the problem is in |
|---|---|
| The camera Pico's console prints blocks when the ball is in view | I2C wiring or HuskyLens training |
| The camera console has no `Send failed` lines | Wi-Fi, `SERVER_URL`, or the server's POST |
| The dashboard's `ball` channel age stays under 2 s | the camera Pico isn't sending: check its console |
| `http://<pi-ip>:8080/data/ball` in a browser shows the right data | the server's GET |
| The LED Pico's console has no `Get failed` lines | Wi-Fi, `SERVER_URL`, or the server's GET |
| The panel draws the right thing for that data | `show()`, `draw_ball()` or `index()` |

## Prove it works (about 5 min)
Test each failure and write down what the dashboard and the panel show:
1. Take the ball away.
2. Unplug the HuskyLens power, wait 3 s, then plug it back in.
3. Stop the server with Ctrl+C, wait 3 s, then start it again.

Your system should **recover by itself** each time, without anyone pressing reset. If it doesn't, which part needs fixing?

## Team questions
- Which device is the **client** and which is the **server**? Could the LED Pico be a server instead? What would change?
- The camera sends 10 times a second and the panel reads 5 times a second. What's the **worst-case delay** from the ball moving to the panel changing?
- Anyone on the network can POST to `/data/ball`. How could a rival team cheat? Suggest two defences.
- This system uses **polling**. Real goal-line technology must decide in under 1 second. Is polling good enough? What would you change?
