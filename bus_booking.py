# Simple Bus Booking System

buses = [
    {"id": 1, "name": "Express A", "from": "Bangalore", "to": "Mumbai", "seats": 5, "fare": 500},
    {"id": 2, "name": "Express B", "from": "Delhi", "to": "Pune", "seats": 3, "fare": 700},
]

bookings = []


def search_buses(from_city, to_city):
    return [b for b in buses if b["from"] == from_city and b["to"] == to_city and b["seats"] > 0]


def book_seat(bus_id, passenger_name):
    for bus in buses:
        if bus["id"] == bus_id:
            if bus["seats"] == 0:
                return "No seats available"
            bus["seats"] -= 1
            booking = {"bus_id": bus_id, "passenger": passenger_name, "fare": bus["fare"]}
            bookings.append(booking)
            return f"Booking confirmed for {passenger_name} on {bus['name']}. Fare: Rs.{bus['fare']}"
    return "Bus not found"


def cancel_booking(bus_id, passenger_name):
    for booking in bookings:
        if booking["bus_id"] == bus_id and booking["passenger"] == passenger_name:
            bookings.remove(booking)
            for bus in buses:
                if bus["id"] == bus_id:
                    bus["seats"] += 1
            return f"Booking cancelled for {passenger_name}"
    return "Booking not found"


if __name__ == "__main__":
    print("=== Bus Booking System ===\n")

    results = search_buses("Bangalore", "Mumbai")
    print("Buses from Bangalore to Mumbai:")
    for b in results:
        print(f"  [{b['id']}] {b['name']} | Seats: {b['seats']} | Fare: Rs.{b['fare']}")

    print()
    print(book_seat(1, "Alice"))
    print(book_seat(1, "Bob"))
    print(book_seat(2, "Charlie"))

    print()
    print("After booking:")
    for b in buses:
        print(f"  {b['name']}: {b['seats']} seats left")

    print()
    print(cancel_booking(1, "Alice"))
    print("After cancellation:", f"Bus 1 has {buses[0]['seats']} seats")
