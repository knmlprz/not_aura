#!/usr/bin/env python3
"""
Network test for the receiver, without ATAK. A "fake sender" emits EXACTLY the bytes
that NetworkManager.java sends -> payload = (json + "\n") encoded as UTF-8.

It verifies:
  - UDP: UPDATE, UPDATE (movement), DELETE
  - UDP: two messages in a single datagram (receiver splitlines)
  - TCP: one persistent connection, several messages
  - TCP: two messages glued into a single write (newline framing)
  - TCP: one message split across two writes (buffer reassembly)
  - malformed JSON (the receiver must survive and log an error)

Runs receiver.py as a subprocess, sends the messages, then checks its stdout.
Exit code 0 = all checks passed, 1 = something failed.
(Console output is in Polish to match receiver.py; code comments are in English.)
"""
import json
import os
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RECEIVER = os.path.join(HERE, "receiver.py")
HOST = "127.0.0.1"
PORT = 18999


def nm_payload(obj):
    """Same framing as NetworkManager: json + '\n', UTF-8."""
    return (json.dumps(obj) + "\n").encode("utf-8")


def update(uid, typ, callsign, lat, lon, hae):
    return {"action": "UPDATE", "uid": uid, "type": typ, "callsign": callsign,
            "lat": lat, "lon": lon, "hae": hae, "time": int(time.time() * 1000)}


def delete(uid):
    return {"action": "DELETE", "uid": uid, "time": int(time.time() * 1000)}


def run_receiver():
    env = dict(os.environ, BIND_HOST=HOST, PORT=str(PORT), PROTO="both")
    return subprocess.Popen([sys.executable, RECEIVER], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)


def main():
    proc = run_receiver()
    time.sleep(1.2)  # give the UDP + TCP servers time to bind

    # --- UDP ---
    us = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    us.sendto(nm_payload(update("ALPHA-1", "a-h-G", "Alpha", 52.2297, 21.0122, 135.0)), (HOST, PORT))
    time.sleep(0.05)
    us.sendto(nm_payload(update("ALPHA-1", "a-h-G", "Alpha", 52.2300, 21.0130, 140.0)), (HOST, PORT))
    time.sleep(0.05)
    # two messages in a single datagram
    two = nm_payload(update("BRAVO-2", "a-f-G", "Bravo", 50.0, 19.9, 200.0)) + \
          nm_payload(delete("BRAVO-2"))
    us.sendto(two, (HOST, PORT))
    time.sleep(0.05)
    us.sendto(nm_payload(delete("ALPHA-1")), (HOST, PORT))
    time.sleep(0.05)
    us.close()

    # --- TCP ---
    ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts.connect((HOST, PORT))
    ts.sendall(nm_payload(update("CHARLIE-3", "a-h-A", "Charlie", 48.1, 17.1, 300.0)))
    time.sleep(0.05)
    # two messages glued into a single write
    glued = nm_payload(update("DELTA-4", "a-f-A", "Delta", 47.0, 16.0, 50.0)) + \
            nm_payload(update("ECHO-5", "a-n-G", "Echo", 46.0, 15.0, 70.0))
    ts.sendall(glued)
    time.sleep(0.05)
    # one message split across two packets
    raw = nm_payload(delete("CHARLIE-3"))
    ts.sendall(raw[:10]); time.sleep(0.05); ts.sendall(raw[10:])
    time.sleep(0.05)
    # malformed JSON
    ts.sendall(b'{not-json}\n')
    time.sleep(0.05)
    ts.close()

    time.sleep(0.4)
    proc.terminate()
    try:
        out, _ = proc.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()

    print("================ STDOUT ODBIORNIKA ================")
    print(out)
    print("================ WERYFIKACJA ================")
    # NOTE: these assertions match receiver.py's Polish output strings.
    checks = [
        ("UDP UPDATE Alpha (1. poz)",       "pos=52.2297,21.0122" in out),
        ("UDP UPDATE Alpha (ruch)",         "pos=52.23,21.013" in out or "pos=52.2300" in out or "21.013" in out),
        ("UDP multi-line UPDATE Bravo",     "Bravo uid=BRAVO-2" in out),
        ("UDP multi-line DELETE Bravo",     "[DELETE] uid=BRAVO-2" in out),
        ("UDP DELETE Alpha",                "[DELETE] uid=ALPHA-1" in out),
        ("TCP UPDATE Charlie",              "Charlie uid=CHARLIE-3" in out),
        ("TCP sklejone UPDATE Delta",       "Delta uid=DELTA-4" in out),
        ("TCP sklejone UPDATE Echo",        "Echo uid=ECHO-5" in out),
        ("TCP rozbita DELETE Charlie",      "[DELETE] uid=CHARLIE-3" in out),
        ("uszkodzony JSON obsluzony",       "[BLAD JSON]" in out),
        ("odbiornik przezyl do konca",      "TCP rozlaczono" in out or "TCP polaczenie" in out),
    ]
    ok = True
    for name, passed in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        ok = ok and passed
    print("================")
    print("WYNIK:", "WSZYSTKO OK" if ok else "SA BLEDY")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
