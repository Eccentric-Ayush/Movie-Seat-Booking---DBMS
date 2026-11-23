"""Golden: terminal menu, show picker and seat map.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.booking import book_seat, cancel_booking  # noqa: E402
from src.queries import get_seat_map, get_user_bookings, list_shows, list_users  # noqa: E402

MENU = """
==== Movie Seat Booking ====
1. List shows
2. Show seat map
3. Book a seat
4. Cancel a booking
5. My bookings
0. Exit
"""


def ask_int(prompt):
    text = input(prompt).strip()
    if not text.lstrip("-").isdigit():
        print("Please type a number.")
        return None
    return int(text)


def print_shows():
    shows = list_shows()
    print(f"\n{'ID':<4}{'Movie':<18}{'Time':<18}{'Free seats'}")
    for s in shows:
        print(f"{s['show_id']:<4}{s['title']:<18}{s['show_time']:<18}{s['free_seats']}")


def print_seat_map(show_id):
    seats = get_seat_map(show_id)
    if not seats:
        print("No seats found.")
        return seats
    numbers = sorted({s["number"] for s in seats})
    print("\n        SCREEN")
    print("    " + " ".join(str(n) for n in numbers))
    for row in sorted({s["row"] for s in seats}):
        marks = ["X" if s["booked"] else "O" for s in seats if s["row"] == row]
        print(f"{row}   " + " ".join(marks))
    print("O = free, X = booked")
    return seats


def print_bookings(user_id):
    bookings = get_user_bookings(user_id)
    if not bookings:
        print("No bookings for this user.")
        return
    print(f"\n{'Booking':<9}{'Movie':<18}{'Time':<18}{'Seat'}")
    for b in bookings:
        print(f"{b['booking_id']:<9}{b['movie']:<18}{b['show_time']:<18}{b['seat']}")


def pick_user():
    users = list_users()
    print("\nUsers: " + ", ".join(f"{u['user_id']}={u['name']}" for u in users))
    return ask_int("Your user id: ")


def find_seat_id(seats, label):
    """Turn a label such as 'B3' into a seat_id."""
    label = label.strip().upper()
    for s in seats:
        if f"{s['row']}{s['number']}" == label:
            return s["seat_id"]
    return None


def do_book():
    user_id = pick_user()
    if user_id is None:
        return
    print_shows()
    show_id = ask_int("Show id: ")
    if show_id is None:
        return
    seats = print_seat_map(show_id)
    if not seats:
        return
    seat_label = input("Seat (for example B3): ").strip().upper()
    seat_id = find_seat_id(seats, seat_label)

    if seat_id is None:
       print("That seat does not exist.")
       return

    selected_seat = next(s for s in seats if s["seat_id"] == seat_id)

    if selected_seat["booked"]:
        print("Sorry, this seat is already booked.")
        return

    print(book_seat(user_id, show_id, seat_id)["message"])



def do_cancel():
    user_id = pick_user()
    if user_id is None:
        return
    print_bookings(user_id)
    booking_id = ask_int("Booking id to cancel: ")
    if booking_id is None:
        return
    print(cancel_booking(booking_id)["message"])


def main():
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        if choice == "1":
            print_shows()
        elif choice == "2":
            print_shows()
            show_id = ask_int("Show id: ")
            if show_id is not None:
                print_seat_map(show_id)
        elif choice == "3":
            do_book()
        elif choice == "4":
            do_cancel()
        elif choice == "5":
            user_id = pick_user()
            if user_id is not None:
                print_bookings(user_id)
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    main()
