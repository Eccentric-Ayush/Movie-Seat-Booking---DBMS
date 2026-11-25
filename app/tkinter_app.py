"""Minimal Tkinter interface for movie seat booking."""
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.seed import seed  # noqa: E402
from src.booking import book_seat, cancel_booking  # noqa: E402
from src.db import get_db_path  # noqa: E402
from src.queries import get_seat_map, get_user_bookings, list_shows, list_users  # noqa: E402


class MovieBookingApp:
    def __init__(self, root):
        self.root = root
        root.title("Movie Seat Booking")
        root.resizable(False, False)
        self.users = {f"{u['user_id']} - {u['name']}": u["user_id"] for u in list_users()}
        self.shows = {
            f"{s['show_id']} - {s['title']} - {s['show_time']}": s["show_id"]
            for s in list_shows()
        }
        self.selected_seat = None

        self.user = self.combo("User", list(self.users), 32, 0)
        self.show = self.combo("Show", list(self.shows), 42, 1)
        self.seat_frame = ttk.Frame(root)
        self.seat_frame.grid(row=2, column=0, columnspan=2, padx=8, pady=8)

        actions = ttk.Frame(root)
        actions.grid(row=3, column=0, columnspan=2)
        ttk.Button(actions, text="Book seat", command=self.book).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Refresh", command=self.refresh).grid(row=0, column=1, padx=4)

        ttk.Label(root, text="My bookings").grid(row=4, column=0, columnspan=2, sticky="w", padx=8)
        self.bookings = tk.Listbox(root, width=74, height=6)
        self.bookings.grid(row=5, column=0, columnspan=2, padx=8)
        ttk.Button(root, text="Cancel booking", command=self.cancel).grid(
            row=6, column=0, columnspan=2, pady=6
        )
        self.status = ttk.Label(root)
        self.status.grid(row=7, column=0, columnspan=2, pady=6)

        self.user.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        self.show.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        self.refresh()

    def combo(self, label, values, width, column):
        ttk.Label(self.root, text=label).grid(row=0, column=column, padx=8, sticky="w")
        box = ttk.Combobox(self.root, values=values, state="readonly", width=width)
        box.grid(row=1, column=column, padx=8, sticky="w")
        if values:
            box.current(0)
        return box

    def refresh(self):
        for widget in self.seat_frame.winfo_children():
            widget.destroy()
        self.selected_seat = None

        show_id = self.shows.get(self.show.get())
        if show_id is not None:
            seats = get_seat_map(show_id)
            ttk.Label(self.seat_frame, text="SCREEN").grid(row=0, column=0, columnspan=9)
            for number in range(1, 9):
                ttk.Label(self.seat_frame, text=str(number)).grid(row=1, column=number)
            for row, letter in enumerate("ABCDE", start=2):
                ttk.Label(self.seat_frame, text=letter).grid(row=row, column=0)
                for seat in (s for s in seats if s["row"] == letter):
                    tk.Button(
                        self.seat_frame,
                        text=f"{letter}{seat['number']}",
                        width=5,
                        bg="#e58b8b" if seat["booked"] else "#90c890",
                        state="disabled" if seat["booked"] else "normal",
                        command=lambda sid=seat["seat_id"]: self.select_seat(sid),
                    ).grid(row=row, column=seat["number"], padx=2, pady=2)

        self.status.config(text="")
        self.refresh_bookings()

    def select_seat(self, seat_id):
        seat = next(
            (s for s in get_seat_map(self.shows[self.show.get()]) if s["seat_id"] == seat_id),
            None,
        )
        if seat is None:
            return
        if seat["booked"]:
            self.selected_seat = None
            self.status.config(text=f"Seat {seat['row']}{seat['number']} is already booked.")
            return
        self.selected_seat = seat_id
        self.status.config(text=f"Selected seat: {seat['row']}{seat['number']}")

    def book(self):
        if self.selected_seat is None:
            messagebox.showinfo("Movie Seat Booking", "Select a seat first.")
            return
        result = book_seat(
            self.users.get(self.user.get()),
            self.shows.get(self.show.get()),
            self.selected_seat,
        )
        self.refresh()
        self.status.config(text=result["message"])

    def refresh_bookings(self):
        self.bookings.delete(0, tk.END)
        user_id = self.users.get(self.user.get())
        if user_id is not None:
            for b in get_user_bookings(user_id):
                self.bookings.insert(
                    tk.END, f"{b['booking_id']} - {b['movie']} - {b['show_time']} - Seat {b['seat']}"
                )

    def cancel(self):
        selected = self.bookings.curselection()
        if not selected:
            messagebox.showinfo("Movie Seat Booking", "Select a booking first.")
            return
        booking_id = int(self.bookings.get(selected[0]).split(" - ", 1)[0])
        result = cancel_booking(booking_id)
        self.refresh()
        self.status.config(text=result["message"])


if __name__ == "__main__":
    if not os.path.exists(get_db_path()):
        seed()
    window = tk.Tk()
    MovieBookingApp(window)
    window.mainloop()
