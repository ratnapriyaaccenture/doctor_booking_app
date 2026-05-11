# -*- coding: utf-8 -*-
"""
DocBook - Doctor Booking App
Generates representative mockup screenshots for each screen using PIL.
Run: python generate_screenshots.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "assets/screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

# Phone frame: 390 x 844 px (iPhone 14 logical resolution scaled 2x = 780x1688)
W, H = 780, 1688

# Color palette
C_PRIMARY       = (26, 115, 232)
C_PRIMARY_DARK  = (21, 87, 176)
C_SECONDARY     = (52, 168, 83)
C_ACCENT        = (255, 107, 107)
C_BG            = (248, 249, 250)
C_SURFACE       = (255, 255, 255)
C_TEXT          = (26, 26, 46)
C_TEXT2         = (107, 114, 128)
C_DIVIDER       = (229, 231, 235)
C_STAR          = (251, 188, 4)
C_WHITE         = (255, 255, 255)
C_GREEN         = (52, 168, 83)
C_YELLOW        = (251, 191, 36)
C_RED           = (239, 68, 68)
C_GRAY          = (156, 163, 175)


def new_img():
    img = Image.new("RGB", (W, H), C_BG)
    return img, ImageDraw.Draw(img)


def load_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("C:/Windows/Fonts/calibrib.ttf", size)
        return ImageFont.truetype("C:/Windows/Fonts/calibri.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_rect(d, x1, y1, x2, y2, fill, radius=0):
    if radius > 0:
        d.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill)
    else:
        d.rectangle([x1, y1, x2, y2], fill=fill)


def draw_text(d, text, x, y, font, color=C_TEXT, anchor="la"):
    d.text((x, y), text, font=font, fill=color, anchor=anchor)


def draw_status_bar(d):
    draw_rect(d, 0, 0, W, 60, C_PRIMARY)
    f = load_font(28)
    draw_text(d, "9:41", 40, 18, f, C_WHITE)
    draw_text(d, "DocBook", W // 2, 18, load_font(30, True), C_WHITE, anchor="ma")


def draw_gradient_header(img, d, title, subtitle="", height=280):
    for y in range(height):
        ratio = y / height
        r = int(C_PRIMARY[0] + (C_PRIMARY_DARK[0] - C_PRIMARY[0]) * ratio)
        g = int(C_PRIMARY[1] + (C_PRIMARY_DARK[1] - C_PRIMARY[1]) * ratio)
        b = int(C_PRIMARY[2] + (C_PRIMARY_DARK[2] - C_PRIMARY[2]) * ratio)
        d.line([(0, y), (W, y)], fill=(r, g, b))

    draw_text(d, title, 40, 80, load_font(52, True), C_WHITE)
    if subtitle:
        draw_text(d, subtitle, 40, 148, load_font(32), (204, 221, 255))


def draw_card(d, x1, y1, x2, y2, shadow=True, radius=20):
    if shadow:
        draw_rect(d, x1 + 4, y1 + 4, x2 + 4, y2 + 4,
                  (0, 0, 0, 30) if False else (200, 210, 220), radius=radius)
    draw_rect(d, x1, y1, x2, y2, C_SURFACE, radius=radius)


def draw_avatar(d, cx, cy, r, bg_color, initials, font_size=36):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg_color)
    draw_text(d, initials, cx, cy, load_font(font_size, True), C_WHITE, anchor="mm")


def draw_stars(d, x, y, rating=4.7, size=30):
    full = int(rating)
    for i in range(5):
        color = C_STAR if i < full else C_DIVIDER
        star_x = x + i * (size + 4)
        d.polygon([
            (star_x + size // 2, y),
            (star_x + size * 0.62, y + size * 0.38),
            (star_x + size, y + size * 0.38),
            (star_x + size * 0.69, y + size * 0.62),
            (star_x + size * 0.81, y + size),
            (star_x + size // 2, y + size * 0.76),
            (star_x + size * 0.19, y + size),
            (star_x + size * 0.31, y + size * 0.62),
            (star_x + 0, y + size * 0.38),
            (star_x + size * 0.38, y + size * 0.38),
        ], fill=color)


def draw_chip(d, x, y, text, selected=False, font_size=26):
    f = load_font(font_size)
    bbox = f.getbbox(text)
    tw = bbox[2] - bbox[0]
    pad = 24
    x2 = x + tw + pad * 2
    y2 = y + 52
    fill = C_PRIMARY if selected else C_SURFACE
    border = C_PRIMARY if selected else C_DIVIDER
    draw_rect(d, x, y, x2, y2, fill, radius=26)
    d.rounded_rectangle([x, y, x2, y2], radius=26, outline=border, width=2)
    text_color = C_WHITE if selected else C_TEXT
    draw_text(d, text, x + pad, y + 12, f, text_color)
    return x2 + 16


def draw_bottom_button(d, text, y_start=1560, color=C_PRIMARY):
    draw_rect(d, 40, y_start, W - 40, y_start + 96, color, radius=20)
    f = load_font(38, True)
    draw_text(d, text, W // 2, y_start + 30, f, C_WHITE, anchor="ma")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — Home Screen
# ══════════════════════════════════════════════════════════════════════════════

def make_home():
    img, d = new_img()

    # Gradient header
    draw_gradient_header(img, d, "Find a Doctor", "37 doctors available", height=250)
    draw_status_bar(d)

    # Calendar icon top-right
    draw_rect(d, W - 90, 72, W - 28, 134, (255, 255, 255, 60) if False else C_PRIMARY_DARK, radius=12)
    draw_text(d, "Cal", W - 59, 88, load_font(24, True), C_WHITE, anchor="ma")

    # Search bar
    draw_card(d, 20, 256, W - 20, 332, shadow=False, radius=16)
    d.rounded_rectangle([20, 256, W - 20, 332], radius=16, outline=C_DIVIDER, width=2)
    draw_text(d, "  Search by name, specialty, hospital...", 70, 276, load_font(28), C_TEXT2)
    # Search icon circle
    d.ellipse([32, 268, 64, 300], fill=C_BG)
    draw_text(d, "Q", 48, 270, load_font(26, True), C_TEXT2, anchor="ma")

    # City filter row
    draw_text(d, "City", 36, 350, load_font(28, True))
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad"]
    cx = 36
    for i, city in enumerate(cities):
        cx = draw_chip(d, cx, 390, city, selected=(i == 0))
        if cx > W - 60:
            break

    # Specialty filter row
    draw_text(d, "Specialty", 36, 462, load_font(28, True))
    specs = ["Cardiologist", "Dermatologist", "Pediatrician"]
    cx = 36
    for i, sp in enumerate(specs):
        cx = draw_chip(d, cx, 502, sp, selected=(i == 1))
        if cx > W - 40:
            break

    # Min Rating row
    draw_text(d, "Min Rating:", 36, 572, load_font(28, True))
    ratings = ["All", "3+", "3.5+", "4+", "4.5+"]
    cx = 240
    for i, r in enumerate(ratings):
        cx = draw_chip(d, cx, 566, r, selected=(i == 3), font_size=24)

    # Results count
    draw_text(d, "37 doctors found", 36, 640, load_font(28), C_TEXT2)

    # Doctor Cards
    doctors = [
        ("Dr. Priya Sharma", "Cardiologist", "Fortis Hospital, Mumbai", 4.9, "PS", (26, 115, 232), 900, 15),
        ("Dr. Amit Kumar", "Neurologist", "AIIMS, Delhi", 4.7, "AK", (52, 168, 83), 1200, 18),
        ("Dr. Leena Patel", "Dermatologist", "Apollo Hospital, Bangalore", 4.8, "LP", (156, 39, 176), 700, 12),
    ]

    y = 680
    for (name, spec, hosp, rating, init, avatar_color, fee, exp) in doctors:
        if y + 200 > H - 80:
            break
        draw_card(d, 20, y, W - 20, y + 196, radius=20)
        # Avatar
        draw_avatar(d, 80, y + 98, 52, avatar_color, init, font_size=32)
        # Text
        draw_text(d, name, 152, y + 30, load_font(34, True))
        draw_text(d, spec + "  |  " + str(exp) + " yrs", 152, y + 74, load_font(26), C_TEXT2)
        draw_stars(d, 152, y + 108, rating, size=24)
        draw_text(d, str(rating) + " (198 reviews)", 152 + 5 * 28 + 8, y + 112, load_font(24), C_TEXT2)
        draw_text(d, hosp[:38], 152, y + 146, load_font(26), C_TEXT2)
        # Fee badge
        draw_rect(d, W - 170, y + 130, W - 40, y + 172, C_PRIMARY, radius=10)
        draw_text(d, "Rs." + str(fee), W - 105, y + 140, load_font(26, True), C_WHITE, anchor="ma")
        y += 216

    img.save(os.path.join(OUT_DIR, "home_screen.png"))
    print("[OK] home_screen.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — Doctor Detail
# ══════════════════════════════════════════════════════════════════════════════

def make_doctor_detail():
    img, d = new_img()
    draw_status_bar(d)

    # Gradient header
    draw_gradient_header(img, d, "", height=370)

    # Back arrow area
    draw_text(d, "< Back", 40, 70, load_font(28), C_WHITE)

    # Large avatar
    draw_avatar(d, W // 2, 240, 90, (26, 115, 232), "PS", font_size=52)

    # Name & specialty
    draw_text(d, "Dr. Priya Sharma", W // 2, 350, load_font(46, True), C_WHITE, anchor="ma")
    draw_text(d, "Cardiologist  |  MBBS, MD (Cardiology), DM", W // 2, 406, load_font(26), (204, 221, 255), anchor="ma")

    # Stars row
    draw_stars(d, 240, 452, 4.9, size=30)
    draw_text(d, "4.9 (287 reviews)", 400, 456, load_font(28), (204, 221, 255))

    # Stats card
    draw_card(d, 30, 510, W - 30, 630, radius=20)
    stats = [("15 yrs", "Experience"), ("1,200+", "Patients"), ("Rs.900", "Consult Fee")]
    sx = 90
    for val, lbl in stats:
        draw_text(d, val, sx, 532, load_font(34, True), C_PRIMARY, anchor="ma")
        draw_text(d, lbl, sx, 578, load_font(24), C_TEXT2, anchor="ma")
        sx += (W - 60) // 3

    # Dividers between stats
    d.line([(W // 3 + 30, 530), (W // 3 + 30, 620)], fill=C_DIVIDER, width=2)
    d.line([(2 * W // 3 + 10, 530), (2 * W // 3 + 10, 620)], fill=C_DIVIDER, width=2)

    # Hospital
    draw_text(d, "Fortis Hospital, Mulund, Mumbai", 50, 648, load_font(28), C_TEXT2)

    # About section
    draw_text(d, "About", 36, 700, load_font(36, True))
    about = (
        "Dr. Priya Sharma is a renowned cardiologist with 15 years\n"
        "of experience in interventional cardiology, heart failure\n"
        "management and preventive cardiology. She specialises in\n"
        "minimally invasive cardiac procedures."
    )
    draw_text(d, about, 36, 750, load_font(26), C_TEXT2)

    # Available days
    draw_text(d, "Available Days", 36, 914, load_font(34, True))
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    dx = 36
    for i, day in enumerate(days):
        sel = i not in [2, 5]  # Wed, Sat unavailable
        dx = draw_chip(d, dx, 958, day, selected=sel, font_size=26)

    # Time slots
    draw_text(d, "Time Slots", 36, 1040, load_font(34, True))
    slots = ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "03:00 PM", "04:00 PM"]
    cols = 3
    for i, slot in enumerate(slots):
        sx2 = 36 + (i % cols) * 240
        sy = 1084 + (i // cols) * 76
        draw_card(d, sx2, sy, sx2 + 220, sy + 60, shadow=False, radius=12)
        d.rounded_rectangle([sx2, sy, sx2 + 220, sy + 60], radius=12, outline=C_DIVIDER, width=2)
        draw_text(d, slot, sx2 + 110, sy + 14, load_font(26), C_TEXT, anchor="ma")

    # Consultation types
    draw_text(d, "Consultation Type", 36, 1260, load_font(34, True))
    types = [("In-Person", "Rs.900"), ("Video Call", "Rs.720"), ("Phone Call", "Rs.540")]
    tx = 36
    for i, (typ, price) in enumerate(types):
        x2 = tx + 218
        sel = i == 0
        fill = C_PRIMARY if sel else C_BG
        draw_rect(d, tx, 1304, x2, 1404, fill, radius=16)
        d.rounded_rectangle([tx, 1304, x2, 1404], radius=16, outline=C_PRIMARY if sel else C_DIVIDER, width=2)
        draw_text(d, typ, tx + 109, 1322, load_font(24, sel), C_WHITE if sel else C_TEXT, anchor="ma")
        draw_text(d, price, tx + 109, 1360, load_font(26, True), C_WHITE if sel else C_PRIMARY, anchor="ma")
        tx = x2 + 20

    # Book button
    draw_bottom_button(d, "Book Appointment", y_start=1560)

    img.save(os.path.join(OUT_DIR, "doctor_detail.png"))
    print("[OK] doctor_detail.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 3 — Booking Screen
# ══════════════════════════════════════════════════════════════════════════════

def make_booking():
    img, d = new_img()
    draw_status_bar(d)

    # Header
    draw_rect(d, 0, 0, W, 130, C_PRIMARY)
    draw_text(d, "< Book Appointment", 36, 70, load_font(34, True), C_WHITE)

    # Doctor summary card
    draw_card(d, 20, 148, W - 20, 264)
    draw_avatar(d, 72, 206, 44, C_PRIMARY, "PS", font_size=28)
    draw_text(d, "Dr. Priya Sharma", 132, 166, load_font(32, True))
    draw_text(d, "Cardiologist", 132, 208, load_font(26), C_TEXT2)
    draw_text(d, "Fortis Hospital, Mumbai", 132, 242, load_font(24), C_TEXT2)

    # Consultation type
    draw_text(d, "Consultation Type", 36, 296, load_font(32, True))
    cons = [("In-Person", "Rs.900", True), ("Video Call", "Rs.720", False), ("Phone Call", "Rs.540", False)]
    cx = 36
    for label, price, sel in cons:
        x2 = cx + 218
        fill = C_PRIMARY if sel else C_BG
        draw_rect(d, cx, 338, x2, 438, fill, radius=16)
        d.rounded_rectangle([cx, 338, x2, 438], radius=16, outline=C_PRIMARY if sel else C_DIVIDER, width=2)
        draw_text(d, label, cx + 109, 354, load_font(26, sel), C_WHITE if sel else C_TEXT, anchor="ma")
        draw_text(d, price, cx + 109, 394, load_font(28, True), C_WHITE if sel else C_PRIMARY, anchor="ma")
        cx = x2 + 20

    # Date picker
    draw_text(d, "Select Date", 36, 462, load_font(32, True))
    months = ["May", "May", "May", "May", "May", "May", "May"]
    days_n = [12, 13, 14, 15, 16, 19, 20]
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Mon", "Tue"]
    dx = 36
    for i in range(7):
        x2 = dx + 86
        sel = i == 3
        fill = C_PRIMARY if sel else C_SURFACE
        draw_rect(d, dx, 508, x2, 612, fill, radius=16)
        d.rounded_rectangle([dx, 508, x2, 612], radius=16, outline=C_PRIMARY if sel else C_DIVIDER, width=2)
        draw_text(d, day_names[i], dx + 43, 522, load_font(24), C_WHITE if sel else C_TEXT2, anchor="ma")
        draw_text(d, str(days_n[i]), dx + 43, 558, load_font(34, True), C_WHITE if sel else C_TEXT, anchor="ma")
        draw_text(d, months[i], dx + 43, 594, load_font(22), C_WHITE if sel else C_TEXT2, anchor="ma")
        dx = x2 + 14

    # Time slots
    draw_text(d, "Select Time Slot", 36, 640, load_font(32, True))
    slots = ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "03:00 PM", "04:00 PM"]
    for i, slot in enumerate(slots):
        sx = 36 + (i % 3) * 242
        sy = 684 + (i // 3) * 82
        sel = i == 1
        fill = C_PRIMARY if sel else C_SURFACE
        draw_rect(d, sx, sy, sx + 222, sy + 66, fill, radius=14)
        d.rounded_rectangle([sx, sy, sx + 222, sy + 66], radius=14, outline=C_PRIMARY if sel else C_DIVIDER, width=2)
        draw_text(d, slot, sx + 111, sy + 14, load_font(26, sel), C_WHITE if sel else C_TEXT, anchor="ma")

    # Fee breakdown
    draw_card(d, 20, 866, W - 20, 1020, radius=20)
    draw_text(d, "Fee Breakdown", 50, 886, load_font(30, True))
    d.line([(36, 930), (W - 36, 930)], fill=C_DIVIDER, width=2)
    draw_text(d, "Consultation Fee", 50, 944, load_font(28), C_TEXT2)
    draw_text(d, "Rs.900", W - 60, 944, load_font(28), C_TEXT, anchor="ra")
    draw_text(d, "GST (18%)", 50, 984, load_font(28), C_TEXT2)
    draw_text(d, "Rs.162", W - 60, 984, load_font(28), C_TEXT, anchor="ra")

    draw_card(d, 20, 1030, W - 20, 1100)
    draw_text(d, "Total Amount", 50, 1046, load_font(32, True))
    draw_text(d, "Rs.1,062", W - 60, 1046, load_font(36, True), C_PRIMARY, anchor="ra")

    # Proceed button
    draw_bottom_button(d, "Proceed to Payment  ->", y_start=1560, color=C_PRIMARY)

    img.save(os.path.join(OUT_DIR, "booking_screen.png"))
    print("[OK] booking_screen.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 4 — Payment Screen (UPI)
# ══════════════════════════════════════════════════════════════════════════════

def make_payment_upi():
    img, d = new_img()
    draw_status_bar(d)

    draw_rect(d, 0, 0, W, 130, C_PRIMARY)
    draw_text(d, "< Payment", 36, 70, load_font(38, True), C_WHITE)
    draw_text(d, "Lock Secure", W - 200, 80, load_font(26), C_SECONDARY)

    # Order summary gradient card
    for y in range(130, 360):
        ratio = (y - 130) / 230
        r = int(C_PRIMARY[0] * (1 - ratio) + C_PRIMARY_DARK[0] * ratio)
        g = int(C_PRIMARY[1] * (1 - ratio) + C_PRIMARY_DARK[1] * ratio)
        b = int(C_PRIMARY[2] * (1 - ratio) + C_PRIMARY_DARK[2] * ratio)
        d.line([(20, y), (W - 20, y)], fill=(r, g, b))
    d.rounded_rectangle([20, 130, W - 20, 360], radius=20, outline=(26, 87, 176), width=2)

    draw_text(d, "Order Summary", 50, 148, load_font(26), (204, 221, 255))
    draw_text(d, "Dr. Priya Sharma", 50, 186, load_font(36, True), C_WHITE)
    draw_text(d, "In-Person Consultation", 50, 232, load_font(28), (204, 221, 255))
    draw_text(d, "Thu, May 15  |  10:00 AM", 50, 272, load_font(26), (204, 221, 255))
    d.line([(36, 308), (W - 36, 308)], fill=(255, 255, 255, 60) if False else (100, 130, 180), width=2)
    draw_text(d, "Total Amount", 50, 320, load_font(28, True), C_WHITE)
    draw_text(d, "Rs.1,062", W - 60, 316, load_font(44, True), C_WHITE, anchor="ra")

    # Payment method tabs
    draw_card(d, 20, 380, W - 20, 500, radius=16)
    draw_text(d, "Payment Method", 50, 394, load_font(30, True))
    tabs = ["UPI", "Card", "Wallet", "Net Bank"]
    tw = (W - 60) // 4
    for i, tab in enumerate(tabs):
        tx = 30 + i * tw
        fill = C_PRIMARY if i == 0 else C_BG
        draw_rect(d, tx, 430, tx + tw - 8, 492, fill, radius=12)
        draw_text(d, tab, tx + (tw - 8) // 2, 448, load_font(26, i == 0), C_WHITE if i == 0 else C_TEXT2, anchor="ma")

    # UPI form
    draw_card(d, 20, 520, W - 20, 1100, radius=20)
    draw_text(d, "Pay via UPI", 50, 540, load_font(34, True))

    # QR code box
    draw_rect(d, 120, 600, W - 120, 900, C_BG, radius=20)
    d.rounded_rectangle([120, 600, W - 120, 900], radius=20, outline=C_DIVIDER, width=2)

    # Draw simple QR-like pattern
    qr_x, qr_y = 260, 630
    cell = 18
    pattern = [
        [1,1,1,1,1,1,1,0,1,0,0],
        [1,0,0,0,0,0,1,0,0,1,0],
        [1,0,1,1,1,0,1,0,1,0,1],
        [1,0,1,1,1,0,1,0,0,1,1],
        [1,0,1,1,1,0,1,0,1,1,0],
        [1,0,0,0,0,0,1,0,0,0,1],
        [1,1,1,1,1,1,1,0,1,0,1],
        [0,0,0,0,0,0,0,0,0,1,0],
        [1,0,1,1,0,1,1,0,1,0,1],
        [0,1,0,0,1,0,0,1,0,1,1],
        [1,1,1,0,1,1,1,0,1,0,0],
    ]
    for row_i, row in enumerate(pattern):
        for col_i, val in enumerate(row):
            if val:
                d.rectangle([
                    qr_x + col_i * cell,
                    qr_y + row_i * cell,
                    qr_x + col_i * cell + cell - 2,
                    qr_y + row_i * cell + cell - 2
                ], fill=C_TEXT)

    draw_text(d, "Scan to Pay", W // 2, 852, load_font(26), C_TEXT2, anchor="ma")
    draw_text(d, "docbook@ybl", W // 2, 882, load_font(28, True), C_PRIMARY, anchor="ma")

    # OR divider
    d.line([(60, 924), (310, 924)], fill=C_DIVIDER, width=2)
    draw_text(d, "OR", W // 2, 910, load_font(26), C_TEXT2, anchor="ma")
    d.line([(470, 924), (720, 924)], fill=C_DIVIDER, width=2)

    # UPI ID field
    draw_rect(d, 40, 948, W - 40, 1034, C_BG, radius=12)
    d.rounded_rectangle([40, 948, W - 40, 1034], radius=12, outline=C_DIVIDER, width=2)
    draw_text(d, "Enter UPI ID  (yourname@upi)", 80, 974, load_font(28), C_TEXT2)

    draw_text(d, "Accepted: Google Pay, PhonePe, Paytm, BHIM", W // 2, 1060, load_font(24), C_TEXT2, anchor="ma")

    draw_bottom_button(d, "Pay Rs.1,062 Securely", y_start=1560, color=C_SECONDARY)

    img.save(os.path.join(OUT_DIR, "payment_upi.png"))
    print("[OK] payment_upi.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 5 — Payment Card
# ══════════════════════════════════════════════════════════════════════════════

def make_payment_card():
    img, d = new_img()
    draw_status_bar(d)

    draw_rect(d, 0, 0, W, 130, C_PRIMARY)
    draw_text(d, "< Payment", 36, 70, load_font(38, True), C_WHITE)

    # Order summary
    for y in range(130, 320):
        ratio = (y - 130) / 190
        r = int(C_PRIMARY[0] * (1 - ratio) + C_PRIMARY_DARK[0] * ratio)
        g = int(C_PRIMARY[1] * (1 - ratio) + C_PRIMARY_DARK[1] * ratio)
        b = int(C_PRIMARY[2] * (1 - ratio) + C_PRIMARY_DARK[2] * ratio)
        d.line([(20, y), (W - 20, y)], fill=(r, g, b))
    d.rounded_rectangle([20, 130, W - 20, 320], radius=20, outline=(26, 87, 176), width=2)
    draw_text(d, "Order Summary", 50, 148, load_font(26), (204, 221, 255))
    draw_text(d, "Dr. Priya Sharma  —  In-Person  |  Rs.1,062", 50, 186, load_font(28, True), C_WHITE)
    draw_text(d, "Thu, May 15  |  10:00 AM", 50, 232, load_font(26), (204, 221, 255))
    draw_text(d, "Rs.1,062", W - 60, 260, load_font(40, True), C_WHITE, anchor="ra")

    # Tabs
    draw_card(d, 20, 340, W - 20, 440, radius=16)
    tabs = ["UPI", "Card", "Wallet", "Net Bank"]
    tw = (W - 60) // 4
    for i, tab in enumerate(tabs):
        tx = 30 + i * tw
        fill = C_PRIMARY if i == 1 else C_BG
        draw_rect(d, tx, 370, tx + tw - 8, 432, fill, radius=12)
        draw_text(d, tab, tx + (tw - 8) // 2, 388, load_font(26, i == 1), C_WHITE if i == 1 else C_TEXT2, anchor="ma")

    # Card form
    draw_card(d, 20, 460, W - 20, 1480, radius=20)
    draw_text(d, "Pay via Card", 50, 480, load_font(34, True))

    # Saved cards
    draw_text(d, "Saved Cards", 50, 528, load_font(28), C_TEXT2)
    saved = [("Visa  ....  4242", "Ratna D Priya", True), ("Mastercard  ....  8888", "Ratna D Priya", False)]
    sy = 566
    for brand, holder, sel in saved:
        fill = (240, 245, 255) if sel else C_BG
        border = C_PRIMARY if sel else C_DIVIDER
        draw_rect(d, 40, sy, W - 40, sy + 88, fill, radius=16)
        d.rounded_rectangle([40, sy, W - 40, sy + 88], radius=16, outline=border, width=2)
        draw_text(d, brand, 100, sy + 14, load_font(28, sel))
        draw_text(d, holder, 100, sy + 52, load_font(24), C_TEXT2)
        if sel:
            draw_text(d, "CHECK", W - 80, sy + 30, load_font(22, True), C_PRIMARY, anchor="ra")
        sy += 104

    # Divider
    d.line([(80, 790), (310, 790)], fill=C_DIVIDER, width=2)
    draw_text(d, "Add New Card", W // 2, 778, load_font(26), C_TEXT2, anchor="ma")
    d.line([(470, 790), (700, 790)], fill=C_DIVIDER, width=2)

    # Card preview
    for y in range(818, 978):
        ratio = (y - 818) / 160
        r = int(26 * (1 - ratio) + 108 * ratio)
        g = int(115 * (1 - ratio) + 92 * ratio)
        b = int(232 * (1 - ratio) + 231 * ratio)
        d.line([(40, y), (W - 40, y)], fill=(r, g, b))
    d.rounded_rectangle([40, 818, W - 40, 978], radius=20, outline=(100, 100, 200), width=0)
    draw_text(d, "DocBook Pay", 70, 834, load_font(24), (255, 255, 255, 180) if False else (200, 220, 255))
    draw_text(d, "....  ....  ....  ....", 70, 880, load_font(32, True), C_WHITE)
    draw_text(d, "CARD HOLDER", 70, 940, load_font(22), (200, 220, 255))
    draw_text(d, "MM/YY", W - 80, 940, load_font(22), (200, 220, 255), anchor="ra")

    # Form fields
    fields = [("Card Number", "1234  5678  9012  3456"), ("Cardholder Name", "Name on card"), ("Expiry  MM/YY", "")]
    fy = 998
    for label, hint in fields:
        draw_rect(d, 40, fy, W - 40, fy + 80, C_BG, radius=12)
        d.rounded_rectangle([40, fy, W - 40, fy + 80], radius=12, outline=C_DIVIDER, width=2)
        draw_text(d, label, 70, fy + 10, load_font(22), C_TEXT2)
        draw_text(d, hint if hint else "                           CVV: ***", 70, fy + 44, load_font(28), C_TEXT)
        fy += 96

    draw_bottom_button(d, "Pay Rs.1,062 Securely", y_start=1560, color=C_SECONDARY)

    img.save(os.path.join(OUT_DIR, "payment_card.png"))
    print("[OK] payment_card.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 6 — Payment Wallet
# ══════════════════════════════════════════════════════════════════════════════

def make_payment_wallet():
    img, d = new_img()
    draw_status_bar(d)

    draw_rect(d, 0, 0, W, 130, C_PRIMARY)
    draw_text(d, "< Payment", 36, 70, load_font(38, True), C_WHITE)

    # Tabs
    draw_card(d, 20, 148, W - 20, 248, radius=16)
    tabs = ["UPI", "Card", "Wallet", "Net Bank"]
    tw = (W - 60) // 4
    for i, tab in enumerate(tabs):
        tx = 30 + i * tw
        fill = C_PRIMARY if i == 2 else C_BG
        draw_rect(d, tx, 178, tx + tw - 8, 240, fill, radius=12)
        draw_text(d, tab, tx + (tw - 8) // 2, 196, load_font(26, i == 2), C_WHITE if i == 2 else C_TEXT2, anchor="ma")

    # Wallet form
    draw_card(d, 20, 268, W - 20, 780, radius=20)
    draw_text(d, "Select Wallet", 50, 288, load_font(34, True))

    wallets = [
        ("Paytm", (0, 186, 242)),
        ("PhonePe", (95, 37, 159)),
        ("Google Pay", (66, 133, 244)),
        ("Amazon Pay", (255, 153, 0)),
    ]
    cols = 2
    wx_start = 50
    for i, (wname, wcolor) in enumerate(wallets):
        col = i % cols
        row = i // cols
        wx = wx_start + col * 340
        wy = 340 + row * 140
        x2 = wx + 310
        y2 = wy + 108
        sel = i == 0
        border_color = wcolor if sel else C_DIVIDER
        bg = tuple(max(0, min(255, c + 220 - max(wcolor))) for c in wcolor) if sel else C_BG
        draw_rect(d, wx, wy, x2, y2, bg if not sel else (240, 250, 255), radius=16)
        d.rounded_rectangle([wx, wy, x2, y2], radius=16, outline=border_color, width=2 if sel else 1)
        # Icon circle
        d.ellipse([wx + 18, wy + 22, wx + 76, wy + 80], fill=wcolor)
        draw_text(d, wname[0], wx + 47, wy + 35, load_font(32, True), C_WHITE, anchor="ma")
        draw_text(d, wname, wx + 90, wy + 40, load_font(28, sel), wcolor if sel else C_TEXT)

    # Info text
    draw_text(d, "Select your preferred digital wallet to pay", W // 2, 660, load_font(26), C_TEXT2, anchor="ma")
    draw_text(d, "Fast, secure, and instant payment", W // 2, 700, load_font(26), C_TEXT2, anchor="ma")

    draw_bottom_button(d, "Pay Rs.1,062 Securely", y_start=1560, color=C_SECONDARY)

    img.save(os.path.join(OUT_DIR, "payment_wallet.png"))
    print("[OK] payment_wallet.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 7 — Payment Net Banking
# ══════════════════════════════════════════════════════════════════════════════

def make_payment_netbanking():
    img, d = new_img()
    draw_status_bar(d)

    draw_rect(d, 0, 0, W, 130, C_PRIMARY)
    draw_text(d, "< Payment", 36, 70, load_font(38, True), C_WHITE)

    # Tabs
    draw_card(d, 20, 148, W - 20, 248, radius=16)
    tabs = ["UPI", "Card", "Wallet", "Net Bank"]
    tw = (W - 60) // 4
    for i, tab in enumerate(tabs):
        tx = 30 + i * tw
        fill = C_PRIMARY if i == 3 else C_BG
        draw_rect(d, tx, 178, tx + tw - 8, 240, fill, radius=12)
        draw_text(d, tab, tx + (tw - 8) // 2, 196, load_font(26, i == 3), C_WHITE if i == 3 else C_TEXT2, anchor="ma")

    # Net banking form
    draw_card(d, 20, 268, W - 20, 1140, radius=20)
    draw_text(d, "Net Banking", 50, 288, load_font(34, True))
    draw_text(d, "Select your bank", 50, 334, load_font(26), C_TEXT2)

    banks = [
        ("SBI", (26, 35, 126), "State Bank of India"),
        ("HDFC", (0, 76, 140), "HDFC Bank"),
        ("ICICI", (183, 28, 28), "ICICI Bank"),
        ("Axis", (136, 14, 79), "Axis Bank"),
        ("Kotak", (230, 81, 0), "Kotak Mahindra Bank"),
        ("BoB", (27, 94, 32), "Bank of Baroda"),
    ]
    by = 378
    for abbr, bcolor, bname in banks:
        draw_rect(d, 40, by, W - 40, by + 96, C_BG, radius=16)
        d.rounded_rectangle([40, by, W - 40, by + 96], radius=16, outline=C_DIVIDER, width=1)
        draw_rect(d, 60, by + 18, 122, by + 78, bcolor, radius=10)
        draw_text(d, abbr[0], 91, by + 30, load_font(32, True), C_WHITE, anchor="ma")
        draw_text(d, bname, 142, by + 36, load_font(30, True))
        draw_text(d, ">", W - 70, by + 38, load_font(28), C_TEXT2)
        by += 112

    draw_bottom_button(d, "Pay Rs.1,062 Securely", y_start=1560, color=C_SECONDARY)

    img.save(os.path.join(OUT_DIR, "payment_netbanking.png"))
    print("[OK] payment_netbanking.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 8 — Confirmation Screen
# ══════════════════════════════════════════════════════════════════════════════

def make_confirmation():
    img, d = new_img()
    draw_status_bar(d)
    draw_rect(d, 0, 0, W, 130, C_PRIMARY)

    # Success circle
    d.ellipse([W // 2 - 90, 148, W // 2 + 90, 328], fill=C_SECONDARY)
    draw_text(d, "OK", W // 2, 218, load_font(64, True), C_WHITE, anchor="mm")

    draw_text(d, "Booking Confirmed!", W // 2, 356, load_font(48, True), C_SECONDARY, anchor="ma")
    draw_text(d, "Your appointment has been booked successfully", W // 2, 406, load_font(26), C_TEXT2, anchor="ma")

    # Booking details card
    draw_card(d, 30, 444, W - 30, 1200, radius=24)

    rows = [
        ("Booking ID", "A3F7BC12"),
        ("Doctor", "Dr. Priya Sharma"),
        ("Specialty", "Cardiologist"),
        ("Hospital", "Fortis Hospital, Mumbai"),
        ("Date", "Thu, May 15, 2026"),
        ("Time", "10:00 AM"),
        ("Type", "In-Person Consultation"),
        ("Amount Paid", "Rs.1,062"),
        ("Payment", "UPI — docbook@ybl"),
        ("Transaction ID", "TXN1715123456789"),
    ]
    ry = 470
    for i, (label, value) in enumerate(rows):
        if ry > 1180:
            break
        if i > 0:
            d.line([(60, ry - 10), (W - 60, ry - 10)], fill=C_DIVIDER, width=1)
        draw_text(d, label, 60, ry, load_font(26), C_TEXT2)
        draw_text(d, value, W - 60, ry, load_font(26, True), C_TEXT, anchor="ra")
        ry += 72

    # Action buttons
    draw_rect(d, 36, 1226, W // 2 - 20, 1322, C_BG, radius=16)
    d.rounded_rectangle([36, 1226, W // 2 - 20, 1322], radius=16, outline=C_PRIMARY, width=2)
    draw_text(d, "Back to Home", (W // 2 - 20 + 36) // 2, 1258, load_font(28, True), C_PRIMARY, anchor="ma")

    draw_rect(d, W // 2 + 20, 1226, W - 36, 1322, C_PRIMARY, radius=16)
    draw_text(d, "My Bookings", (W // 2 + 20 + W - 36) // 2, 1258, load_font(28, True), C_WHITE, anchor="ma")

    img.save(os.path.join(OUT_DIR, "confirmation_screen.png"))
    print("[OK] confirmation_screen.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 9 — My Bookings
# ══════════════════════════════════════════════════════════════════════════════

def make_my_bookings():
    img, d = new_img()
    draw_status_bar(d)

    draw_rect(d, 0, 0, W, 130, C_PRIMARY)
    draw_text(d, "My Bookings", W // 2, 72, load_font(40, True), C_WHITE, anchor="ma")

    bookings = [
        ("A3F7BC12", "Dr. Priya Sharma", "Cardiologist", "Fortis Hospital", "Thu, May 15", "10:00 AM", "In-Person", "Rs.1,062", "Confirmed", C_SECONDARY),
        ("B9E2DA34", "Dr. Amit Kumar", "Neurologist", "AIIMS, Delhi", "Fri, May 16", "02:00 PM", "Video", "Rs.1,180", "Pending", C_YELLOW),
        ("C1F4AB56", "Dr. Leena Patel", "Dermatologist", "Apollo, Bangalore", "Mon, May 19", "11:00 AM", "Phone", "Rs.530", "Confirmed", C_SECONDARY),
    ]

    y = 150
    for booking_id, doc, spec, hosp, date, time, typ, amt, status, status_color in bookings:
        card_h = 220
        draw_card(d, 20, y, W - 20, y + card_h, radius=20)

        # Header row
        draw_text(d, "ID: " + booking_id, 50, y + 18, load_font(24), C_TEXT2)
        # Status badge
        bw = 200
        draw_rect(d, W - 60 - bw, y + 14, W - 40, y + 54, status_color, radius=10)
        draw_text(d, status, W - 40 - bw // 2, y + 24, load_font(22, True), C_WHITE, anchor="ma")

        d.line([(36, y + 66), (W - 36, y + 66)], fill=C_DIVIDER, width=1)

        # Doctor info
        draw_avatar(d, 68, y + 130, 42, C_PRIMARY, doc[3] + doc[4], font_size=26)
        draw_text(d, doc, 126, y + 84, load_font(30, True))
        draw_text(d, spec + "  |  " + hosp, 126, y + 124, load_font(24), C_TEXT2)
        draw_text(d, date + "  |  " + time + "  |  " + typ, 126, y + 162, load_font(24), C_TEXT2)
        draw_text(d, amt, W - 60, y + 84, load_font(32, True), C_PRIMARY, anchor="ra")

        y += card_h + 20

    img.save(os.path.join(OUT_DIR, "my_bookings.png"))
    print("[OK] my_bookings.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 10 — My Bookings Empty State
# ══════════════════════════════════════════════════════════════════════════════

def make_bookings_empty():
    img, d = new_img()
    draw_status_bar(d)

    draw_rect(d, 0, 0, W, 130, C_PRIMARY)
    draw_text(d, "My Bookings", W // 2, 72, load_font(40, True), C_WHITE, anchor="ma")

    # Empty state illustration
    d.ellipse([W // 2 - 120, 400, W // 2 + 120, 640], fill=C_DIVIDER)
    draw_text(d, "Cal", W // 2, 510, load_font(72, True), C_TEXT2, anchor="mm")

    draw_text(d, "No Bookings Yet", W // 2, 680, load_font(44, True), C_TEXT, anchor="ma")
    draw_text(d, "You have not booked any appointments yet.", W // 2, 736, load_font(28), C_TEXT2, anchor="ma")
    draw_text(d, "Find a doctor and book your first appointment!", W // 2, 776, load_font(28), C_TEXT2, anchor="ma")

    draw_rect(d, W // 2 - 200, 840, W // 2 + 200, 924, C_PRIMARY, radius=16)
    draw_text(d, "Browse Doctors", W // 2, 866, load_font(32, True), C_WHITE, anchor="ma")

    img.save(os.path.join(OUT_DIR, "my_bookings_empty.png"))
    print("[OK] my_bookings_empty.png")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 11 — Home Screen with Filter Applied
# ══════════════════════════════════════════════════════════════════════════════

def make_home_filtered():
    img, d = new_img()
    draw_gradient_header(img, d, "Find a Doctor", "5 doctors available", height=250)
    draw_status_bar(d)

    draw_text(d, "Cal", W - 59, 88, load_font(24, True), C_WHITE, anchor="ma")
    draw_card(d, 20, 256, W - 20, 332, shadow=False, radius=16)
    d.rounded_rectangle([20, 256, W - 20, 332], radius=16, outline=C_PRIMARY, width=2)
    draw_text(d, "  Cardiologist", 70, 276, load_font(28), C_TEXT)

    # City filter with Mumbai selected
    draw_text(d, "City", 36, 350, load_font(28, True))
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai"]
    cx = 36
    for i, city in enumerate(cities):
        cx = draw_chip(d, cx, 390, city, selected=(i == 0))
        if cx > W: break

    # Specialty with Cardiologist selected
    draw_text(d, "Specialty", 36, 462, load_font(28, True))
    specs = ["Cardiologist", "Dermatologist", "Pediatrician"]
    cx = 36
    for i, sp in enumerate(specs):
        cx = draw_chip(d, cx, 502, sp, selected=(i == 0))
        if cx > W: break

    draw_text(d, "Min Rating:", 36, 572, load_font(28, True))
    ratings = ["All", "3+", "3.5+", "4+", "4.5+"]
    cx = 240
    for i, r in enumerate(ratings):
        cx = draw_chip(d, cx, 566, r, selected=(i == 4), font_size=24)

    # Clear all button
    draw_text(d, "Clear all", W - 160, 574, load_font(26), C_ACCENT)

    draw_text(d, "5 doctors found", 36, 640, load_font(28), C_TEXT2)

    doctors = [
        ("Dr. Priya Sharma", "Cardiologist", "Fortis Hospital, Mumbai", 4.9, "PS", (26, 115, 232), 900),
        ("Dr. Ananya Bose", "Cardiologist", "Kokilaben Hospital, Mumbai", 4.7, "AB", (230, 81, 0), 1000),
        ("Dr. Vikram Malhotra", "Cardiologist", "Lilavati Hospital, Mumbai", 4.5, "VM", (0, 121, 107), 1100),
    ]

    y = 680
    for name, spec, hosp, rating, init, color, fee in doctors:
        if y + 200 > H - 80: break
        draw_card(d, 20, y, W - 20, y + 196, radius=20)
        draw_avatar(d, 80, y + 98, 52, color, init, font_size=32)
        draw_text(d, name, 152, y + 30, load_font(34, True))
        draw_text(d, spec, 152, y + 74, load_font(26), C_TEXT2)
        draw_stars(d, 152, y + 108, rating, size=24)
        draw_text(d, str(rating), 152 + 5 * 28 + 12, y + 112, load_font(24), C_TEXT2)
        draw_text(d, hosp, 152, y + 146, load_font(24), C_TEXT2)
        draw_rect(d, W - 170, y + 130, W - 40, y + 172, C_PRIMARY, radius=10)
        draw_text(d, "Rs." + str(fee), W - 105, y + 140, load_font(26, True), C_WHITE, anchor="ma")
        y += 216

    img.save(os.path.join(OUT_DIR, "home_filtered.png"))
    print("[OK] home_filtered.png")


if __name__ == "__main__":
    print("\nGenerating DocBook screen mockup screenshots -> assets/screenshots/\n")
    make_home()
    make_home_filtered()
    make_doctor_detail()
    make_booking()
    make_payment_upi()
    make_payment_card()
    make_payment_wallet()
    make_payment_netbanking()
    make_confirmation()
    make_my_bookings()
    make_bookings_empty()

    print("\nAll screenshots saved to: " + os.path.abspath(OUT_DIR) + "/")
    files = [f for f in os.listdir(OUT_DIR) if f.endswith(".png")]
    print("Files generated:", len(files))
    for f in sorted(files):
        size = os.path.getsize(os.path.join(OUT_DIR, f))
        print(f"  {f}  ({size:,} bytes)")
