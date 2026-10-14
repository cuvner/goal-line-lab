# Goal-line Lab

A fun, 2-hour, hands-on activity for 16-year-olds (open day friendly). Teams of three build a mini **goal-line detector**: an AI camera spots a football, a Raspberry Pi "referee" decides GOAL or NO GOAL and keeps score, and an LED panel shows it, all over Wi-Fi. A live web dashboard shows everything happening.

```
  SPOTTER (camera Pico)  ──▶  REFEREE (server on the Pi)  ──▶  SCOREBOARD (LED Pico)
  HuskyLens finds the ball     who's who? goal? score?          ball, or GOAL! in lights
                                        │
                                   dashboard (web page)
```

Students only write **short functions** using loops, if-statements, 2D lists and reading a text file. All the networking and hardware code is given, and every function they write is checked automatically with ✓/✗ and a hint.

## Start here
| | |
|---|---|
| [docs/how_it_works.md](docs/how_it_works.md) | the plain-English explanation for everyone |
| [docs/team_card.md](docs/team_card.md) | the IP-address swap at the start (print one per team) |
| [docs/role_referee.md](docs/role_referee.md) | the Referee's stages (server, on the Pi) |
| [docs/role_spotter.md](docs/role_spotter.md) | the Spotter's stages (camera Pico) |
| [docs/role_scoreboard.md](docs/role_scoreboard.md) | the Scoreboard's stages (LED Pico) |
| [docs/lesson_plan.md](docs/lesson_plan.md) | timings, checkpoints, plenary questions |
| [docs/teacher_setup.md](docs/teacher_setup.md) | what to prepare beforehand |
| [docs/troubleshooting.md](docs/troubleshooting.md) | what the messages mean and what to do |
| [docs/slide_outline.md](docs/slide_outline.md) | suggested slides |
| [CLAUDE_PROJECT_INSTRUCTIONS.md](CLAUDE_PROJECT_INSTRUCTIONS.md) | for making slides and worksheets with a Claude Project |

## What's where
```
server/                   the Referee (runs on the Raspberry Pi, normal Python 3)
  referee.py              ★ the student's file
  devices.txt             the address book the student fills in
  commentary.txt          comments for the student's commentary()
  test_referee.py         checks the student's functions (✓/✗)
  server.py               given: the server; reloads referee.py when it's saved
  dashboard.html          given: the live web page
  goal-line-server.service  runs the server on boot
  solution/referee.py     TEACHER ONLY
camera_pico/              the Spotter (CircuitPython, Pico 2 W + HuskyLens)
  camera.py               ★ the student's file
  code.py                 given: checks camera.py, reads the camera, sends the ball
  solution/camera.py      TEACHER ONLY
scoreboard_pico/          the Scoreboard (CircuitPython, Pico 2 W + 8x32 NeoPixels)
  scoreboard.py           ★ the student's file
  goal.txt, my_picture.txt  pictures as # and . characters
  code.py                 given: checks scoreboard.py, fetches decisions, drives the panel
  solution/scoreboard.py  TEACHER ONLY
pico_lib/                 given: copy into CIRCUITPY/lib on both Picos
  pico_coms.py            PicoComs: Wi-Fi + talking to the server
  huskylens.py            HuskyLens driver
tools/
  fake_camera.py          pretends to be the camera (a bouncing ball) for testing
  terminal_dashboard.py   the dashboard in a terminal
settings.toml.example     Wi-Fi details + the Pi's address, for each Pico
```

## Hardware (per team)
- Raspberry Pi with screen, keyboard and Thonny
- 2 × Raspberry Pi Pico 2 W with CircuitPython 10.x, and 2 laptops with Thonny
- DFRobot HuskyLens v1 (green → GP16, blue → GP17, black → GND, red → 3V3)
- 8×32 WS2812 NeoPixel panel (DIN → GP0, its own 5 V supply, shared ground)
- a football

## Try the server on any computer
```bash
python3 server/server.py
```
```bash
python3 tools/fake_camera.py
```
Open http://localhost:8080/. Copy `server/solution/referee.py` over `server/referee.py` and put `camera,127.0.0.1` in `server/devices.txt` to see decisions and goals.
