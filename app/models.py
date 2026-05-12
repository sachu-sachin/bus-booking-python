"""
Bus Booking System - Domain Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid


class SeatStatus(Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    RESERVED = "reserved"


class BookingStatus(Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    PENDING = "pending"


@dataclass
class Seat:
    seat_number: str
    status: SeatStatus = SeatStatus.AVAILABLE

    def is_available(self) -> bool:
        return self.status == SeatStatus.AVAILABLE


@dataclass
class Bus:
    bus_id: str
    bus_number: str
    source: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    total_seats: int
    fare_per_seat: float
    seats: List[Seat] = field(default_factory=list)

    def __post_init__(self):
        if not self.seats:
            self.seats = [
                Seat(seat_number=f"{i+1}") for i in range(self.total_seats)
            ]

    def available_seats(self) -> List[Seat]:
        return [s for s in self.seats if s.is_available()]

    def available_seat_count(self) -> int:
        return len(self.available_seats())

    def get_seat(self, seat_number: str) -> Optional[Seat]:
        for seat in self.seats:
            if seat.seat_number == seat_number:
                return seat
        return None

    def duration_hours(self) -> float:
        delta = self.arrival_time - self.departure_time
        return round(delta.total_seconds() / 3600, 2)


@dataclass
class Passenger:
    name: str
    email: str
    phone: str
    age: int

    def validate(self) -> bool:
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Passenger name must be at least 2 characters.")
        if "@" not in self.email:
            raise ValueError("Invalid email address.")
        if not self.phone.isdigit() or len(self.phone) < 10:
            raise ValueError("Phone number must be at least 10 digits.")
        if not (1 <= self.age <= 120):
            raise ValueError("Age must be between 1 and 120.")
        return True


@dataclass
class Booking:
    bus: Bus
    passenger: Passenger
    seat_number: str
    booking_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    status: BookingStatus = BookingStatus.CONFIRMED
    booked_at: datetime = field(default_factory=datetime.now)

    @property
    def total_fare(self) -> float:
        return self.bus.fare_per_seat

    def cancel(self) -> None:
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Booking is already cancelled.")
        self.status = BookingStatus.CANCELLED
        seat = self.bus.get_seat(self.seat_number)
        if seat:
            seat.status = SeatStatus.AVAILABLE

    def __str__(self) -> str:
        return (
            f"Booking ID : {self.booking_id}\n"
            f"Passenger  : {self.passenger.name}\n"
            f"Bus        : {self.bus.bus_number}\n"
            f"Route      : {self.bus.source} → {self.bus.destination}\n"
            f"Seat       : {self.seat_number}\n"
            f"Fare       : ₹{self.total_fare:.2f}\n"
            f"Status     : {self.status.value.upper()}"
        )
