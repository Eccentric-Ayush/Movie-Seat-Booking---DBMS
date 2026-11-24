"""MV3 (Pankaj): the same race WITHOUT protection (the bug).

This uses its own throw-away database whose Bookings table has NO UNIQUE(show_id, seat_id)
and whose booking code has NO transaction: it checks "is the seat free?", pauses a moment,
then inserts. Both users pass the check before either one inserts, so BOTH succeed.

    terminal 1:  python demo/race_no_protection.py 1
    terminal 2:  python demo/race_no_protection.py 2

One-terminal shortcut:   python demo/race_no_protection.py --auto
Start over:              python demo/race_no_protection.py --reset
"""
import argparse
import os
import sqlite3
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNSAFE_DB = os.path.join(ROOT, "race_unprotected.db")


def connect():
    # isolation_level=None: autocommit, so there is no transaction around check + insert.
    conn = sqlite3.connect(UNSAFE_DB, timeout=10, isolation_level=None)
    # Same columns as the real table but WITHOUT the UNIQUE constraint.
    conn.execute(
        """CREATE TABLE IF NOT EXISTS Bookings (
               booking_id INTEGER PRIMARY KEY,
               user_id INTEGER NOT NULL,
               show_id INTEGER NOT NULL,
               seat_id INTEGER NOT NULL
           )"""
    )
    return conn


def unsafe_book(user_id, show_id, seat_id):
    conn = connect()
    taken = conn.execute(
        "SELECT 1 FROM Bookings WHERE show_id = ? AND seat_id = ?", (show_id, seat_id)
    ).fetchone()
    if taken:
        conn.close()
        return {"ok": False, "message": "Seat already taken for this show."}
    time.sleep(0.3)  # the gap in which the other user also passes the check
    conn.execute(
        "INSERT INTO Bookings (user_id, show_id, seat_id) VALUES (?, ?, ?)",
        (user_id, show_id, seat_id),
    )
    conn.close()
    return {"ok": True, "message": "Booking confirmed."}


def count_rows(show_id, seat_id):
    conn = connect()
    n = conn.execute(
        "SELECT COUNT(*) FROM Bookings WHERE show_id = ? AND seat_id = ?", (show_id, seat_id)
    ).fetchone()[0]
    conn.close()
    return n


def reset():
    conn = connect()
    conn.execute("DELETE FROM Bookings")
    conn.close()


def wait_until(epoch):
    while True:
        left = epoch - time.time()
        if left <= 0:
            return
        if sys.stdout.isatty():
            print(f"  firing in {left:4.1f} s", end="\r", flush=True)
        time.sleep(min(0.1, left))


def next_boundary(period=30):
    return (int(time.time() // period) + 1) * period


def run_one(user_id, show_id, seat_id, epoch):
    print(f"[user {user_id}] (NO protection) trying show {show_id}, seat {seat_id}")
    wait_until(epoch)
    result = unsafe_book(user_id, show_id, seat_id)
    status = "OK" if result["ok"] else "FAILED"
    print(f"\n[user {user_id}] {status}: {result['message']}")
    time.sleep(1.0)
    print(f"[user {user_id}] rows saved for this seat: {count_rows(show_id, seat_id)}")


def run_auto(show_id, seat_id):
    reset()
    epoch = time.time() + 2
    procs = []
    for user_id in (1, 2):
        cmd = [sys.executable, os.path.abspath(__file__), str(user_id),
               "--show", str(show_id), "--seat", str(seat_id), "--at-epoch", str(epoch)]
        procs.append(subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True))
    for p in procs:
        out, _ = p.communicate()
        print(out.replace("\r", "").strip())
        print("-" * 40)
    n = count_rows(show_id, seat_id)
    print(f"Final: {n} booking(s) exist for this seat" + (" <- DOUBLE BOOKING!" if n > 1 else ""))


def main():
    parser = argparse.ArgumentParser(description="Race test WITHOUT protection")
    parser.add_argument("user_id", nargs="?", type=int, help="user id (1-5)")
    parser.add_argument("--show", type=int, default=1)
    parser.add_argument("--seat", type=int, default=1)
    parser.add_argument("--auto", action="store_true", help="start two runs from this terminal")
    parser.add_argument("--reset", action="store_true", help="clear the demo table and exit")
    parser.add_argument("--at-epoch", type=float, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.reset:
        reset()
        print("Demo table cleared.")
    elif args.auto:
        run_auto(args.show, args.seat)
    elif args.user_id is None:
        parser.error("give a user id, or use --auto / --reset")
    else:
        run_one(args.user_id, args.show, args.seat, args.at_epoch or next_boundary())


if __name__ == "__main__":
    main()
