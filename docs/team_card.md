# Team card (print one per team)

**Team name:** ______________________________

| Device | Who | IP address | How to find it |
|---|---|---|---|
| **Referee** (Raspberry Pi) | | `____.____.____.____` | on the Pi, open a Terminal and type `hostname -I` (the first number) |
| **Spotter** (camera Pico) | | `____.____.____.____` | printed in big letters when the Pico starts |
| **Scoreboard** (LED Pico) | | `____.____.____.____` | printed in big letters when the Pico starts |

### Step 1: Referee → Picos
Give the Pi's address to both Pico people. In `settings.toml` on **each** Pico, change the server line to:
```
SERVER_URL = "http://____.____.____.____:8080"
```
Save it. The Pico restarts and prints its **own** address in big letters. Write it on this card.

### Step 2: Picos → Referee
Give both Pico addresses to the Referee, who puts them in `devices.txt` on the Pi:
```
camera,____.____.____.____
scoreboard,____.____.____.____
```

### Step 3: Watch the dashboard
On any computer, open **`http://<Pi's address>:8080/`**. Once the Referee's `who_is()` works, the CLIENTS box shows `camera` and `scoreboard` in green instead of "unknown" in red.
