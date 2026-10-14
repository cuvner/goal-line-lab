# Goal-line Lab

A 2-hour A Level Computer Science practical. Teams of three build a **networked goal-line detector**. An AI camera spots a football, a Pico 2 W sends its position over Wi-Fi to a Python server on a Raspberry Pi, and a second Pico 2 W shows it on an LED panel. A live web dashboard shows every message in between.

```
HuskyLens ──I2C──▶ Pico 2 W ──HTTP POST──▶ Raspberry Pi server ◀──HTTP GET── Pico 2 W ──▶ 8x32 LED panel
 (camera)        (camera client)    /data/ball     (port 8080)      /data/ball  (display client)
                                                        ▲
                                              browser dashboard (GET /stats)
```

Topics covered: client-server, HTTP (methods, status codes, headers), JSON, IP addresses and ports, APIs/REST, concurrency and locks, I2C, testing with stubs, and robustness.

## For the lesson
| Start here | |
|---|---|
| [docs/lesson_plan.md](docs/lesson_plan.md) | objectives, timings, checkpoint table, plenary |
| [docs/protocol.md](docs/protocol.md) | **the contract** between the three roles |
| [docs/role_server.md](docs/role_server.md) | Server student's staged guide |
| [docs/role_huskylens.md](docs/role_huskylens.md) | HuskyLens student's staged guide |
| [docs/role_led_panel.md](docs/role_led_panel.md) | LED panel student's staged guide |
| [docs/integration.md](docs/integration.md) | putting the team's system together, and debugging |
| [docs/teacher_setup.md](docs/teacher_setup.md) | what to prepare before the lesson |
| [docs/troubleshooting.md](docs/troubleshooting.md) | symptoms, causes, fixes |
| [docs/slide_outline.md](docs/slide_outline.md) | suggested slide deck structure |
| [CLAUDE_PROJECT_INSTRUCTIONS.md](CLAUDE_PROJECT_INSTRUCTIONS.md) | for making slides and worksheets with a Claude Project |

## What's in the repo
```
server/
  dashboard.html          given: the live web dashboard the server sends to browsers
  server.py               STARTER for the Server student (TODOs by stage)
  solution/               complete server, terminal dashboard, systemd services
huskylens_pico/
  i2c_scan.py             given: stage 1 wiring check
  code.py                 STARTER for the HuskyLens student
  solution/code.py
led_pico/
  code.py                 STARTER for the LED panel student (chase / test_pattern / fake_ball / server modes)
  solution/code.py, solution/onboard_test.py
pico_lib/                 given: copy into CIRCUITPY/lib on both Picos
  pico_coms.py            PicoComs, a general-purpose Wi-Fi client class for the protocol
  huskylens.py            HuskyLens v1 I2C driver
tools/
  check_server.py         automated stage-by-stage tests for the server
  fake_camera.py          pretends to be the camera Pico (a bouncing ball)
settings.toml.example     Wi-Fi details and SERVER_URL for each Pico
```

## Hardware (per team)
- Raspberry Pi (runs the student's server on port 8080 and the reference server on port 8081)
- 2 x Raspberry Pi Pico 2 W with CircuitPython 10.x
- DFRobot HuskyLens v1, on I2C: SDA to GP16, SCL to GP17
- 8x32 WS2812 NeoPixel panel: DIN to GP0, with its own 5 V supply and shared ground
- A football

## Quick test of the complete system
```bash
python3 server/solution/server.py
```
```bash
python3 tools/fake_camera.py
```
Open http://localhost:8080/: a ball should bounce around the dashboard.

> **Solutions are included** in the `solution/` folders so the repo works as a teacher's reference. Remove them from student copies if needed.
