from odoo import fields, models


class RoomBooking(models.Model):
    _name = "room.booking"
    _description = "Room Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Subject", required=True)

    room_id = fields.Many2one("room.booking.room", string="Room", required=True)

    organizer_id = fields.Many2one("res.users", string="Organizer", required=True, default=lambda self: self.env.user)

    attendee_ids = fields.Many2many("res.partner", string="Attendees")

    start = fields.Datetime(string="Start", required=True)

    stop = fields.Datetime(string="Stop", required=True)

    note = fields.Html(string="Notes")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ], string="Status", default="draft", tracking=True)

    def action_confirm(self):
        for booking in self:
            if booking.state == "draft":
                booking.state = "confirmed"

    def action_done(self):
        for booking in self:
            if booking.state == "confirmed":
                booking.state = "done"

    def action_cancel(self):
        for booking in self:
            if booking.state in ("draft", "confirmed"):
                booking.state = "cancelled"

    def action_reset_to_draft(self):
        for booking in self:
            if booking.state == "cancelled":
                booking.state = "draft"