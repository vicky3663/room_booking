from datetime import datetime

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase


class TestRoomBooking(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.room = cls.env["room.booking.room"].create({
            "name": "Test Meeting Room",
        })

        cls.manager_group = cls.env.ref(
            "room_booking.group_room_booking_manager"
        )

        cls.user_a = cls.env["res.users"].create({
            "name": "Booking User A",
            "login": "booking_user_a",
            "email": "booking_user_a@example.com",
            "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
        })

        cls.user_b = cls.env["res.users"].create({
            "name": "Booking User B",
            "login": "booking_user_b",
            "email": "booking_user_b@example.com",
            "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
        })

        cls.manager = cls.env["res.users"].create({
            "name": "Booking Manager",
            "login": "booking_manager",
            "email": "booking_manager@example.com",
            "groups_id": [
                (6, 0, [
                    cls.env.ref("base.group_user").id,
                    cls.manager_group.id,
                ])
            ],
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

    def test_user_can_access_own_booking(self):
        booking = self.env["room.booking"].with_user(self.user_a).create({
            "name": "User A Booking",
            "room_id": self.room.id,
            "start": datetime(2026, 12, 1, 9, 0, 0),
            "stop": datetime(2026, 12, 1, 10, 0, 0),
        })

        self.assertEqual(
            booking.with_user(self.user_a).name,
            "User A Booking",
        )

    def test_user_cannot_access_another_users_booking(self):
        booking = self.env["room.booking"].with_user(self.user_a).create({
            "name": "User A Private Booking",
            "room_id": self.room.id,
            "start": datetime(2026, 12, 2, 9, 0, 0),
            "stop": datetime(2026, 12, 2, 10, 0, 0),
        })

        with self.assertRaises(AccessError):
            booking.with_user(self.user_b).write({
                "name": "User B Trying To Edit",
            })

    def test_manager_can_access_another_users_booking(self):
        booking = self.env["room.booking"].with_user(self.user_a).create({
            "name": "User A Manager Test",
            "room_id": self.room.id,
            "start": datetime(2026, 12, 3, 9, 0, 0),
            "stop": datetime(2026, 12, 3, 10, 0, 0),
        })

        booking.with_user(self.manager).write({
            "name": "Updated By Manager",
        })

        self.assertEqual(
            booking.with_user(self.manager).name,
            "Updated By Manager",
        )

    def test_normal_user_cannot_modify_room(self):
        with self.assertRaises(AccessError):
            self.room.with_user(self.user_a).write({
                "name": "Modified By Normal User",
            })

    def test_manager_can_modify_room(self):
        self.room.with_user(self.manager).write({
            "name": "Modified By Manager",
        })

        self.assertEqual(
            self.room.with_user(self.manager).name,
            "Modified By Manager",
        )