# Lesson plan: Goal-line Lab (2 hours, open day)

## What it is
A fun, hands-on **proof of concept**, not a test. Teams of three 16-year-olds build a mini goal-line detector: an AI camera spots a football, a Raspberry Pi "referee" decides GOAL or NO GOAL, and an LED panel shows it, all talking over Wi-Fi. Visitors can kick (or roll) the ball and watch the scoreboard.

Students only write **short functions** using **loops, if-statements, 2D lists and reading text files**. All the networking and hardware code is given, and every function they write is checked automatically with ✓/✗ and a hint.

| Role | Builds | Guide | Python they use |
|---|---|---|---|
| **Referee** (server, on the Pi) | who's who, goal or no goal, the score, commentary | [role_referee.md](role_referee.md) | reading a file, 2D list, loops, if |
| **Spotter** (camera Pico) | wiring, training the camera, `find_ball`, `describe` | [role_spotter.md](role_spotter.md) | loop over a 2D list, if / elif / else |
| **Scoreboard** (LED Pico) | the grid, drawing the ball, loading and drawing a GOAL! picture | [role_scoreboard.md](role_scoreboard.md) | building a 2D list, nested loops, reading a file |

Start every student on [how_it_works.md](how_it_works.md) and the [team card](team_card.md).

## What they'll get out of it
- A real **client-server** system they built: "the Pi is the server, the Picos are clients".
- What an **IP address** is for, found hands-on by swapping addresses on the team card so the right data gets to the right device.
- Functions, loops, selection, 2D lists and file reading **doing something physical**.
- Working as a team to a shared plan where each part depends on the others.

## Timings

| Time | What | Teacher | Students |
|---|---|---|---|
| 0:00–0:10 | **Hook** | Demo the finished system: roll the ball over the line, GOAL! flashes, score goes up. Show the diagram in how_it_works.md. One sentence per role. | Form teams of 3, choose roles. |
| 0:10–0:25 | **Stage 0: addresses** | Hand out team cards. Walk round helping with `hostname -I`, `settings.toml` and `devices.txt`. | Referee finds the Pi's address → Picos put it in `settings.toml` → Picos print their addresses → Referee puts them in `devices.txt`. |
| 0:25–1:25 | **Build** | Checkpoints at **0:45**, **1:05** and **1:25** (see table). Circulate with [troubleshooting.md](troubleshooting.md). | Work through your stages. Each one has a ✅ checkpoint. |
| 1:25–1:45 | **Play** | Mark a real goal line with tape. Get the Spotter to read the ball's `x` on the line and the Referee to set `GOAL_LINE`. | Test it: roll the ball over the line, take the ball away, unplug the camera. Does it recover? Improve commentary and pictures. |
| 1:45–2:00 | **Show off** | Each team demos to the others (1 min). Quick questions below. | Demo. Leave it running for visitors. |

### Where each role should be at each checkpoint

| Checkpoint | Referee | Spotter | Scoreboard |
|---|---|---|---|
| 0:45 | Stage 1 done: CLIENTS shows `camera` and `scoreboard` | Stage 2 done: camera trained | Stage 1 done: drawing on the panel |
| 1:05 | Stage 2 done: GOAL / NO GOAL on dashboard | Stage 3 done: green box follows the ball | Stage 2 done: green dot follows the ball |
| 1:25 | Stage 3 done: score counts | Stage 4 done | Stage 3 done: GOAL! flashes |

Nobody is blocked by anyone else for long: the Spotter and Scoreboard each have their own checks and test modes, and the Referee's `test_referee.py` works without the Picos. If a Referee is stuck at stage 1, the teacher can drop in `server/solution/referee.py` so the team can carry on, then let them keep working on their own copy.

## Quick questions for the plenary (plain answers)
1. **Which device is the server?** The Pi. The Picos are clients: they start every conversation, and the Pi just answers.
2. **Why did we swap IP addresses?** So the Picos know where to send messages, and so the server knows who's who. It only takes the ball from the camera and only gives the decision to the scoreboard.
3. **How does the scoreboard know the camera's unplugged?** The server remembers *when* the last ball message arrived. If it's over 2 seconds old, everyone treats the camera as offline.
4. **Why count a goal only when the previous decision wasn't GOAL?** The ball stays over the line for a while, and the camera reports it 10 times a second. Without that check, one goal would count as 50.
5. **What could go wrong on a real network?** Anyone could pretend to be the camera, so real systems use passwords and encryption, not just addresses.

## If things go wrong on the day
- A Pico won't join the Wi-Fi: use the teacher's phone hotspot for the whole team (Pi and both Picos).
- The camera won't train: use a brightly coloured ball and a plain background.
- Running short on time: skip Referee stage 4, Spotter stage 4 and Scoreboard stage 4. The system works without them.
