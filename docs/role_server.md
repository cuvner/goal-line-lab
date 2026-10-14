# Role: Server

You're building the **server**, the middle of the system. The camera Pico sends the ball's position to you, and the LED panel Pico and the web dashboard read it from you. If the server is down, nothing works, so test each stage before moving on.

**You'll work on:** your team's Raspberry Pi, editing `server/server.py`. Use Thonny, or any editor plus a terminal.
**Your spec:** [protocol.md](protocol.md). Keep it open the whole time.
**Given to you:** `server/dashboard.html`, the web page your server sends to browsers. You don't need to edit it.

While you build, your teammates test against a **reference server** that's already running on your Pi on port **8081**. Yours runs on port **8080**. At integration, they switch their Picos over to yours.

## How to run and test
In one terminal, start your server:
```bash
cd ~/goal-line-lab/server
python3 server.py
```
In a second terminal, run the checker for the stage you've just finished:
```bash
cd ~/goal-line-lab/tools
python3 check_server.py --stage 1
```
Python only loads your code when the server starts, so **stop the server with Ctrl+C and start it again after every change.**

Find the Pi's IP address with `hostname -I`, and share it with your teammates.

---

## Stage 1: Serve the web page (target: 10 min)
**Goal:** a browser that asks for `/` gets `dashboard.html`.

Follow the numbered steps in the `STAGE 1` comment in `do_GET`. An HTTP response has three parts:
1. a **status line**, such as `HTTP/1.0 200 OK` (`send_response`)
2. **headers** (`send_header`), ending with a blank line (`end_headers`)
3. the **body**, which is the bytes of the file (`wfile.write`)

**Checkpoint**
- `python3 check_server.py --stage 1` passes.
- Open `http://<pi-ip>:8080/` on another computer. You should see the dashboard saying "No data yet". That's expected, because `/data` doesn't exist yet.

<details><summary>Hint</summary>

`open(PAGE_FILE, "rb")` opens the file in binary mode, so `.read()` gives `bytes`, which is what `wfile.write` needs. `Content-Length` is `str(len(page))`.
</details>

## Stage 2: GET a channel (target: 10 min)
**Goal:** `GET /data/<channel>` returns `{"data": ..., "age": ...}`.

`channels` is a dictionary: `name -> (data, time_received)`. It already has a `test` channel in it.
- If `name` isn't in `channels`, reply `{"data": None, "age": None}`.
- Otherwise reply with the data and `round(time.time() - time_received, 2)`.
- Do all the reading inside `with lock:`.

This logic is needed again in stage 4, so write it as a function, for example `channel_info(name)`, outside the class.

**Checkpoint**
- `check_server.py --stage 2` passes.
- `http://<pi-ip>:8080/data/test` in a browser shows `{"data": {"hello": "world"}, "age": ...}`, and the age goes up each time you refresh.

<details><summary>Hint</summary>

```python
def channel_info(name):
    with lock:
        if name not in channels:
            return {"data": None, "age": None}
        data, received = channels[name]
    return {"data": data, "age": round(time.time() - received, 2)}
```
</details>

## Stage 3: POST to a channel (target: 15 min)
**Goal:** clients can send data. Follow the `STAGE 3` steps in `do_POST`.

- Read exactly `Content-Length` bytes. HTTP has no "end of message" marker, so this is how the server knows where the body ends.
- Bad JSON must return **400** and must **not** change the stored data.

**Checkpoint**
- `check_server.py --stage 3` passes.
- Send a test message with `curl`:
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"seen": false}' localhost:8080/data/ball
  ```
- Send fake ball positions for 10 seconds:
  ```bash
  python3 ~/goal-line-lab/tools/fake_camera.py
  ```
  Leave it running and refresh `/data/ball`. The numbers should change.

**Think:** why is a lock needed? What could go wrong if the HuskyLens Pico POSTs while the LED Pico is in the middle of a GET?

## Stage 4: GET every channel (target: 10 min)
**Goal:** `GET /data` returns every channel, for example `{"ball": {"data": ..., "age": ...}, "test": {...}}`.

Copy the channel names inside the lock, then build the reply with your stage 2 function.

**Checkpoint**
- `check_server.py --stage 4` passes.
- Run `fake_camera.py`, then open the dashboard: **the CAMERA panel shows the bouncing ball**, and CHANNELS lists `ball` and `test`.

> Stages 1-4 are everything your team needs. Tell your teammates you're ready for integration, and see [integration.md](integration.md).

## Stage 5 (extension): `/stats` (target: 15 min)
**Goal:** the dashboard's CLIENTS and EVENTS panels work.

The format is in [protocol.md, GET /stats](protocol.md#get-stats). You'll need to:
- record each request to `/data/<channel>`: the client's IP is `self.client_address[0]` and its name is `self.headers.get("X-Pico-Name", "")`
- keep an `events` list, adding an event when you see a new client or channel, or an error
- work out `rate`: keep the recent request times, for example in `collections.deque(maxlen=200)`, and count how many are in the last 5 seconds

**Checkpoint:** `check_server.py --stage 5` passes, and the dashboard's CLIENTS panel lists `huskylens` and `led_panel` once they're connected.

## More extensions
- **Hardening:** reject POST bodies over 4096 bytes with 413. Why does a server on a shared network need limits like this? What else could a malicious client do?
- **Run on boot:** install the server as a `systemd` service (see `server/solution/goal-line-server.service`).
- **Terminal dashboard:** run `server/solution/terminal_dashboard.py` and read how it uses `/stats`.
- **Think:** the LED Pico polls 5 times a second, even when nothing has changed. What would be better, and what would it cost? Research WebSockets or long polling.
