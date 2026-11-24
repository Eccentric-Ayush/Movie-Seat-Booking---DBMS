"""MV5 (Kanhaiya): read-only queries used by the menu."""
from src.db import get_connection


def list_shows():
    """Every show with its movie and how many seats are still free."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT s.show_id,
                   m.title,
                   s.show_time,
                   m.duration_min,
                   (SELECT COUNT(*) FROM Seats)
                     - (SELECT COUNT(*) FROM Bookings b WHERE b.show_id = s.show_id)
                     AS free_seats
            FROM Shows s
            JOIN Movies m ON m.movie_id = s.movie_id
            ORDER BY s.show_time, s.show_id
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_seat_map(show_id):
    """[{'seat_id', 'row', 'number', 'booked'}] for one show."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT st.seat_id,
                   st.row_label   AS row,
                   st.seat_number AS number,
                   (b.booking_id IS NOT NULL) AS booked
            FROM Seats st
            LEFT JOIN Bookings b
                   ON b.seat_id = st.seat_id AND b.show_id = ?
            ORDER BY st.row_label, st.seat_number
            """,
            (show_id,),
        ).fetchall()
        return [
            {"seat_id": r["seat_id"], "row": r["row"], "number": r["number"],
             "booked": bool(r["booked"])}
            for r in rows
        ]
    finally:
        conn.close()


def get_user_bookings(user_id):
    """One query: a user's bookings with movie, time and seat."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT b.booking_id,
                   m.title                              AS movie,
                   s.show_time,
                   st.row_label || st.seat_number       AS seat
            FROM Bookings b
            JOIN Shows  s  ON s.show_id  = b.show_id
            JOIN Movies m  ON m.movie_id = s.movie_id
            JOIN Seats  st ON st.seat_id = b.seat_id
            WHERE b.user_id = ?
            ORDER BY s.show_time, st.row_label, st.seat_number
            """,
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_users():
    """Small helper so the menu can show who can log in."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT user_id, name FROM Users ORDER BY user_id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
