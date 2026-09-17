{
    "name": "Meeting Room Booking",
    "summary": "Manage meeting rooms and room bookings",
    "description": """
Meeting Room Booking
====================

A small training module used to manage meeting rooms and bookings.

It allows employees to book meeting rooms for specific time slots,
while providing room configuration, booking history, and reminders.
""",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "author": "Dark",
    "website": "https://www.example.com",
    "license": "LGPL-3",
    "icon": "/room_booking/static/description/icon.png",
    "application": True,
    "installable": True,
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/room_booking_security.xml",
        "security/ir.model.access.csv",
        "data/room_booking_mail_template.xml",
        "data/room_booking_cron.xml",
        "views/room_booking_equipment_views.xml",
        "views/room_booking_room_views.xml",
        "views/room_booking_views.xml",
        "views/room_booking_menu.xml",
    ],
    "demo": [
         "demo/room_booking_demo.xml",
            ],
    "assets": {},
}
