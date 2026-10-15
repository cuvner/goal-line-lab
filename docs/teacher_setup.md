# Teacher setup (before the day)

Allow about 15 minutes per team the first time.

## Per team you need
- 1 × Raspberry Pi (Raspberry Pi OS, on the Wi-Fi, with screen, keyboard, mouse and Thonny) for the **Referee**
- 2 × Pico 2 W with CircuitPython, and 2 laptops with **Thonny** for the **Spotter** and **Scoreboard**
- 1 × HuskyLens with its 4-wire I2C cable (students wire it up in stage 1)
- 1 × 8×32 WS2812 LED panel **already wired** to the scoreboard Pico: DIN → GP0, 5 V supply (2 A or more), **ground shared** with the Pico
- a football, and tape to mark a goal line

## 1. Each team's Pi
```bash
git clone https://github.com/cuvner/goal-line-lab.git ~/goal-line-lab
```
```bash
sudo cp ~/goal-line-lab/server/goal-line-server.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now goal-line-server
```
The server now runs on port 8080 and starts again on every boot. The Referee student edits `~/goal-line-lab/server/referee.py` in Thonny; the server reloads it whenever it's saved.

Check it: open `http://localhost:8080/` in the Pi's browser. You should see the dashboard with "Waiting for the camera".

Reset for a fresh team: `git -C ~/goal-line-lab checkout -- server/referee.py server/devices.txt server/commentary.txt`

> `server/solution/referee.py` is the finished version. Keep it for yourself, or delete that folder from the Pi if you don't want students finding it.

## 2. Each Pico 2 W
1. Flash the **Raspberry Pi Pico 2 W** CircuitPython UF2 (10.x) from circuitpython.org.
2. From the matching Adafruit CircuitPython **bundle**, copy into `CIRCUITPY/lib`:
   - both Picos: `adafruit_requests.mpy`, `adafruit_connection_manager.mpy`
   - scoreboard Pico: also `neopixel.mpy` and `adafruit_pixelbuf.mpy`
3. Copy **both files in `pico_lib/`** (`pico_coms.py`, `huskylens.py`) into `CIRCUITPY/lib`.
4. Copy `settings.toml.example` to `CIRCUITPY/settings.toml` and fill in the Wi-Fi name and password. Leave `SERVER_URL` as it is: the students change it in stage 0.
5. Copy the role's files onto the drive root:
   - **camera Pico:** `camera_pico/code.py` and `camera_pico/camera.py`
   - **scoreboard Pico:** `scoreboard_pico/code.py`, `scoreboard.py` and `digits.py`

Reset for a fresh team: copy `camera.py` / `scoreboard.py` from the repo over the student's version.

## 2b. Cosmic Unicorn instead of a NeoPixel Pico
A Pimoroni Cosmic Unicorn (32×32, runs Pimoroni MicroPython) can be a team's scoreboard instead. It has its own Wi-Fi and runs `main.py` whenever it has power, so it doesn't need to stay plugged into the Pi. Install `mpremote` on the Pi or a laptop (`pip3 install --user --break-system-packages mpremote`), plug the board in by USB, then:
```bash
cp scoreboard_unicorn/settings.py.example /tmp/settings.py   # then fill it in
```
```bash
mpremote cp scoreboard_unicorn/main.py scoreboard_unicorn/pico_coms.py scoreboard_unicorn/digits.py scoreboard_unicorn/scoreboard.py /tmp/settings.py :
```
Reset for a fresh team: `mpremote cp scoreboard_unicorn/scoreboard.py :`. The board's own console (for the ✓/✗ and the IP banner) is in Thonny with *MicroPython (Raspberry Pi Pico)* selected, or `mpremote repl`.

## 3. Check each LED panel (once)
Copy `scoreboard_pico/solution/scoreboard.py` onto a scoreboard Pico as `scoreboard.py`, with `TEST_MODE = True`. You should see a red border on the panel. If it's scrambled or nothing lights up:
- **Nothing:** check the 5 V supply, the shared ground, and that DIN is on GP0.
- **Scrambled:** the panel's LEDs run in a different order. In `scoreboard_pico/code.py`, try changing `SERPENTINE`, `COLUMN_MAJOR`, `FLIP_X` or `FLIP_Y` until the border is right. Do this on every scoreboard Pico.

## 4. Network
- Picos can only join **WPA2/WPA3-Personal** Wi-Fi (name + password), not networks that need a username. If the school Wi-Fi needs a username, use a phone hotspot per team.
- Devices must be able to see each other. Check by opening `http://<pi-ip>:8080/` from a laptop.
- Pi addresses can change after a reboot. Students find them fresh on the day, so that's fine.

## 5. Your demo system
Put the solution files on one full set (the `solution/` versions of `referee.py`, `camera.py` and `scoreboard.py`, with the real addresses in `devices.txt`) for the hook demo and as a spare. Put its dashboard on the projector.

## On the day
- [ ] Each Pi: dashboard loads at `http://localhost:8080/`, Thonny opens `referee.py`
- [ ] Each Pico: has `lib/pico_coms.py`, `settings.toml`, and the role's files
- [ ] HuskyLens units powered, with cables; balls, tape and team cards on desks
- [ ] LED panel supplies switched on
