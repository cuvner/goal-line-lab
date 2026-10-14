# You are the SCOREBOARD (the LED panel)

You control **256 coloured lights** in a panel 8 tall and 32 wide. Your Pico asks the Referee what's happening, and your code lights up **GOAL** and the **score**.

**Your file:** `scoreboard.py` on the scoreboard Pico (the `CIRCUITPY` drive). Open it in **Thonny**.
**When you save it**, the Pico restarts and checks your functions. Look in Thonny's **Shell** for ✓ and ✗.

## The grid
You draw with a **2D list** of numbers called `grid`, with one number per light:
```
grid[row][col]      row 0-7 (top to bottom), col 0-31 (left to right)
0 = off   1 = green   2 = yellow   3 = red   4 = blue   5 = white
```
So `grid[0][0] = 3` makes the top-left light red. The code you don't need to touch turns your grid into real lights.

---

## Stage 0: Swap addresses (10 min, with your team)
1. The Referee tells you the Pi's IP address. Open `settings.toml` on the Pico and change the `SERVER_URL` line to `SERVER_URL = "http://<the Pi's address>:8080"`. Save it.
2. The Pico restarts and prints **its own** address in big letters. Write it on the **team card** and give it to the Referee.

## Stage 1: Make a grid and draw on it (15 min)
**`make_grid()`** gives back 8 rows, where each row is a list of 32 zeros. Use two loops: for each of the 8 rows, make a new empty list, add 32 zeros to it, then add it to `grid`.

**`draw_test(grid)`** is for fun: draw anything you like by setting numbers in the grid, such as your initials, a smiley or a flag. Loops are great for lines: `for col in range(32): grid[0][col] = 3` draws a red line along the top.

With `TEST_MODE = True`, the panel shows only your `draw_test` drawing.

✅ **Checkpoint:** ✓ for all three `make_grid` checks, and your drawing appears on the panel.

💡 Watch out for the "separate lists" check. `[[0] * 32] * 8` *looks* right, but it makes 8 copies of the **same** row: change one and they all change! Make a new row inside your loop.

## Stage 2: Your letters (20 min)
A letter is a little 2D list: **7 rows of 5 numbers**, where `1` means lit. `G` is drawn for you:
```
[0, 1, 1, 1, 0]      .###.
[1, 0, 0, 0, 1]      #...#
[1, 0, 0, 0, 0]      #....
[1, 0, 1, 1, 1]  =   #.###
[1, 0, 0, 0, 1]      #...#
[1, 0, 0, 0, 1]      #...#
[0, 1, 1, 1, 0]      .###.
```
Draw **O**, **A** and **L** by changing 0s to 1s. Sketch them on squared paper first. Make them your own style if you like!

Then write **`draw_letter(grid, letter, top, left, colour)`**, which copies a letter onto the grid with its top-left corner at row `top`, column `left`:
- loop over every `row` and `col` of `letter`
- where it's a `1`, set `grid[top + row][left + col] = colour`
- **but** only if that row is 0–7 and that column is 0–31. Otherwise skip it, so a letter can hang off the edge without crashing (you'll want this for scrolling).

✅ **Checkpoint:** ✓ for `letter O/A/L is drawn` and all four `draw_letter` checks.

## Stage 3: GOAL and the score (15 min)
Set `TEST_MODE = False`. Now the Pico asks the Referee for the decision and the score.

**`draw_goal(grid, score, tick)`**: draw G, O, A and L, then the score. Letters are 5 wide, so leave a 1-light gap: columns **0, 6, 12, 18** for the letters and **26** for the number. The number is `DIGITS[score % 10]` (the digits are drawn for you in `digits.py`). Choose your colours!

**`draw_score(grid, score)`**: between goals, just show the number in the middle (column 14 or so).

✅ **Checkpoint:** ✓ for `draw_goal` and `draw_score`, the score shows on the panel, and when the Referee says GOAL the panel says **GOAL** with the score.

## Stage 4: Make it yours (as long as you like)
`tick` goes up by 1 five times a second. Use it in `draw_goal`:
- **Flash:** `if tick % 2 == 0:` use one colour, `else:` another.
- **Scroll:** work out `left = 32 - (tick % 70)` and draw the letters at `left`, `left + 6`, `left + 12`, `left + 18` and the number at `left + 26`. They slide in from the right and off the left (that's why `draw_letter` skips lights that are off the panel).
- **Rainbow:** a different colour for each letter.
- **Two-digit scores:** `score // 10` is the tens digit and `score % 10` is the units.
- Draw an exclamation mark `!` (it only needs 1 column wide) and add it after the L.

## More to try
- Move the letters down a row (`top = 1`) to see which looks best.
- Make `draw_score` show the number in a different colour when the score is 5 or more.
