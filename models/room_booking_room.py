from odoo import fields, models


class RoomBookingRoom(models.Model):
    _name = "room.booking.room"
    _description = "Meeting Room"

    name = fields.Char(
        string="Name",
        required=True,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    capacity = fields.Integer(
        string="Capacity",
    )

    floor = fields.Char(
        string="Floor",
    )

    equipment_ids = fields.Many2many(
        "room.booking.equipment",
        string="Equipment",
    )

    booking_ids = fields.One2many(
        "room.booking",
        "room_id",
        string="Bookings",
    )
