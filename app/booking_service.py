"""
Bus Booking System - Service Layer
"""

from typing import Dict, List, Optional
from .models import Bus, Booking, Passenger, SeatStatus, BookingStatus


class BusBookingService:
    """Core service to manage bus fleet and reservations."""

    def __init__(self):
        self._buses: Dict[str, Bus] = {}
        self._bookings: Dict[str, Booking] = {}

    # ── Bus Management ────────────────────────────────────────────────────────

    def add_bus(self, bus: Bus) -> None:
        """Register a bus in the system."""
        if bus.bus_id in self._buses:
            raise ValueError(f"Bus with ID '{bus.bus_id}' already exists.")
        self._buses[bus.bus_id] = bus

    def get_bus(self, bus_id: str) -> Optional[Bus]:
        return self._buses.get(bus_id)

    def list_buses(self) -> List[Bus]:
        return list(self._buses.values())

    # ── Search ─────────────────────────────────────────────────────────────────

    def search_buses(self, source: str, destination: str) -> List[Bus]:
        """Find buses matching origin and destination (case-insensitive)."""
        return [
            bus
            for bus in self._buses.values()
            if bus.source.lower() == source.lower()
            and bus.destination.lower() == destination.lower()
            and bus.available_seat_count() > 0
        ]

    # ── Booking ────────────────────────────────────────────────────────────────

    def book_seat(self, bus_id: str, passenger: Passenger, seat_number: str) -> Booking:
        """Book a specific seat on a bus for a passenger."""
        bus = self._buses.get(bus_id)
        if not bus:
            raise ValueError(f"Bus '{bus_id}' not found.")

        passenger.validate()

        seat = bus.get_seat(seat_number)
        if not seat:
            raise ValueError(f"Seat '{seat_number}' does not exist on bus '{bus_id}'.")
        if not seat.is_available():
            raise ValueError(f"Seat '{seat_number}' is not available.")

        seat.status = SeatStatus.BOOKED
        booking = Booking(bus=bus, passenger=passenger, seat_number=seat_number)
        self._bookings[booking.booking_id] = booking
        return booking

    # ── Cancellation ───────────────────────────────────────────────────────────

    def cancel_booking(self, booking_id: str) -> Booking:
        """Cancel an existing booking and free up the seat."""
        booking = self._bookings.get(booking_id)
        if not booking:
            raise ValueError(f"Booking '{booking_id}' not found.")
        booking.cancel()
        return booking

    # ── Retrieval ──────────────────────────────────────────────────────────────

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        return self._bookings.get(booking_id)

    def list_bookings(self, status: Optional[BookingStatus] = None) -> List[Booking]:
        bookings = list(self._bookings.values())
        if status:
            bookings = [b for b in bookings if b.status == status]
        return bookings

    def get_passenger_bookings(self, email: str) -> List[Booking]:
        return [b for b in self._bookings.values() if b.passenger.email == email]
