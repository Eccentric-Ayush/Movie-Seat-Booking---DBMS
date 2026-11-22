"""MV2 (Shivam): book and cancel with real transactions.

Both functions return {'ok': bool, 'message': str} and never leave a half-saved change.
"""
import sqlite3

from src.db import get_connection


def _exists(conn, table, column, value):
    row = conn.execute(f"SELECT 1 FROM {table} WHERE {column} = ?", (value,)).fetchone()
    return row is not None


def _rollback(conn):
    if conn.in_transaction:
        conn.execute("ROLLBACK")


def book_seat(user_id, show_id, seat_id):
    conn = get_connection()
    try:
        # IMMEDIATE takes the write lock now, so two bookings cannot interleave
        # between the "is it free?" check and the INSERT.
        conn.execute("BEGIN IMMEDIATE")

        if not _exists(conn, "Users", "user_id", user_id):
            _rollback(conn)
            return {"ok": False, "message": f"User {user_id} does not exist."}
        if not _exists(conn, "Shows", "show_id", show_id):
            _rollback(conn)
            return {"ok": False, "message": f"Show {show_id} does not exist."}
        if not _exists(conn, "Seats", "seat_id", seat_id):
            _rollback(conn)
            return {"ok": False, "message": f"Seat {seat_id} does not exist."}

        taken = conn.execute(
            "SELECT 1 FROM Bookings WHERE show_id = ? AND seat_id = ?",
            (show_id, seat_id),
        ).fetchone()
        if taken:
            _rollback(conn)
            return {"ok": False, "message": "Seat already taken for this show."}

        conn.execute(
            "INSERT INTO Bookings (user_id, show_id, seat_id) VALUES (?, ?, ?)",
            (user_id, show_id, seat_id),
        )
        conn.execute("COMMIT")
        return {"ok": True, "message": "Booking confirmed."}

    except sqlite3.IntegrityError:
        # Safety net: UNIQUE(show_id, seat_id) fired even though the check passed.
        _rollback(conn)
        return {"ok": False, "message": "Seat already taken for this show."}
    except sqlite3.OperationalError as err:
        _rollback(conn)
        return {"ok": False, "message": f"Database busy or unavailable, nothing saved ({err})."}
    except sqlite3.Error as err:
        _rollback(conn)
        return {"ok": False, "message": f"Booking failed, nothing saved ({err})."}
    finally:
        conn.close()


def cancel_booking(booking_id):
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        row = conn.execute(
            "SELECT booking_id FROM Bookings WHERE booking_id = ?", (booking_id,)
        ).fetchone()
        if row is None:
            _rollback(conn)
            return {"ok": False, "message": f"Booking {booking_id} does not exist."}

        conn.execute("DELETE FROM Bookings WHERE booking_id = ?", (booking_id,))
        conn.execute("COMMIT")
        return {"ok": True, "message": "Booking cancelled, seat is free again."}

    except sqlite3.Error as err:
        _rollback(conn)
        return {"ok": False, "message": f"Cancel failed, nothing changed ({err})."}
    finally:
        conn.close()
