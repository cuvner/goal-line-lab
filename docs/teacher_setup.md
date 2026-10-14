# Teacher setup (before the lesson)

Allow about 15 minutes per team the first time, then about 5 once you have a routine.

## Per team you need
- 1 x Raspberry Pi (Raspberry Pi OS, on the school Wi-Fi, with a screen, keyboard and mouse) for the **server** student
- 2 x Pico 2 W with CircuitPython, plus 2 computers with Thonny or Mu for the **Pico** students
- 1 x HuskyLens v1 with its 4-pin I2C cable (students wire it in the lesson)
- 1 x 8x32 WS2812 NeoPixel panel, already wired to the LED Pico (DIN to GP0, plus a 5 V supply of at least 2 A, with **shared ground**)
- 1 x football (or any ball with a strong pattern or colour)

## 1. Each team's Pi
```bash
git clone https://github.com/cuvner/goal-line-lab.git ~/goal-line-lab
```
```bash
sudo cp ~/goal-line-lab/server/solution/goal-line-reference.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now goal-line-reference
```
This runs the **reference server** on port **8081**, and it starts again on every boot. Check it by opening `http://<pi-ip>:8081/` from another computer, and note each Pi's IP address (`hostname -I`) on a card for the team.

Run a quick self-test:
```bash
python3 ~/goal-line-lab/tools/check_server.py --url http://localhost:8081
```
It should say `All checks passed!`.

> The repo is public and includes `solution/` folders. If you don't want the server student to find `server/solution/server.py` on the Pi, delete that folder after installing the service. The service only needs that file, so copy it somewhere else first and edit `ExecStart` in the service file to match.

## 2. Each Pico 2 W
1. Flash the **Raspberry Pi Pico 2 W** CircuitPython UF2 (10.x) from circuitpython.org.
2. From the matching Adafruit CircuitPython **bundle**, copy into `CIRCUITPY/lib`:
   - both Picos: `adafruit_requests.mpy`, `adafruit_connection_manager.mpy`
   - LED Pico: also `neopixel.mpy` and `adafruit_pixelbuf.mpy`
3. Copy **everything in `pico_lib/`** into `CIRCUITPY/lib` (`pico_coms.py`, `huskylens.py`).
4. Copy `settings.toml.example` to `CIRCUITPY/settings.toml`, then fill in the Wi-Fi name and password, and `SERVER_URL = "http://<team-pi-ip>:8081"`.
5. Leave `code.py` blank. Students copy in the starter files themselves.

## 3. Check each LED panel (do this once)
Copy `led_pico/solution/code.py` onto the LED Pico with `MODE = "test_pattern"`. You should see a red top row, a blue left column and a green bottom-right pixel. If you don't:
- **Nothing lights up:** check DIN is on `PIXEL_PIN` (GP0), the 5 V supply is on, and its ground is joined to the Pico's GND.
- **The pattern is wrong:** this panel isn't wired in the column zig-zag the solution assumes. That's fine, because students work it out with `MODE = "chase"`, but make a note of the layout so you can help them.

## 4. Network
- The Pico 2 W can only join **WPA2/WPA3-Personal** networks (name + password), not ones that need a username.
- Devices must be able to reach each other. Some school networks block this (client isolation). To check, open `http://<pi-ip>:8081/` from a student computer.
- Pi IP addresses can change after a reboot. Check them on the day, or ask IT to reserve them.

## 5. Your demo system (for the hook)
Your own Pi runs the complete system on port 8080 as `goal-line-server.service`, with the solution code on both Picos. Open its dashboard on the projector.

## On the day: quick checks
- [ ] Each team's `http://<pi-ip>:8081/` loads
- [ ] Each Pico shows `CIRCUITPY` and has `lib/pico_coms.py` and `settings.toml`
- [ ] HuskyLens units charged/powered, with I2C cables and balls on the desks
- [ ] LED panel power supplies switched on
