import pytest
import bus_booking


@pytest.fixture(autouse=True)
def reset():
    # Reset state before each test
    bus_booking.buses = [
        {"id": 1, "name": "Express A", "from": "Bangalore", "to": "Mumbai", "seats": 5, "fare": 500},
        {"id": 2, "name": "Express B", "from": "Delhi", "to": "Pune", "seats": 3, "fare": 700},
    ]
    bus_booking.bookings = []


def test_search_buses_found():
    results = bus_booking.search_buses("Bangalore", "Mumbai")
    assert len(results) == 1
    assert results[0]["name"] == "Express A"


def test_search_buses_not_found():
    results = bus_booking.search_buses("Chennai", "Hyderabad")
    assert results == []


def test_book_seat_success():
    msg = bus_booking.book_seat(1, "Alice")
    assert "confirmed" in msg
    assert bus_booking.buses[0]["seats"] == 4


def test_book_seat_bus_not_found():
    msg = bus_booking.book_seat(99, "Alice")
    assert msg == "Bus not found"


def test_book_seat_no_seats():
    bus_booking.buses[0]["seats"] = 0
    msg = bus_booking.book_seat(1, "Alice")
    assert msg == "No seats available"


def test_cancel_booking_success():
    bus_booking.book_seat(1, "Alice")
    msg = bus_booking.cancel_booking(1, "Alice")
    assert "cancelled" in msg
    assert bus_booking.buses[0]["seats"] == 5


def test_cancel_booking_not_found():
    msg = bus_booking.cancel_booking(1, "Nobody")
    assert msg == "Booking not found"
