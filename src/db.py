"""Shared database connection (agreed interface: get_connection)."""
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.join(ROOT, "movie.db")


def get_db_path():
    """Database file. Tests can point somewhere else with the MOVIE_DB variable."""
    return os.environ.get("MOVIE_DB", DEFAULT_DB)


def get_connection():
    """Open a connection.

    isolation_level=None means Python does NOT start transactions for us,
    so booking.py writes BEGIN / COMMIT / ROLLBACK itself.
    timeout=10 makes a second writer wait for the first instead of failing at once.
    """
    conn = sqlite3.connect(get_db_path(), timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite ignores foreign keys unless asked
    return conn
