# Lesson plan: Goal-line Lab (2 hours, A Level Computer Science)

## Overview
Teams of three build a small networked **goal-line detector**. A camera client reports the football's position to a server, a display client shows it on an LED panel, and a web dashboard watches all the traffic. Each student owns one part, and the three parts must work together through an agreed **protocol** ([protocol.md](protocol.md)).

| Role | Builds | Guide |
|---|---|---|
| Server | a Python HTTP server on the Raspberry Pi | [role_server.md](role_server.md) |
| HuskyLens | a camera client on a Pico 2 W (I2C in, HTTP POST out) | [role_huskylens.md](role_huskylens.md) |
| LED panel | a display client on a Pico 2 W (HTTP GET in, NeoPixels out) | [role_led_panel.md](role_led_panel.md) |

The teacher provides the web dashboard (`server/dashboard.html`), the Pico libraries (`pico_lib/`), and a **reference server** on every team's Pi on port 8081. The reference server means the two client students aren't blocked waiting for the server student.

## Learning objectives
By the end, students can:
1. Explain the **client-server model** using a system they built, including who starts each exchange and why.
2. Describe the parts of an **HTTP request and response** (method, path, headers, body, status code) and use **GET** and **POST** correctly.
3. Represent and exchange structured data as **JSON**.
4. Use **IP addresses and ports** to address a service on a network.
5. Explain how a **shared specification (API)** lets a team develop in parallel, and test against it with stubs and test tools.
6. Make networked software **robust**: handling errors, timeouts and stale data, and detecting failure.

## Specification links
- **Networking:** the client-server model, protocols, the TCP/IP stack (HTTP at the application layer, TCP at the transport layer, IP at the network layer), IP addresses, ports and sockets.
- **Web technologies:** HTTP methods and status codes, APIs, JSON (and how it compares with XML), the REST style of mapping CRUD to HTTP methods (POST = create/update, GET = read).
- **Software development:** decomposition, abstraction (PicoComs and the HuskyLens driver hide details), testing (`check_server.py` is an automated test, `fake_camera.py` is a stub), and concurrency (the threaded server needs a lock).
- **Hardware and other:** I2C as a serial bus with addressed devices, coordinate scaling, and data representation (bytes, checksums and little-endian numbers in the HuskyLens protocol, as an extension).

## Timings

| Time | Phase | Teacher | Students |
|---|---|---|---|
| 0:00-0:15 | **Hook and big picture** | Demo the finished system: move the ball, and the panel and dashboard follow. Show the diagram in protocol.md. Explain client vs server, HTTP GET/POST, JSON and polling. Show the protocol as a "contract". | Form teams and choose roles. |
| 0:15-0:25 | **Set-up** | Hand out Pi IPs. Check the reference server works on each Pi (`http://<pi>:8081/`). | Open your role guide. Server: open a terminal on the Pi. Picos: open Thonny/Mu, check the `CIRCUITPY` drive and `settings.toml`. |
| 0:25-1:25 | **Build in stages** | Call a **checkpoint every 15 min** (0:40, 0:55, 1:10, 1:25) and tick off stages on the board below. Circulate. Use the troubleshooting guide. | Work through your stages. Test at each checkpoint before moving on. |
| 1:25-1:45 | **Integration** | Teams switch to their own server ([integration.md](integration.md)). Model the debugging method: find the broken hop. | Connect, test, and prove it recovers from failures. |
| 1:45-2:00 | **Plenary** | 1-minute demo per team. Discussion questions (below). Exit question. | Demo, then answer the team questions in integration.md. |

### Target stage by checkpoint

| Checkpoint | Server | HuskyLens | LED panel |
|---|---|---|---|
| 0:40 | 1 (page) done | 1 (wired, 0x32 found) done | 1 in progress |
| 0:55 | 2 (GET) and 3 (POST) under way | 2 (trained) and 3 (reading) done | 1 (index) done, 2 under way |
| 1:10 | 3 done, 4 under way | 4 (sending) done | 2 (drawing) done, 3 under way |
| 1:25 | 4 done, 5 optional | 5 (robust) done | 3 and 4 done |

Fast finishers do the extensions at the end of each role guide. Struggling students use the `<details>` hints. For the most stuck, the teacher can show the matching part of the `solution/` file.

## Differentiation
- **Support:** every stage has a checkpoint and a hint. The server role has a self-check tool, and both Pico roles have test modes (`i2c_scan.py`, `MODE = "chase"`/`"test_pattern"`/`"fake_ball"`). Pair a weaker student with the HuskyLens role: it's the most hands-on, and its code is the shortest.
- **Stretch:** server stage 5 (`/stats`), hardening (body size limits), the HuskyLens bandwidth/heartbeat extension, LED text scrolling, the goal-line decision channel, and reading the HuskyLens byte protocol.

## Plenary questions (with model answers)
1. **Why does the LED panel ask the server, rather than the camera telling the panel directly?** The server decouples them: either side can restart or be replaced, and more displays or loggers can be added without changing the camera. The cost is an extra hop (latency) and a single point of failure.
2. **How does the LED panel know the camera is offline when nobody tells it?** The server timestamps each update. The client compares the `age` with a 2-second threshold, so a missing heartbeat counts as a failure.
3. **What does the 400 status tell a client, compared with 404 and 501?** 400 means the request was malformed, 404 means there's no such resource, and 501 means the server hasn't implemented it yet. Clients can react differently to each.
4. **Why did the server need a lock?** Requests are handled by several threads at once. Without a lock, a read could see a half-updated shared dictionary, or two writes could race.
5. **Name a security weakness and a fix.** Anyone can POST fake data (no authentication), so add a shared secret or token header. A client could also flood the server or send huge bodies, so add rate limits and size limits (413). Traffic is plain HTTP and can be read on the network, so use HTTPS/TLS.

## Exit question
*"Explain, using HTTP, JSON and the client-server model, how a ball moving in front of the camera ends up lit on the LED panel."* Look for: the camera client POSTs JSON to the server; the server stores it with a timestamp; the display client polls with GET; the server replies with the data and its age; the client scales the coordinates and lights the LEDs.
