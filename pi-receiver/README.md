# CoT Forwarder — receiver (Raspberry Pi / any host)

The receiving end of the **CoT Forwarder** ATAK plugin (sibling folder
`../CotForwarderPlugin/`). It listens for the line-framed JSON the plugin emits over
UDP and/or TCP, and prints a human-readable log of which markers are being tracked.

It is a single file, **`receiver.py`**, using only the Python 3 standard library — drop
it on a Raspberry Pi (or any machine) and run it. Treat it as the starting point:
replace the `print(...)` calls in `handle_message()` with whatever you actually need
(drive an LED, write to a DB, re-broadcast, etc.).

---

## 1. What it does

- Binds a **UDP** server and a **TCP** server on the same port (default `18999`).
- Reassembles messages by newline (`\n`) framing: handles several messages glued into
  one TCP write, one message split across packets, and multiple messages in one UDP
  datagram.
- Maintains an in-memory set of currently-tracked markers (`uid → last UPDATE`) and
  prints every event with a running count.
- Malformed JSON is logged and skipped — a bad packet never crashes the server.

### Message format (from the plugin)

One JSON object per line, UTF-8:

```json
{"action":"UPDATE","uid":"ABC-123","type":"a-h-G","callsign":"Alpha","lat":52.2297,"lon":21.0122,"hae":135.0,"time":1718200000000}
{"action":"DELETE","uid":"ABC-123","time":1718200000000}
```

| Field | Meaning |
|---|---|
| `action` | `UPDATE` (marker is ON / moved) or `DELETE` (toggled OFF / removed) |
| `uid` | ATAK marker UID — the stable identifier to key on |
| `type` | CoT type, e.g. `a-h-G` (hostile ground), `a-f-G` (friendly ground) |
| `callsign` | marker callsign (falls back to the UID) |
| `lat`,`lon` | WGS-84 degrees |
| `hae` | height above ellipsoid, metres (`0.0` if unknown) |
| `time` | sender epoch milliseconds |

### Example output

The receiver's console output is in Polish (`nasluchuje` = listening, `sledzonych` =
tracked count, `[BLAD JSON]` = JSON error):

```
=== CoT Forwarder receiver === proto=both 0.0.0.0:18999
[10:58:09] UDP nasluchuje na 0.0.0.0:18999
[10:58:09] TCP nasluchuje na 0.0.0.0:18999
[10:58:23] [UPDATE] Alpha uid=ABC-123 type=a-h-G pos=52.2297,21.0122 (sledzonych: 1) <- udp://10.0.0.5:49580
[10:58:25] [DELETE] uid=ABC-123 (sledzonych: 0) <- udp://10.0.0.5:49580
```

---

## 2. Requirements

- **Python 3.8+** (standard library only — `requirements.txt` is intentionally empty), or
- **Docker** (a `Dockerfile` and `docker-compose.yml` are provided).

---

## 3. Run it directly

```bash
cd pi-receiver
python3 receiver.py
```

Configuration is via environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `BIND_HOST` | `0.0.0.0` | interface to bind (all by default) |
| `PORT` | `18999` | UDP+TCP port (must match the plugin's setting) |
| `PROTO` | `both` | `udp`, `tcp`, or `both` |

Examples:

```bash
PORT=18999 PROTO=udp python3 receiver.py        # UDP only
BIND_HOST=192.168.42.50 python3 receiver.py     # bind one interface
```

Stop with `Ctrl-C`.

---

## 4. Run it with Docker

```bash
cd pi-receiver
docker compose up --build          # uses docker-compose.yml (network_mode: host)
# logs:
docker logs -f cot-receiver
```

`docker-compose.yml` uses `network_mode: host` so the container receives traffic
directly on the Pi's interfaces (e.g. `usb0`) with no NAT — recommended on a Pi.
Override `BIND_HOST` / `PORT` / `PROTO` in the `environment:` block.

Or build/run by hand:

```bash
docker build -t cot-receiver .
docker run --rm --network host -e PROTO=both cot-receiver
```

---

## 5. Network setup (connecting ATAK ↔ Pi)

The plugin sends to the **IP / Port / Protocol** configured in
*ATAK → Settings → Tool Preferences → CoT Forwarder*. Make them match this receiver.

- **Android phone ↔ Raspberry Pi over USB tethering:** enable USB tethering on the
  phone; the Pi gets an address on `usb0` (often `192.168.42.x`, phone is the gateway).
  Point the plugin's IP at the Pi's `usb0` address, run the receiver with
  `BIND_HOST=0.0.0.0` (the default).
- **Same Wi-Fi/LAN:** use the Pi's LAN IP.
- **Android emulator → receiver on your dev PC:** from the emulator the host machine is
  `10.0.2.2`. Run the receiver on the PC and set the plugin's IP to `10.0.2.2`.
- **UDP vs TCP:** UDP is fire-and-forget (lower overhead, fine on a stable local link);
  TCP keeps a connection and is more reliable over lossy links. The receiver accepts
  both at once (`PROTO=both`).

> Make sure the host firewall allows inbound `18999/udp` (and `/tcp` if used).

---

## 6. Test without ATAK

`test_network.py` is a self-contained check: it launches `receiver.py`, then a "fake
sender" emits exactly the bytes `NetworkManager.java` produces (UDP + TCP, glued and
split frames, multi-line datagram, malformed JSON) and asserts the receiver handled
each correctly.

```bash
cd pi-receiver
python3 test_network.py
# ... prints PASS/FAIL per check; exit code 0 = all passed
```

Use it after changing `receiver.py` to confirm you didn't break the framing/parsing.

---

## 7. Extending it

All real logic goes in `handle_message(raw, source)`:

- `action == "UPDATE"` → a marker is active or moved (`msg["uid"]`, `lat`, `lon`,
  `type`, `callsign`, …). The `_tracked` dict holds the latest payload per UID.
- `action == "DELETE"` → stop tracking `msg["uid"]`.

Replace the `print(...)` calls with your sink (GPIO/LED, sqlite, MQTT, serial, another
socket…). Keep it quick or hand work off to a thread/queue so you don't stall the
UDP/TCP receive loops.

---

## 8. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| No output when toggling in ATAK | Wrong IP/Port/Protocol in the plugin's Tool Preferences, or a firewall blocking `18999`. Confirm the plugin shows the right host. |
| `[BLAD JSON]` lines | A non-JSON packet reached the port (something else sending to it). The receiver skips it safely. |
| `Address already in use` | Another process holds `18999`. Stop it or change `PORT` (and the plugin's port). |
| Works on `localhost` but not from the phone | `BIND_HOST` too narrow, or the Pi/host firewall blocks the port. Bind `0.0.0.0` and open the port. |
| Emulator can't reach the receiver | Use `10.0.2.2` as the plugin IP and run the receiver on the dev PC. |
