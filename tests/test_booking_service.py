"""Tests for booking service"""

import pytest
from datetime import datetime
from app.models import Bus, Passenger, BookingStatus, SeatStatus
from app.booking_service import BusBookingService

# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture
def service():
    return BusBookingService()


@pytest.fixture
def bus_blr_mum():
    return Bus(
        bus_id="B001",
        bus_number="KA-01-AB-1234",
        source="Bangalore",
        destination="Mumbai",
        departure_time=datetime(2026, 6, 1, 8, 0),
        arrival_time=datetime(2026, 6, 1, 20, 0),
        total_seats=5,
        fare_per_seat=850.0,
    )


@pytest.fixture
def bus_del_mum():
    return Bus(
        bus_id="B002",
        bus_number="DL-02-CD-5678",
        source="Delhi",
        destination="Mumbai",
        departure_time=datetime(2026, 6, 2, 6, 0),
        arrival_time=datetime(2026, 6, 2, 22, 0),
        total_seats=3,
        fare_per_seat=1200.0,
    )


@pytest.fixture
def passenger():
    return Passenger(
        name="Sita Devi",
        email="sita@example.com",
        phone="8765432109",
        age=27,
    )


@pytest.fixture
def loaded_service(service, bus_blr_mum):
    service.add_bus(bus_blr_mum)
    return service


# ── Bus Management Tests ────────────────────────────────────────────────────────


class TestBusManagement:
    def test_add_bus_success(self, service, bus_blr_mum):
        service.add_bus(bus_blr_mum)
        assert service.get_bus("B001") is not None

    def test_add_duplicate_bus_raises(self, loaded_service, bus_blr_mum):
        with pytest.raises(ValueError, match="already exists"):
            loaded_service.add_bus(bus_blr_mum)

    def test_list_buses_returns_all(self, service, bus_blr_mum, bus_del_mum):
        service.add_bus(bus_blr_mum)
        service.add_bus(bus_del_mum)
        assert len(service.list_buses()) == 2

    def test_get_nonexistent_bus_returns_none(self, service):
        assert service.get_bus("INVALID") is None


# ── Search Tests ────────────────────────────────────────────────────────────────


class TestSearch:
    def test_search_finds_matching_bus(self, service, bus_blr_mum, bus_del_mum):
        service.add_bus(bus_blr_mum)
        service.add_bus(bus_del_mum)
        results = service.search_buses("Bangalore", "Mumbai")
        assert len(results) == 1
        assert results[0].bus_id == "B001"

    def test_search_is_case_insensitive(self, loaded_service):
        results = loaded_service.search_buses("bangalore", "mumbai")
        assert len(results) == 1

    def test_search_returns_empty_for_no_match(self, loaded_service):
        results = loaded_service.search_buses("Chennai", "Pune")
        assert results == []

    def test_search_excludes_fully_booked_bus(self, loaded_service, passenger):
        # Book all 5 seats
        for i in range(1, 6):
            p = Passenger(
                name=f"Passenger{i}",
                email=f"p{i}@test.com",
                phone="9999999999",
                age=30,
            )
            loaded_service.book_seat("B001", p, str(i))
        results = loaded_service.search_buses("Bangalore", "Mumbai")
        assert results == []


# ── Booking Tests ───────────────────────────────────────────────────────────────


class TestBooking:
    def test_successful_booking(self, loaded_service, passenger):
        booking = loaded_service.book_seat("B001", passenger, "1")
        assert booking.booking_id is not None
        assert booking.status == BookingStatus.CONFIRMED

    def test_seat_marked_booked_after_reservation(self, loaded_service, passenger):
        loaded_service.book_seat("B001", passenger, "2")
        seat = loaded_service.get_bus("B001").get_seat("2")
        assert seat.status == SeatStatus.BOOKED

    def test_booking_invalid_bus_raises(self, service, passenger):
        with pytest.raises(ValueError, match="not found"):
            service.book_seat("GHOST", passenger, "1")

    def test_booking_invalid_seat_raises(self, loaded_service, passenger):
        with pytest.raises(ValueError, match="does not exist"):
            loaded_service.book_seat("B001", passenger, "99")

    def test_booking_already_taken_seat_raises(self, loaded_service, passenger):
        loaded_service.book_seat("B001", passenger, "3")
        p2 = Passenger(name="Jane Doe", email="jane@test.com", phone="9000000000", age=22)
        with pytest.raises(ValueError, match="not available"):
            loaded_service.book_seat("B001", p2, "3")

    def test_get_booking_returns_correct(self, loaded_service, passenger):
        booking = loaded_service.book_seat("B001", passenger, "1")
        fetched = loaded_service.get_booking(booking.booking_id)
        assert fetched is booking

    def test_get_nonexistent_booking_returns_none(self, service):
        assert service.get_booking("ZZZZZZZZ") is None


# ── Cancellation Tests ──────────────────────────────────────────────────────────


class TestCancellation:
    def test_cancel_booking_changes_status(self, loaded_service, passenger):
        booking = loaded_service.book_seat("B001", passenger, "1")
        cancelled = loaded_service.cancel_booking(booking.booking_id)
        assert cancelled.status == BookingStatus.CANCELLED

    def test_cancel_frees_seat(self, loaded_service, passenger):
        booking = loaded_service.book_seat("B001", passenger, "1")
        loaded_service.cancel_booking(booking.booking_id)
        seat = loaded_service.get_bus("B001").get_seat("1")
        assert seat.is_available() is True

    def test_cancel_nonexistent_booking_raises(self, service):
        with pytest.raises(ValueError, match="not found"):
            service.cancel_booking("INVALID123")

    def test_seat_can_be_rebooked_after_cancellation(self, loaded_service, passenger):
        booking = loaded_service.book_seat("B001", passenger, "1")
        loaded_service.cancel_booking(booking.booking_id)
        p2 = Passenger(name="Arjun M", email="arjun@test.com", phone="8888888888", age=40)
        new_booking = loaded_service.book_seat("B001", p2, "1")
        assert new_booking.status == BookingStatus.CONFIRMED


# ── Passenger Bookings ──────────────────────────────────────────────────────────


class TestPassengerBookings:
    def test_get_passenger_bookings(self, service, bus_blr_mum, bus_del_mum, passenger):
        service.add_bus(bus_blr_mum)
        service.add_bus(bus_del_mum)
        service.book_seat("B001", passenger, "1")
        service.book_seat("B002", passenger, "1")
        bookings = service.get_passenger_bookings("sita@example.com")
        assert len(bookings) == 2

    def test_passenger_no_bookings_returns_empty(self, loaded_service):
        assert loaded_service.get_passenger_bookings("nobody@example.com") == []

    def test_list_bookings_by_status(self, loaded_service, passenger):
        booking = loaded_service.book_seat("B001", passenger, "1")
        loaded_service.cancel_booking(booking.booking_id)
        p2 = Passenger(name="Bob", email="bob@test.com", phone="7777777777", age=30)
        loaded_service.book_seat("B001", p2, "2")

        confirmed = loaded_service.list_bookings(status=BookingStatus.CONFIRMED)
        cancelled = loaded_service.list_bookings(status=BookingStatus.CANCELLED)
        assert len(confirmed) == 1
        assert len(cancelled) == 1
