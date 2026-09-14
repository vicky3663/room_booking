from odoo import fields, models


class RoomBooking(models.Model):
    _name = "room.booking"
    _description = "Room Booking"

    name = fields.Char(
        string="Subject",
        required=True,
    )

    room_id = fields.Many2one(
        "room.booking.room",
        string="Room",
        required=True,
    )

    organizer_id = fields.Many2one(
        "res.users",
        string="Organizer",
        required=True,
        default=lambda self: self.env.user,
    )

    attendee_ids = fields.Many2many(
        "res.partner",
        string="Attendees",
    )

    start = fields.Datetime(
        string="Start",
        required=True,
    )

    stop = fields.Datetime(
        string="Stop",
        required=True,
    )

    note = fields.Html(
        string="Notes",
    )
