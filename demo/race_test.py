"""MV3 (Pankaj): the race test WITH protection (transaction + UNIQUE constraint).

Two-terminal demo, run from the repo root (after python db/seed.py):

    terminal 1:  python demo/race_test.py 1
    terminal 2:  python demo/race_test.py 2

Both terminals wait for the next :00 or :30 on the clock, then fire at the same moment.
Exactly one prints OK, the other prints "Seat already taken".

One-terminal shortcut that starts both runs itself:   python demo/race_test.py --auto
Free the seat again before repeating:                 python demo/race_test.py --reset
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.booking import book_seat  # noqa: E402
from src.db import get_connection  # noqa: E402


def reset_seat(show_id, seat_id):
    conn = get_connection()
    conn.execute("DELETE FROM Bookings WHERE show_id = ? AND seat_id = ?", (show_id, seat_id))
    conn.close()


def count_rows(show_id, seat_id):
    conn = get_connection()
    n = conn.execute(
        "SELECT COUNT(*) FROM Bookings WHERE show_id = ? AND seat_id = ?", (show_id, seat_id)
    ).fetchone()[0]
    conn.close()
    return n


def wait_until(epoch):
    while True:
        left = epoch - time.time()
        if left <= 0:
            return
        if sys.stdout.isatty():
            print(f"  firing in {left:4.1f} s", end="\r", flush=True)
        time.sleep(min(0.1, left))


def next_boundary(period=30):
    now = time.time()
    return (int(now // period) + 1) * period


def run_one(user_id, show_id, seat_id, epoch):
    print(f"[user {user_id}] trying show {show_id}, seat {seat_id}")
    wait_until(epoch)
    result = book_seat(user_id, show_id, seat_id)
    status = "OK" if result["ok"] else "FAILED"
    print(f"\n[user {user_id}] {status}: {result['message']}")
    time.sleep(0.5)
    print(f"[user {user_id}] rows saved for this seat: {count_rows(show_id, seat_id)}")


def run_auto(show_id, seat_id):
    reset_seat(show_id, seat_id)
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
    print(f"Final: {count_rows(show_id, seat_id)} booking(s) exist for this seat (must be 1).")


def main():
    parser = argparse.ArgumentParser(description="Race test WITH protection")
    parser.add_argument("user_id", nargs="?", type=int, help="user id (1-5)")
    parser.add_argument("--show", type=int, default=1)
    parser.add_argument("--seat", type=int, default=1)
    parser.add_argument("--auto", action="store_true", help="start two runs from this terminal")
    parser.add_argument("--reset", action="store_true", help="free the seat and exit")
    parser.add_argument("--at-epoch", type=float, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.reset:
        reset_seat(args.show, args.seat)
        print("Seat is free again.")
    elif args.auto:
        run_auto(args.show, args.seat)
    elif args.user_id is None:
        parser.error("give a user id, or use --auto / --reset")
    else:
        run_one(args.user_id, args.show, args.seat, args.at_epoch or next_boundary())


if __name__ == "__main__":
    main()
