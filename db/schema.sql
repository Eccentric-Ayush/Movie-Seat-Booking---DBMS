-- MV1 (Ananya): five tables, primary keys, foreign keys, UNIQUE(show_id, seat_id)
PRAGMA foreign_keys = ON;

CREATE TABLE Movies (
    movie_id     INTEGER PRIMARY KEY,
    title        TEXT    NOT NULL,
    duration_min INTEGER NOT NULL CHECK (duration_min > 0)
);

CREATE TABLE Shows (
    show_id   INTEGER PRIMARY KEY,
    movie_id  INTEGER NOT NULL REFERENCES Movies(movie_id),
    show_time TEXT    NOT NULL            -- 'YYYY-MM-DD HH:MM'
);

-- One hall: the same seat grid is used by every show.
CREATE TABLE Seats (
    seat_id     INTEGER PRIMARY KEY,
    row_label   TEXT    NOT NULL,         -- 'A', 'B', ...
    seat_number INTEGER NOT NULL,         -- 1, 2, ...
    UNIQUE (row_label, seat_number)
);

CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    email   TEXT NOT NULL UNIQUE
);

CREATE TABLE Bookings (
    booking_id INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES Users(user_id),
    show_id    INTEGER NOT NULL REFERENCES Shows(show_id),
    seat_id    INTEGER NOT NULL REFERENCES Seats(seat_id),
    booked_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- M2: the same seat can never be saved twice for the same show
    UNIQUE (show_id, seat_id)
);
