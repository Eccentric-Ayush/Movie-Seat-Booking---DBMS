
import sqlite3
import os


def main():

    # 1. get folder path
    base_dir = os.path.dirname(__file__)

    # 2. create file paths
    schema_path = os.path.join(base_dir, "schema.sql")
    db_path = os.path.join(base_dir, "movie.db")

    # 3. connect to database
    conn = sqlite3.connect(db_path)

    # enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    cur = conn.cursor()

    # 4. read and execute schema
    with open(schema_path, "r") as file:
        sql = file.read()

    conn.executescript(sql)

    # 5. insert movies
    movies = [
        ("3 Idiots", 170, "Comedy"),
        ("Dangal", 161, "Drama"),
        ("Chhichhore", 143, "Comedy")
    ]

    cur.executemany(
        "INSERT INTO movies (title, duration_min, genre) VALUES (?, ?, ?)",
        movies
    )

    # 6. insert users
    users = [
        ("Ananya", "ananya@gmail.com"),
        ("Rahul", "rahul@gmail.com"),
        ("Priya", "priya@gmail.com"),
        ("Aman", "aman@gmail.com"),
        ("Sneha", "sneha@gmail.com")
    ]

    cur.executemany(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        users
    )

    # 7. insert shows
    shows = [
        (1, "2026-11-13", "10:00"),
        (1, "2026-11-13", "18:00"),
        (2, "2026-11-14", "12:00"),
        (2, "2026-11-14", "19:00"),
        (3, "2026-11-15", "15:00")
    ]

    cur.executemany(
        "INSERT INTO shows (movie_id, show_date, show_time) VALUES (?, ?, ?)",
        shows
    )

    # 8. insert 40 seats
    seats = []

    for row in "ABCDE":
        for num in range(1, 9):
            seats.append((row, num))

    cur.executemany(
        "INSERT INTO seats (row_label, seat_number) VALUES (?, ?)",
        seats
    )

    # 9. finish
    conn.commit()

    print("Database ready!")
    print("3 movies inserted")
    print("5 users inserted")
    print("5 shows inserted")
    print("40 seats inserted")

    conn.close()


if __name__ == "__main__":
    main()
