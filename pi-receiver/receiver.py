#!/usr/bin/env python3
"""
CoT Forwarder receiver for Raspberry Pi (or any host).

Listens for the JSON messages emitted by the ATAK "CoT Forwarder" plugin over UDP
and/or TCP simultaneously (each message terminated by a newline '\\n').

Message format:
  UPDATE: {"action":"UPDATE","uid":..,"type":..,"callsign":..,"lat":..,"lon":..,"hae":..,"time":..}
  DELETE: {"action":"DELETE","uid":..,"time":..}

Configuration via environment variables:
  BIND_HOST  (default 0.0.0.0)
  PORT       (default 18999)
  PROTO      (udp | tcp | both ; default both)

Uses only the Python standard library (no dependencies).
(User-facing log output is intentionally in Polish; code comments are in English.)
"""

import json
import os
import socket
import sys
import threading
from datetime import datetime, timezone

BIND_HOST = os.environ.get("BIND_HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "18999"))
PROTO = os.environ.get("PROTO", "both").lower()

# Current state of tracked markers: uid -> last UPDATE payload.
_tracked = {}
_lock = threading.Lock()


def _ts():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def handle_message(raw, source):
    """Parse and handle a single JSON message."""
    raw = raw.strip()
    if not raw:
        return
    try:
        msg = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[{_ts()}] [BLAD JSON] od {source}: {e} :: {raw!r}", flush=True)
        return

    action = str(msg.get("action", "")).upper()
    uid = msg.get("uid", "?")

    if action == "UPDATE":
        lat = msg.get("lat")
        lon = msg.get("lon")
        typ = msg.get("type", "?")
        callsign = msg.get("callsign", uid)
        with _lock:
            _tracked[uid] = msg
            count = len(_tracked)
        print(f"[{_ts()}] [UPDATE] {callsign} uid={uid} type={typ} "
              f"pos={lat},{lon} (sledzonych: {count}) <- {source}", flush=True)
    elif action == "DELETE":
        with _lock:
            _tracked.pop(uid, None)
            count = len(_tracked)
        print(f"[{_ts()}] [DELETE] uid={uid} (sledzonych: {count}) <- {source}",
              flush=True)
    else:
        print(f"[{_ts()}] [NIEZNANE action={action}] {msg} <- {source}",
              flush=True)


def udp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((BIND_HOST, PORT))
    print(f"[{_ts()}] UDP nasluchuje na {BIND_HOST}:{PORT}", flush=True)
    while True:
        data, addr = s.recvfrom(65535)
        src = f"udp://{addr[0]}:{addr[1]}"
        # A single datagram may carry several newline-separated messages.
        for line in data.decode("utf-8", "replace").splitlines():
            handle_message(line, src)


def _tcp_client(conn, addr):
    src = f"tcp://{addr[0]}:{addr[1]}"
    print(f"[{_ts()}] TCP polaczenie z {src}", flush=True)
    buf = b""
    with conn:
        while True:
            try:
                chunk = conn.recv(4096)
            except OSError:
                break
            if not chunk:
                break
            buf += chunk
            # Split the stream on newline boundaries (handles partial/glued frames).
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                handle_message(line.decode("utf-8", "replace"), src)
    print(f"[{_ts()}] TCP rozlaczono {src}", flush=True)


def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((BIND_HOST, PORT))
    s.listen(8)
    print(f"[{_ts()}] TCP nasluchuje na {BIND_HOST}:{PORT}", flush=True)
    while True:
        conn, addr = s.accept()
        threading.Thread(target=_tcp_client, args=(conn, addr),
                         daemon=True).start()


def main():
    print(f"=== CoT Forwarder receiver === proto={PROTO} {BIND_HOST}:{PORT}",
          flush=True)
    threads = []
    if PROTO in ("udp", "both"):
        threads.append(threading.Thread(target=udp_server, daemon=True))
    if PROTO in ("tcp", "both"):
        threads.append(threading.Thread(target=tcp_server, daemon=True))
    if not threads:
        print(f"Nieznany PROTO={PROTO} (uzyj udp|tcp|both)", file=sys.stderr)
        sys.exit(1)
    for t in threads:
        t.start()
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nZatrzymano.", flush=True)


if __name__ == "__main__":
    main()
