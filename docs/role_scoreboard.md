# You are the SCOREBOARD (the LED panel)

You control **256 coloured lights** in a panel 8 tall and 32 wide. Your Pico asks the Referee what's happening, and your code draws it: the ball, or a big **GOAL!**

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

## Stage 1: Make a grid and draw on it (20 min)
**`make_grid()`** gives back 8 rows, where each row is a list of 32 zeros. Use two loops: for each of the 8 rows, make a new empty list, add 32 zeros to it, then add it to `grid`.

**`draw_test(grid)`** is for fun: draw anything you like by setting numbers in the grid, such as your initials, a smiley or a flag. Loops are great for lines: `for col in range(32): grid[0][col] = 3` draws a red line along the top.

With `TEST_MODE = True`, the panel shows only your `draw_test` drawing.

✅ **Checkpoint:** ✓ for all three `make_grid` checks, and your drawing appears on the panel.

💡 Watch out for the "separate lists" check. `[[0] * 32] * 8` *looks* right, but it makes 8 copies of the **same** row: change one and they all change! Make a new row inside your loop.

## Stage 2: Draw the ball (15 min)
Set `TEST_MODE = False`. Now the Pico asks the Referee for the ball's position.

**`draw_ball(grid, x, y)`**: the camera's picture is 320 × 240, but the panel is only 32 × 8, so you need to scale:
```python
col = x // 10      # 320 / 32 = 10
row = y // 30      # 240 / 8  = 30
```
Then set that place in the grid to `GREEN`. Careful: `x` can be 320, which makes `col` 32, and that's off the end of the grid! If `col` is bigger than 31, make it 31. Do the same for `row` and 7.

✅ **Checkpoint:** ✓ for `draw_ball`, and a green dot on the panel follows the ball.

## Stage 3: GOAL! (15 min)
`goal.txt` holds a picture made of characters: `#` means light on and `.` means off.

**`load_picture(filename)`**: read the file and give back a 2D list of characters, one row per line. `list(line.strip())` turns `"..##.."` into `[".", ".", "#", "#", ".", "."]`.

**`draw_picture(grid, picture, colour)`**: loop over every row and column of `picture`. Wherever it's `"#"`, set the same place in `grid` to `colour`.

✅ **Checkpoint:** ✓ for both, and when the Referee says GOAL, the panel flashes **GOAL!**

## Stage 4: Your own picture (10 min)
When the camera can't see the ball, the panel shows `my_picture.txt` (a smiley). Open it in Thonny and design your own: 8 lines of 32 characters, using `#` and `.`. Save it, then unplug and replug the Pico.

## More to try
- Write `draw_goal_line(grid, line_x)`, which draws the goal line as a blue column (`col = line_x // 10`). The code already uses it if it exists!
- Make the ball 2 × 2 lights instead of 1.
- Design a `nogoal.txt` picture (and ask your teacher to show it).
