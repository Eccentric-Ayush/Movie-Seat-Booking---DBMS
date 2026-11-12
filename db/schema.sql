
drop table if exists bookings;
drop table if exists shows;
drop table if exists seats;
drop table if exists users;
drop table if exists movies;


create table movies (
    movie_id integer primary key autoincrement,
    title text not null,
    duration_min integer,
    genre text
);



create table users (
    user_id integer primary key autoincrement,
    name text not null,
    email text not null unique
);


create table seats (
    seat_id integer primary key autoincrement,
    row_label text not null,
    seat_number integer not null,

    unique (row_label, seat_number)
);


create table shows (
    show_id integer primary key autoincrement,
    movie_id integer not null,
    show_date text not null,
    show_time text not null,

    foreign key (movie_id) references movies(movie_id)
);


create table bookings (
    booking_id integer primary key autoincrement,
    user_id integer not null,
    show_id integer not null,
    seat_id integer not null,
    booking_date text not null default current_timestamp,

    foreign key (user_id) references users(user_id),
    foreign key (show_id) references shows(show_id),
    foreign key (seat_id) references seats(seat_id),

    unique (show_id, seat_id)
);



