# How Goal-line Lab works

Real football uses **goal-line technology**: cameras watch the goal line and buzz the referee's watch within a second if the ball crosses it. Today your team builds a mini version with three small computers that talk over Wi-Fi.

```
  SPOTTER                      REFEREE                       SCOREBOARD
  (camera Pico)                (the server, on the Pi)       (LED panel Pico)

  HuskyLens camera             "Who sent this? Is it         8 x 32 lights
  finds the ball  ──────────▶   a goal? What's the  ──────▶  light up GOAL
                  "the ball     score?"             "GOAL, 2" and the score
                   is at x=250"
                                      │
                                      ▼
                               the dashboard
                         (a web page anyone can watch)
```

| Who | What they build | Their file |
|---|---|---|
| **Spotter** | wire up the camera, teach it what a football looks like, write `find_ball()` | `camera.py` on the camera Pico |
| **Referee** | the server's brain: who's who, goal or no goal, and the score | `referee.py` on the Raspberry Pi |
| **Scoreboard** | light up GOAL and the score on the LED panel | `scoreboard.py` on the scoreboard Pico |

Each of you only edits **your own file**. The tricky stuff (Wi-Fi, the camera and the lights) is already done in the other files.

## Addresses: how the devices find each other
Every device on a network has an **IP address**, a bit like a house number, for example `192.168.1.23`.

- The Picos need to know the **Referee's (Pi's)** address, so they know where to send and fetch messages. It goes in each Pico's `settings.toml` file.
- The Referee needs to know the **Picos'** addresses, so it can tell who's talking. It only accepts the ball from the camera, and only gives the decision to the scoreboard. That's how the server makes sure the **right information goes to the right device**. The addresses go in the Referee's `devices.txt` "address book".

At the start, everyone finds their address and writes it on the [team card](team_card.md).

## The messages
The devices send short messages to the server, like this:

- **Spotter → Referee**, 10 times a second: `{"seen": true, "x": 250, "y": 120}`, meaning "I can see the ball, 250 across and 120 down".
- **Scoreboard → Referee**, 5 times a second: "What's the decision?" The reply is something like `{"decision": "GOAL", "score": 2, "x": 250, "y": 120}`.

The camera's picture is **320 wide and 240 tall**. `x` goes from 0 (left) to 320 (right), and `y` goes from 0 (top) to 240 (bottom). The goal line is an up-and-down line at an `x` the Referee chooses.

## Words you'll hear
| Word | Meaning |
|---|---|
| **Server** | the computer in the middle that the others talk to (our Pi). Here it's the Referee. |
| **Client** | a device that talks to the server (both Picos) |
| **IP address** | a device's number on the network, like `192.168.1.23` |
| **Pico** | a tiny, cheap computer (Raspberry Pi Pico 2 W) with Wi-Fi |
| **Function** | a named piece of code that takes inputs and gives back an answer |
| **2D list** | a list of lists, like a grid or a table: `grid[row][col]` |
| **Dashboard** | the web page that shows everything happening: open `http://<Pi's IP>:8080/` |
