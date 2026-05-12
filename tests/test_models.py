"""Tests for domain models"""
import pytest
from datetime import datetime, timedelta
from app.models import Bus, Seat, Passenger, Booking, SeatStatus, BookingStatus


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_bus():
    return Bus(
        bus_id="B001",
        bus_number="KA-01-AB-1234",
        source="Bangalore",
        destination="Mumbai",
        departure_time=datetime(2026, 6, 1, 8, 0),
        arrival_time=datetime(2026, 6, 1, 20, 0),
        total_seats=10,
        fare_per_seat=850.0,
    )


@pytest.fixture
def valid_passenger():
    return Passenger(
        name="Ramesh Kumar",
        email="ramesh@example.com",
        phone="9876543210",
        age=32,
    )


# ── Seat Tests ──────────────────────────────────────────────────────────────────

class TestSeat:
    def test_seat_default_available(self):
        seat = Seat(seat_number="1")
        assert seat.is_available() is True

    def test_seat_booked_not_available(self):
        seat = Seat(seat_number="1", status=SeatStatus.BOOKED)
        assert seat.is_available() is False

    def test_seat_reserved_not_available(self):
        seat = Seat(seat_number="2", status=SeatStatus.RESERVED)
        assert seat.is_available() is False


# ── Bus Tests ───────────────────────────────────────────────────────────────────

class TestBus:
    def test_bus_creates_correct_number_of_seats(self, sample_bus):
        assert len(sample_bus.seats) == 10

    def test_all_seats_initially_available(self, sample_bus):
        assert sample_bus.available_seat_count() == 10

    def test_get_existing_seat(self, sample_bus):
        seat = sample_bus.get_seat("3")
        assert seat is not None
        assert seat.seat_number == "3"

    def test_get_nonexistent_seat_returns_none(self, sample_bus):
        assert sample_bus.get_seat("99") is None

    def test_duration_hours(self, sample_bus):
        assert sample_bus.duration_hours() == 12.0

    def test_available_seats_decreases_after_booking(self, sample_bus):
        sample_bus.seats[0].status = SeatStatus.BOOKED
        assert sample_bus.available_seat_count() == 9


# ── Passenger Validation Tests ──────────────────────────────────────────────────

class TestPassengerValidation:
    def test_valid_passenger_passes(self, valid_passenger):
        assert valid_passenger.validate() is True

    def test_short_name_raises(self):
        p = Passenger(name="A", email="a@b.com", phone="9876543210", age=25)
        with pytest.raises(ValueError, match="name"):
            p.validate()

    def test_invalid_email_raises(self):
        p = Passenger(name="Alice", email="not-an-email", phone="9876543210", age=25)
        with pytest.raises(ValueError, match="email"):
            p.validate()

    def test_short_phone_raises(self):
        p = Passenger(name="Alice", email="a@b.com", phone="12345", age=25)
        with pytest.raises(ValueError, match="Phone"):
            p.validate()

    def test_invalid_age_raises(self):
        p = Passenger(name="Alice", email="a@b.com", phone="9876543210", age=0)
        with pytest.raises(ValueError, match="Age"):
            p.validate()

    def test_age_too_high_raises(self):
        p = Passenger(name="Alice", email="a@b.com", phone="9876543210", age=200)
        with pytest.raises(ValueError, match="Age"):
            p.validate()


# ── Booking Tests ───────────────────────────────────────────────────────────────

class TestBooking:
    def test_booking_total_fare(self, sample_bus, valid_passenger):
        booking = Booking(bus=sample_bus, passenger=valid_passenger, seat_number="1")
        assert booking.total_fare == 850.0

    def test_booking_default_status_confirmed(self, sample_bus, valid_passenger):
        booking = Booking(bus=sample_bus, passenger=valid_passenger, seat_number="2")
        assert booking.status == BookingStatus.CONFIRMED

    def test_booking_id_generated(self, sample_bus, valid_passenger):
        booking = Booking(bus=sample_bus, passenger=valid_passenger, seat_number="3")
        assert booking.booking_id is not None
        assert len(booking.booking_id) > 0

    def test_cancel_booking_changes_status(self, sample_bus, valid_passenger):
        seat = sample_bus.get_seat("4")
        seat.status = SeatStatus.BOOKED
        booking = Booking(bus=sample_bus, passenger=valid_passenger, seat_number="4")
        booking.cancel()
        assert booking.status == BookingStatus.CANCELLED

    def test_cancel_booking_frees_seat(self, sample_bus, valid_passenger):
        seat = sample_bus.get_seat("5")
        seat.status = SeatStatus.BOOKED
        booking = Booking(bus=sample_bus, passenger=valid_passenger, seat_number="5")
        booking.cancel()
        assert seat.is_available() is True

    def test_double_cancel_raises(self, sample_bus, valid_passenger):
        seat = sample_bus.get_seat("6")
        seat.status = SeatStatus.BOOKED
        booking = Booking(bus=sample_bus, passenger=valid_passenger, seat_number="6")
        booking.cancel()
        with pytest.raises(ValueError, match="already cancelled"):
            booking.cancel()

    def test_booking_str_representation(self, sample_bus, valid_passenger):
        booking = Booking(bus=sample_bus, passenger=valid_passenger, seat_number="1")
        output = str(booking)
        assert "Ramesh Kumar" in output
        assert "Bangalore" in output
        assert "Mumbai" in output
