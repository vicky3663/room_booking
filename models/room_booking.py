from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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

    duration = fields.Float(
        string="Duration",
        compute="_compute_duration",
        inverse="_inverse_duration",
        store=True,
    )

    note = fields.Html(string="Notes")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ], string="Status", default="draft", tracking=True, copy="False")

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
    
    @api.depends("start", "stop")
    def _compute_duration(self):
        for booking in self:
            if booking.start and booking.stop:
                delta = booking.stop - booking.start
                booking.duration = delta.total_seconds() / 3600
            else:
                booking.duration = 0.0
    
    def _inverse_duration(self):
        for booking in self:
            if booking.start and booking.duration:
                booking.stop = booking.start + timedelta(hours=booking.duration)
    
    @api.constrains("start", "stop")
    def _check_stop_after_start(self):
        for booking in self:
            if booking.start and booking.stop and booking.stop <= booking.start:
                raise ValidationError(_("The stop time must be later than the start time."))

    @api.constrains("start")
    def _check_start_not_in_past(self):
        for booking in self:
            if booking.start and booking.start < fields.Datetime.now():
                raise ValidationError(
                    _("The booking start time cannot be in the past.")
                )

    @api.constrains("room_id", "start", "stop")
    def _check_no_overlap(self):
        for booking in self:
            if not booking.room_id or not booking.start or not booking.stop:
                continue

            overlapping_bookings = self.search([
                ("id", "!=", booking.id),
                ("room_id", "=", booking.room_id.id),
                ("start", "<", booking.stop),
                ("stop", ">", booking.start),
            ])

            if overlapping_bookings:
                raise ValidationError(
                    _("This room is already booked during this time.")
                )