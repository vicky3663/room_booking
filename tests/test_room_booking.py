from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestRoomBooking(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.room = cls.env["room.booking.room"].create({
            "name": "Test Meeting Room",
        })

    def test_duration_compute(self):
        booking = self.env["room.booking"].create({
            "name": "Duration Compute Test",
            "room_id": self.room.id,
            "start": datetime(2026, 10, 1, 9, 0, 0),
            "stop": datetime(2026, 10, 1, 11, 30, 0),
        })

        self.assertEqual(booking.duration, 2.5)

    def test_duration_inverse(self):
        booking = self.env["room.booking"].create({
            "name": "Duration Inverse Test",
            "room_id": self.room.id,
            "start": datetime(2026, 10, 1, 9, 0, 0),
            "stop": datetime(2026, 10, 1, 10, 0, 0),
        })

        booking.duration = 3.0

        self.assertEqual(
            booking.stop,
            datetime(2026, 10, 1, 12, 0, 0),
        )

    def test_stop_must_be_after_start(self):
        with self.assertRaises(ValidationError):
            self.env["room.booking"].create({
                "name": "Invalid Booking",
                "room_id": self.room.id,
                "start": datetime(2026, 10, 1, 11, 0, 0),
                "stop": datetime(2026, 10, 1, 10, 0, 0),
            })

    def test_stop_cannot_equal_start(self):
        with self.assertRaises(ValidationError):
            self.env["room.booking"].create({
                "name": "Zero Duration Booking",
                "room_id": self.room.id,
                "start": datetime(2026, 10, 1, 10, 0, 0),
                "stop": datetime(2026, 10, 1, 10, 0, 0),
            })
    
    def test_start_cannot_be_in_the_past(self):
        with self.assertRaises(ValidationError):
            self.env["room.booking"].create({
                "name": "Past Booking",
                "room_id": self.room.id,
                "start": datetime(2020, 1, 1, 9, 0, 0),
                "stop": datetime(2020, 1, 1, 10, 0, 0),
            })

    def test_overlapping_booking_is_rejected(self):
        self.env["room.booking"].create({
            "name": "First Booking",
            "room_id": self.room.id,
            "start": datetime(2026, 10, 1, 9, 0, 0),
            "stop": datetime(2026, 10, 1, 11, 0, 0),
        })

        with self.assertRaises(ValidationError):
            self.env["room.booking"].create({
                "name": "Overlapping Booking",
                "room_id": self.room.id,
                "start": datetime(2026, 10, 1, 10, 0, 0),
                "stop": datetime(2026, 10, 1, 12, 0, 0),
            })

    def test_adjacent_bookings_are_allowed(self):
        self.env["room.booking"].create({
            "name": "First Booking",
            "room_id": self.room.id,
            "start": datetime(2026, 10, 1, 9, 0, 0),
            "stop": datetime(2026, 10, 1, 10, 0, 0),
        })

        booking = self.env["room.booking"].create({
            "name": "Second Booking",
            "room_id": self.room.id,
            "start": datetime(2026, 10, 1, 10, 0, 0),
            "stop": datetime(2026, 10, 1, 11, 0, 0),
        })

        self.assertEqual(booking.name, "Second Booking")

    def test_same_time_different_room_is_allowed(self):
        second_room = self.env["room.booking.room"].create({
            "name": "Second Test Room",
        })

        self.env["room.booking"].create({
            "name": "First Room Booking",
            "room_id": self.room.id,
            "start": datetime(2026, 10, 1, 9, 0, 0),
            "stop": datetime(2026, 10, 1, 11, 0, 0),
        })

        booking = self.env["room.booking"].create({
            "name": "Second Room Booking",
            "room_id": second_room.id,
            "start": datetime(2026, 10, 1, 9, 0, 0),
            "stop": datetime(2026, 10, 1, 11, 0, 0),
        })

        self.assertEqual(booking.room_id, second_room)