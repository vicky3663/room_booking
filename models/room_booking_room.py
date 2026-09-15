from odoo import api, fields, models


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

    booking_count = fields.Integer(
        string="Bookings",
        compute="_compute_booking_count",
        store=True,
    )

    @api.depends("booking_ids")
    def _compute_booking_count(self):
        for room in self:
            room.booking_count = len(room.booking_ids)
    
    def action_view_bookings(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Bookings",
            "res_model": "room.booking",
            "view_mode": "list,form",
            "domain": [("room_id", "=", self.id)],
            "context": {
                "default_room_id": self.id,
            },
        }
