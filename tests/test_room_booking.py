from datetime import datetime, timedelta

from odoo import fields
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


    def test_configuration_menu_is_manager_only(self):
        menu = self.env.ref(
            "room_booking.menu_room_booking_configuration"
        )

        self.assertIn(self.manager_group, menu.groups_id)
        self.assertNotIn(
            self.env.ref("base.group_user"),
            menu.groups_id,
        )
    def test_send_reminder_sets_reminder_sent(self):
        booking = self.env["room.booking"].create({
            "name": "Reminder Test",
            "room_id": self.room.id,
            "start": datetime(2026, 12, 10, 9, 0, 0),
            "stop": datetime(2026, 12, 10, 10, 0, 0),
        })

        self.assertFalse(booking.reminder_sent)

        booking.action_send_reminder()

        self.assertTrue(booking.reminder_sent)

    def test_send_reminder_does_not_send_twice(self):
        booking = self.env["room.booking"].create({
            "name": "Reminder Once Test",
            "room_id": self.room.id,
            "start": datetime(2026, 12, 11, 9, 0, 0),
            "stop": datetime(2026, 12, 11, 10, 0, 0),
        })

        booking.action_send_reminder()

        self.assertTrue(booking.reminder_sent)

        booking.action_send_reminder()

        self.assertTrue(booking.reminder_sent)

    def test_cron_sends_reminders_for_upcoming_bookings(self):
        now = fields.Datetime.now()

        booking_to_remind = self.env["room.booking"].create({
            "name": "Upcoming Reminder",
            "room_id": self.room.id,
            "start": now + timedelta(hours=2),
            "stop": now + timedelta(hours=3),
        })

        booking_outside_window = self.env["room.booking"].create({
            "name": "Far Future Booking",
            "room_id": self.room.id,
            "start": now + timedelta(hours=48),
            "stop": now + timedelta(hours=49),
        })

        booking_already_sent = self.env["room.booking"].create({
            "name": "Already Reminded",
            "room_id": self.room.id,
            "start": now + timedelta(hours=3),
            "stop": now + timedelta(hours=4),
            "reminder_sent": True,
        })

        self.env["room.booking"]._cron_send_booking_reminders()

        self.assertTrue(booking_to_remind.reminder_sent)
        self.assertFalse(booking_outside_window.reminder_sent)
        self.assertTrue(booking_already_sent.reminder_sent)

    def test_cron_cancels_stale_draft_bookings(self):
        now = fields.Datetime.now()

        stale_draft = self.env["room.booking"].create({
            "name": "Stale Draft",
            "room_id": self.room.id,
            "start": now + timedelta(hours=2),
            "stop": now + timedelta(hours=3),
        })

        future_draft = self.env["room.booking"].create({
            "name": "Future Draft",
            "room_id": self.room.id,
            "start": now + timedelta(hours=4),
            "stop": now + timedelta(hours=5),
        })

        confirmed_past_booking = self.env["room.booking"].create({
            "name": "Past Confirmed Booking",
            "room_id": self.room.id,
            "start": now + timedelta(hours=6),
            "stop": now + timedelta(hours=7),
            "state": "confirmed",
        })

        # Move two bookings into the past directly in SQL.
        # This bypasses the FR-6 ORM constraint so the cron
        # can be tested with genuinely stale bookings.
        stale_start = now - timedelta(hours=2)
        stale_stop = now - timedelta(hours=1)

        confirmed_start = now - timedelta(hours=4)
        confirmed_stop = now - timedelta(hours=3)

        self.env.cr.execute(
            """
            UPDATE room_booking
            SET start = %s, stop = %s
            WHERE id = %s
            """,
            (stale_start, stale_stop, stale_draft.id),
        )

        self.env.cr.execute(
            """
            UPDATE room_booking
            SET start = %s, stop = %s
            WHERE id = %s
            """,
            (confirmed_start, confirmed_stop, confirmed_past_booking.id),
        )

        stale_draft.invalidate_recordset(["start", "stop"])
        confirmed_past_booking.invalidate_recordset(["start", "stop"])

        self.env["room.booking"]._cron_cancel_stale_draft_bookings()

        self.assertEqual(stale_draft.state, "cancelled")
        self.assertEqual(future_draft.state, "draft")
        self.assertEqual(confirmed_past_booking.state, "confirmed")