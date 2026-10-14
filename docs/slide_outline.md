# Slide outline (for building the deck)

This is a suggested 18-slide deck for the 2-hour lesson. Slides 1-8 are the 15-minute intro. The rest stay on screen during the build, or come up at checkpoints. Take all facts and code from the other docs, not from memory.

1. **Title.** Goal-line Lab: build a networked goal-line detector in 2 hours. Show a photo or diagram of the finished system.
2. **Hook.** Real goal-line technology (Hawk-Eye / GLT) has to decide "goal or not" in under 1 second. How do the cameras get that decision to the referee's watch? Live demo: move the ball, and the panel and dashboard follow.
3. **The system.** A diagram of HuskyLens → camera Pico → Wi-Fi → server (Pi) → Wi-Fi → LED Pico → panel, with the browser dashboard also reading from the server. Label each arrow with its protocol (I2C, HTTP POST, HTTP GET).
4. **Client-server.** Who starts each conversation? Clients **request** and the server **responds**. Our server never contacts a Pico first. Compare with peer-to-peer.
5. **Anatomy of HTTP.** A real request and response for `POST /data/ball`: method, path, headers (`Content-Type`, `Content-Length`, `X-Pico-Name`), JSON body, then the status line `200 OK` and the JSON reply. Point out where TCP/IP and ports fit.
6. **GET vs POST, status codes.** GET reads and POST writes/creates (CRUD → HTTP). The codes we use: 200, 400, 404, 413, 501.
7. **JSON.** The `ball` message, both forms (`seen` true/false). Why JSON? It's human-readable and maps straight onto Python dicts. Compare with XML briefly.
8. **The contract.** protocol.md as the API: the endpoints table and the staleness rule (age > 2 s means offline). "If you all follow this, you can build at the same time."
9. **Roles.** Server / HuskyLens / LED panel, with what each one builds, its guide, and the hardware on their desk.
10. **The reference server.** Port 8081 vs 8080: test against a working server first, then swap in your own. This is like using a stub or test double. Show how to read a URL like `http://10.x.x.x:8081/data/ball`.
11. **Stage roadmap.** The checkpoint table (from the lesson plan), showing where each role should be at 0:40, 0:55, 1:10 and 1:25.
12. **Checkpoint slide (reuse it).** "Stop. Test. Does your checkpoint pass? Tell your team where you are." Keep a team tracker grid visible.
13. **Concurrency and locks.** Why the threaded server needs `with lock:`. Show a race condition in a two-thread timeline.
14. **Robustness.** Errors that will happen (Wi-Fi drops, unplugged camera, server restart) and how each part copes. Show the LED states table.
15. **Integration.** Switch `SERVER_URL` from 8081 to 8080, and find the broken hop using the debugging table from integration.md.
16. **Prove it.** The three failure tests (ball removed, camera unplugged, server stopped). It should recover by itself.
17. **Discuss.** The plenary questions from the lesson plan: decoupling, staleness detection, status codes, locks, security.
18. **Exit question and extensions.** The exit question from the lesson plan, plus "where next": WebSockets/push vs polling, authentication tokens, HTTPS.

## Visual style
- Use one diagram (slide 3) as the visual anchor, and repeat it small in the corner of later slides, with the part being discussed highlighted.
- Show code at a readable size, at most about 12 lines per slide, taken exactly from the repo files.
- Use the colours from the dashboard: green = OK or ball seen, amber = warning or no ball, red = offline or error, cyan = section headings.
