# Slide outline

Keep it short: the intro is 10 minutes, and the rest are "stay on screen" slides. Big text, few words, lots of pictures. Take all facts from the other docs.

## Intro (slides 1–6, 10 minutes)
1. **Goal-line Lab.** A photo of the finished setup. "Today you build this."
2. **The real thing.** Real goal-line technology: cameras watch the line and buzz the ref's watch in under a second. We're building a mini one.
3. **How it works.** The diagram from how_it_works.md: Spotter → Referee → Scoreboard, plus the dashboard. One arrow at a time.
4. **Three jobs.** Spotter (camera), Referee (the server on the Pi), Scoreboard (LED panel). One line each on what they write. "You only edit your own file. Everything else is done."
5. **Addresses.** Every device has an IP address, like a house number. The Picos need the Pi's address, the Pi needs the Picos' addresses. Show the team card. "First job: swap addresses."
6. **How you'll know it's working.** Thonny's Shell shows ✓ and ✗ with hints. The dashboard shows everything live. Each stage has a ✅ checkpoint.

## During the build (leave up, or switch at checkpoints)
7. **Team card and stage 0 steps.** The three steps from team_card.md, big.
8. **Checkpoint tracker.** The table from lesson_plan.md: where each role should be at 0:45, 1:05 and 1:25. Tick teams off on the board.
9. **The grid** (for the Scoreboard). `grid[row][col]`, the colour numbers, and a picture of the 8×32 panel with row 0 and col 0 labelled.
10. **The blocks list** (for the Spotter). The 2D list with `x, y, width, height, id` labelled, and the 320×240 picture with (0, 0) top-left.
11. **The address book** (for the Referee). `devices.txt` next to the 2D list it becomes, and what `who_is` should give back.
12. **Stuck?** The "finding the broken link" table from troubleshooting.md.

## Play and show off (slides 13–15)
13. **Set the goal line.** Tape on the floor; Spotter reads `x` on the dashboard; Referee sets `GOAL_LINE`.
14. **Break it!** Take the ball away. Unplug the camera. Does it recover by itself?
15. **Quick questions.** The five plenary questions from lesson_plan.md, one at a time.

## Style
- At most 20 words of text per slide, apart from the code and table slides.
- Code only in the three "cheat sheet" slides (9–11), copied exactly from the student files.
- Dashboard colours: green = good, yellow = no ball, red = problem, blue = headings.
