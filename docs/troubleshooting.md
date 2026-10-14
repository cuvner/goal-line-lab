# Troubleshooting

Most problems show up as a message in Thonny's **Shell** (on the Picos) or in the dashboard's **EVENTS** box (on the Pi). Read the message first: it usually says what to do.

## Finding the broken link
The ball's journey is: **HuskyLens → camera Pico → Wi-Fi → Referee → Wi-Fi → scoreboard Pico → panel**. Check each hop in order:

| Check | If not, the problem is |
|---|---|
| The camera Pico's Shell says `✓ HuskyLens found` | wiring or the HuskyLens's Protocol Type |
| The Shell prints `ball: left/middle/right` with the ball in view | the camera isn't trained, or `find_ball` |
| The dashboard's CLIENTS box shows `camera` in green | the camera's `SERVER_URL`, or `devices.txt` / `who_is()` |
| The dashboard's big word changes when the ball crosses the line | `decide()` |
| CLIENTS shows `scoreboard` in green | the scoreboard's `SERVER_URL`, or `devices.txt` / `who_is()` |
| The panel shows something | `make_grid`, `draw_letter`, `draw_goal` or `draw_score` |

## Both Picos
| What you see | Why | Fix |
|---|---|---|
| `PicoComs: connecting to ...` over and over | wrong Wi-Fi name or password | check `settings.toml` (watch the quotes) |
| `Can't reach the server at ...` | wrong Pi address in `SERVER_URL`, or the server's off | check the team card; open the dashboard on the Pi |
| `The server doesn't know this Pico yet` | its address isn't in `devices.txt`, or `who_is()` isn't finished | the Shell shows the exact line to add |
| `ImportError: no module named ...` | a library is missing from `CIRCUITPY/lib` | teacher: copy it from the bundle or `pico_lib/` |
| The Pico didn't restart after saving | auto-reload is off | press **Ctrl+D** in the Shell |
| Changed `settings.toml` but nothing happened | it's only read at start-up | Ctrl+D, or unplug and replug |
| An occasional `EINPROGRESS` | a tiny Wi-Fi hiccup | ignore it |

## Spotter
| What you see | Why | Fix |
|---|---|---|
| `Can't find the HuskyLens: check it has power...` | no power, or wrong pins | red → 3V3(OUT), black → GND, green → GP16, blue → GP17 |
| `...isn't answering like a HuskyLens` | Protocol Type isn't I2C, or green/blue swapped | General Settings > Protocol Type > I2C |
| `blocks` is always `[]` | the ball isn't learned, or the camera's in the wrong mode | Object Tracking, then learn the ball (stage 2) |
| It follows your hand instead | Learn Enable is on | long-press the dial, turn **Learn Enable** off, save |
| The HuskyLens keeps restarting | not enough power from 3V3 | move red to **VBUS (pin 40)** |

## Scoreboard
| What you see | Why | Fix |
|---|---|---|
| Nothing lights up | no 5 V, no shared ground, or wrong pin | teacher: check the panel wiring |
| `✗ make_grid's rows are separate lists` | used `[[0]*32]*8` | make a **new** row list inside the loop |
| `✗ letter O is drawn` | the letter is still all zeros | change some 0s to 1s (7 rows of 5) |
| `IndexError` in `draw_letter` | a letter is hanging off the panel | only set `grid[r][c]` when `r` is 0–7 and `c` is 0–31 |
| `IndexError` in `draw_goal` when the score reaches 10 | `DIGITS[10]` doesn't exist | use `DIGITS[score % 10]` |
| The letters look wrong | rows and columns mixed up | `letter[row][col]` → `grid[top + row][left + col]` |
| Nothing but a blinking blue corner | the camera isn't sending | fix the Spotter's side first |
| Only an orange corner | can't reach the server | see "Both Picos" |

## Referee
| What you see | Why | Fix |
|---|---|---|
| EVENTS: `referee.py problem: line N: ...` | a typo or crash on that line | fix line N and save; it reloads by itself |
| EVENTS: `turned away ...: who_is() says it's 'unknown'` | the address isn't in `devices.txt`, or `who_is()` doesn't match it | compare the address in the message with `devices.txt` |
| CLIENTS shows `unknown (camera)` in red | same as above | same as above |
| Big word stuck on `REFEREE ERROR` | one of your functions crashed | the EVENTS box says which line |
| Dashboard won't load | the server isn't running | teacher: `sudo systemctl restart goal-line-server` |
| `test_referee.py` says `referee.py has a typo on line N` | a syntax error | fix that line |
