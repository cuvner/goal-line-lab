# Troubleshooting

## Pico (both roles)
| Symptom | Likely cause | Fix |
|---|---|---|
| `ImportError: no module named 'adafruit_requests'` (or `pico_coms`, `huskylens`, `neopixel`) | a library is missing from `CIRCUITPY/lib` | copy it in from the bundle or `pico_lib/` |
| `PicoComs: connecting to ...` repeats forever | wrong Wi-Fi name or password, or a network that needs a username | check `settings.toml` spelling and quotes |
| `Send failed: [Errno 113] ...` or `ETIMEDOUT` | wrong `SERVER_URL`, or the server isn't running | open `SERVER_URL/data/ball` in a browser on the same network |
| `Send failed: HTTP 404` | wrong path, for example `SERVER_URL` ends in `/data` | `SERVER_URL` should only be `http://<ip>:<port>` |
| `Send failed: HTTP 501` | the server stage isn't finished yet | use port 8081 until your server is ready |
| An occasional `EINPROGRESS` or `Repeated socket failures` | a brief Wi-Fi hiccup | ignore it if the next request works |
| The code doesn't restart after saving | auto-reload is off, or the file was saved somewhere else | press Ctrl+D in the serial console |
| `settings.toml` changes are ignored | CircuitPython only reads it at start-up | Ctrl+D, or unplug and replug the Pico |

## HuskyLens
| Symptom | Likely cause | Fix |
|---|---|---|
| `RuntimeError: No pull up found on SDA or SCL` | no power to the HuskyLens, or wires on the wrong pins | check the wiring table, red to 3V3(OUT) |
| `I2C devices found: []` | Protocol Type not set to I2C, or SDA/SCL swapped | General Settings > Protocol Type > I2C, then swap the green and blue wires |
| `HuskyLens connect failed: no reply` | the HuskyLens is still booting | wait, because it retries by itself |
| The HuskyLens keeps rebooting | the 3V3 pin can't supply enough current | power it from VBUS (pin 40, 5 V) instead |
| `blocks` is always `[]` | the ball isn't learned, or it's in a different mode | Object Tracking mode, then learn the ball (stage 2) |
| It tracks your hand or the background | Learn Enable is still on | turn Learn Enable off after training |

## LED panel
| Symptom | Likely cause | Fix |
|---|---|---|
| Nothing lights up | no 5 V supply, no shared ground, or the wrong `PIXEL_PIN` | check the power and GND join, and the DIN pin |
| The test pattern is scrambled | `index()` doesn't match the wiring | use `MODE = "chase"` and sketch the order |
| Wrong colours | a GRB vs RGB panel | add `pixel_order=neopixel.RGB` to `NeoPixel(...)` |
| `AttributeError: 'NoneType' object has no attribute 'get'` | `show()` got `None` (server unreachable) before stage 4 | that's what stage 4 fixes |
| The panel flickers or the Pico resets | `BRIGHTNESS` too high for the supply | keep it at 0.05 |

## Server
| Symptom | Likely cause | Fix |
|---|---|---|
| `OSError: [Errno 98] Address already in use` | an old copy of the server is still running | close the other terminal, or `pkill -f "python3 server.py"` |
| Changes don't take effect | the server wasn't restarted | Ctrl+C, then run it again |
| The browser on another computer can't connect | wrong IP, the server is on the wrong port, or a firewall | `hostname -I`, check the port, then try `curl localhost:8080/` on the Pi |
| `check_server.py` says "Can't reach" | the server isn't running, or it's on a different port | start it, or pass `--url` |
| The dashboard says "No data yet: /data -> HTTP 501" | stage 4 isn't done yet | that's expected until stage 4 |
| `BrokenPipeError` in the log | a client gave up before the reply was sent | harmless |
