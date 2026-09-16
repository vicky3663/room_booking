from odoo import _, fields, models


class RoomBookingEquipment(models.Model):
    _name = "room.booking.equipment"
    _description = "Meeting Room Equipment"

    _sql_constraints = [
        (
            "room_booking_equipment_name_unique",
            "UNIQUE(name)",
            _("Equipment name must be unique."),
        ),
    ]

    name = fields.Char(
        string="Name",
        required=True,
    )
