"""MV1 (Ananya): create the database from schema.sql and fill it with sample data.

Run from the repo root:   python db/seed.py
WARNING: this deletes and rebuilds the database file.
"""
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.db import get_db_path  # noqa: E402

SCHEMA_FILE = os.path.join(ROOT, "db", "schema.sql")

MOVIES = [
    (1, "Interstellar", 169),
    (2, "Inception", 148),
    (3, "The Lion King", 88),
]

SHOWS = [  # (show_id, movie_id, show_time)
    (1, 1, "2026-12-01 10:00"),
    (2, 1, "2026-12-01 18:00"),
    (3, 2, "2026-12-01 14:00"),
    (4, 2, "2026-12-02 20:00"),
    (5, 3, "2026-12-02 11:00"),
]

USERS = [
    (1, "Aarav", "aarav@example.com"),
    (2, "Diya", "diya@example.com"),
    (3, "Rohan", "rohan@example.com"),
    (4, "Meera", "meera@example.com"),
    (5, "Kabir", "kabir@example.com"),
]

ROWS = "ABCDE"      # 5 rows
SEATS_PER_ROW = 8   # x 8 seats = 40 seats


def seed(db_path=None):
    """Rebuild the database at db_path (default: the normal database file)."""
    db_path = db_path or get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    with open(SCHEMA_FILE, encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.executemany("INSERT INTO Movies VALUES (?, ?, ?)", MOVIES)
    conn.executemany("INSERT INTO Shows VALUES (?, ?, ?)", SHOWS)
    conn.executemany("INSERT INTO Users VALUES (?, ?, ?)", USERS)

    seat_id = 1
    for row in ROWS:
        for number in range(1, SEATS_PER_ROW + 1):
            conn.execute(
                "INSERT INTO Seats (seat_id, row_label, seat_number) VALUES (?, ?, ?)",
                (seat_id, row, number),
            )
            seat_id += 1

    conn.commit()
    conn.close()
    return db_path


if __name__ == "__main__":
    path = seed()
    print(f"Database created at {path}")
    print(f"{len(MOVIES)} movies, {len(SHOWS)} shows, "
          f"{len(ROWS) * SEATS_PER_ROW} seats, {len(USERS)} users.")
