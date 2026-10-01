from odoo import _, fields, models
from odoo.exceptions import ValidationError


class RoomBookingFindRoomWizard(models.TransientModel):
    _name = "room.booking.find.room.wizard"
    _description = "Find a Free Room"

    start = fields.Datetime(
        string="Start",
        required=True,
    )

    stop = fields.Datetime(
        string="Stop",
        required=True,
    )

    min_capacity = fields.Integer(
        string="Minimum Capacity",
        default=1,
    )

    available_room_ids = fields.Many2many(
        "room.booking.room",
        string="Available Rooms",
        readonly=True,
    )

    room_id = fields.Many2one(
        "room.booking.room",
        string="Selected Room",
    )

    def action_search_rooms(self):
        self.ensure_one()

        # Validate the time range
        if self.stop <= self.start:
            raise ValidationError(
                _("The stop time must be later than the start time.")
            )

        # Validate minimum capacity
        if self.min_capacity < 0:
            raise ValidationError(
                _("Minimum capacity cannot be negative.")
            )

        # Find active rooms with enough capacity
        rooms = self.env["room.booking.room"].search([
            ("active", "=", True),
            ("capacity", ">=", self.min_capacity),
        ])

        # Keep only rooms without a conflicting booking
        available_rooms = rooms.filtered(
            lambda room: not self.env["room.booking"].search([
                ("room_id", "=", room.id),
                ("start", "<", self.stop),
                ("stop", ">", self.start),
                ("state", "in", ("draft", "confirmed")),
            ], limit=1)
        )

        # Display the available rooms in the wizard
        self.available_room_ids = available_rooms

        # Clear any previous room selection
        self.room_id = False

        # Stay on the same wizard
        return {
            "type": "ir.actions.act_window",
            "name": _("Available Rooms"),
            "res_model": "room.booking.find.room.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def action_create_booking(self):
        self.ensure_one()

        # A room must be selected
        if not self.room_id:
            raise ValidationError(
                _("Please select a room.")
            )

        # Create the booking using the wizard values
        booking = self.env["room.booking"].create({
            "name": _("Room Booking"),
            "room_id": self.room_id.id,
            "organizer_id": self.env.user.id,
            "start": self.start,
            "stop": self.stop,
        })

        # Open the newly created booking
        return {
            "type": "ir.actions.act_window",
            "name": _("Booking"),
            "res_model": "room.booking",
            "view_mode": "form",
            "res_id": booking.id,
            "target": "current",
        }