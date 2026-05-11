# -*- coding: utf-8 -*-
"""
DocBook - Doctor Booking App
Generates ONE complete full-demo video (MP4 + MOV) covering every feature
in a single end-to-end walkthrough.
Run: python generate_full_demo.py
"""

import cv2
import numpy as np
import os

SCREENSHOTS = "assets/screenshots"
MP4_OUT = os.path.join("Video", "MP4", "DocBook_Full_Demo.mp4")
MOV_OUT = os.path.join("Video", "MOV", "DocBook_Full_Demo.mov")

FPS    = 30
VID_W  = 1920
VID_H  = 1080
PH_W   = 420   # phone screen width  (drawn at 2x = 840)
PH_H   = 910   # phone screen height (drawn at 2x = 1820, then scaled to fit)

# ── Colours (BGR) ─────────────────────────────────────────────────────────────
BG_TOP       = (28,  22,  14)
BG_BOT       = (10,   8,   5)
C_PRIMARY    = (232, 115,  26)
C_SEC        = ( 83, 168,  52)
C_PURPLE     = (159,  37,  95)
C_TEAL       = ( 94, 122,   0)
C_ORANGE     = (  0,  92, 230)
C_WHITE      = (255, 255, 255)
C_GRAY       = (170, 170, 190)
C_DARK_CARD  = ( 35,  30,  50)
C_ACCENT_LINE= (255, 200,  80)

SECTION_COLORS = {
    "home":     (232, 115,  26),
    "detail":   (176,  78,  16),
    "booking":  ( 94, 122,   0),
    "payment":  (159,  37,  95),
    "confirm":  ( 83, 168,  52),
    "bookings": (  0,  92, 230),
}

# ── Font helper ───────────────────────────────────────────────────────────────
FONT      = cv2.FONT_HERSHEY_SIMPLEX
FONT_BOLD = cv2.FONT_HERSHEY_DUPLEX

def txt(canvas, text, x, y, scale=1.0, color=C_WHITE,
        thick=2, anchor="left", bold=False):
    f = FONT_BOLD if bold else FONT
    (tw, th), _ = cv2.getTextSize(text, f, scale, thick)
    if anchor == "center":
        x -= tw // 2
    elif anchor == "right":
        x -= tw
    cv2.putText(canvas, text, (x, y), f, scale, color, thick, cv2.LINE_AA)
    return tw, th

def txt_shadow(canvas, text, x, y, scale, color, thick=2, anchor="left", bold=False):
    txt(canvas, text, x+2, y+2, scale, (0,0,0), thick, anchor, bold)
    txt(canvas, text, x,   y,   scale, color,   thick, anchor, bold)

# ── Base frame ────────────────────────────────────────────────────────────────
def make_base():
    f = np.zeros((VID_H, VID_W, 3), dtype=np.uint8)
    for y in range(VID_H):
        r = (y / VID_H)
        f[y] = [int(BG_TOP[i]*(1-r) + BG_BOT[i]*r) for i in range(3)]
    return f

BASE = make_base()

# ── Screenshot loader ─────────────────────────────────────────────────────────
_cache = {}
def load_ss(name):
    if name in _cache:
        return _cache[name]
    p = os.path.join(SCREENSHOTS, name)
    img = cv2.imread(p)
    if img is None:
        img = np.full((PH_H*2, PH_W*2, 3), 40, dtype=np.uint8)
        txt(img, name[:20], 20, PH_H, 0.6, C_WHITE)
    _cache[name] = img
    return img

# ── Phone frame renderer ──────────────────────────────────────────────────────
def draw_phone(canvas, ss_name, cx, cy, scale=1.0, alpha=1.0):
    img = load_ss(ss_name)
    src_h, src_w = img.shape[:2]

    # target screen dims
    sw = int(390 * 2 * scale)
    sh = int(min(src_h, src_w * src_h // src_w) * scale)
    sh = int(sw * src_h / src_w)

    resized = cv2.resize(img, (sw, sh))

    pad   = int(22 * scale)
    notch = int(32 * scale)
    bot   = int(28 * scale)
    rad   = int(52 * scale)

    bx1 = cx - sw//2 - pad
    by1 = cy - sh//2 - pad - notch
    bx2 = cx + sw//2 + pad
    by2 = cy + sh//2 + pad + bot

    # clamp to canvas
    if bx1 < 0 or by1 < 0 or bx2 > VID_W or by2 > VID_H:
        return

    # shadow
    shad = canvas.copy()
    cv2.rectangle(shad, (bx1+8, by1+14), (bx2+8, by2+14), (4,4,8), -1)
    cv2.addWeighted(shad, 0.55, canvas, 0.45, 0, canvas)

    # body
    cv2.rectangle(canvas, (bx1, by1), (bx2, by2), (42,36,58), -1)
    cv2.rectangle(canvas, (bx1, by1), (bx2, by2), (72,64,100), 3)

    # screen
    sx1 = cx - sw//2;  sy1 = cy - sh//2
    sx2 = cx + sw//2;  sy2 = cy + sh//2
    if alpha >= 1.0:
        canvas[sy1:sy2, sx1:sx2] = resized
    else:
        roi = canvas[sy1:sy2, sx1:sx2].astype(np.float32)
        blended = roi*(1-alpha) + resized.astype(np.float32)*alpha
        canvas[sy1:sy2, sx1:sx2] = blended.astype(np.uint8)

    # notch bar
    nw = int(110*scale)
    nx1 = cx - nw//2;  ny1 = by1 + pad - 4
    cv2.rectangle(canvas, (nx1, ny1), (nx1+nw, ny1+notch-4), (22,18,30), -1)

    # home indicator
    hy = by2 - bot + 8
    cv2.line(canvas, (cx-int(55*scale), hy), (cx+int(55*scale), hy),
             (90, 80, 120), max(1, int(6*scale)))

# ── Info card on right/left ───────────────────────────────────────────────────
def draw_info_card(canvas, header, bullets, x, y, width=560, accent=C_PRIMARY,
                   fade=1.0):
    if fade <= 0:
        return
    overlay = canvas.copy()
    bh = 52 + len(bullets)*50 + 24
    cv2.rectangle(overlay, (x-16, y-16), (x+width, y+bh), C_DARK_CARD, -1)
    cv2.rectangle(overlay, (x-16, y-16), (x+width, y+bh), accent, 2)
    # header strip
    cv2.rectangle(overlay, (x-16, y-16), (x+width, y+28), accent, -1)
    cv2.addWeighted(overlay, fade, canvas, 1-fade, 0, canvas)

    if fade > 0.05:
        txt(canvas, header, x, y+16, 0.75, C_WHITE, 2, bold=True)
        by = y + 60
        for b in bullets:
            cv2.circle(canvas, (x+8, by-10), 5, accent, -1)
            txt(canvas, b, x+22, by, 0.62, C_WHITE, 1)
            by += 48

# ── Progress bar ──────────────────────────────────────────────────────────────
SECTIONS = [
    ("Home Screen",     "home"),
    ("Doctor Detail",   "detail"),
    ("Book Appt",       "booking"),
    ("Payment",         "payment"),
    ("Confirmation",    "confirm"),
    ("My Bookings",     "bookings"),
]

def draw_progress(canvas, active_idx, sub_progress=0.0):
    n   = len(SECTIONS)
    bw  = 130
    gap = 12
    total_w = n*bw + (n-1)*gap
    sx  = (VID_W - total_w)//2
    y   = VID_H - 44

    for i, (label, key) in enumerate(SECTIONS):
        color = SECTION_COLORS[key]
        x1 = sx + i*(bw+gap)
        x2 = x1 + bw
        mid = (x1+x2)//2

        if i < active_idx:
            cv2.rectangle(canvas, (x1, y), (x2, y+20), color, -1)
        elif i == active_idx:
            done_w = int(bw * sub_progress)
            cv2.rectangle(canvas, (x1, y), (x1+done_w, y+20), color, -1)
            cv2.rectangle(canvas, (x1+done_w, y), (x2, y+20), (55,50,70), -1)
        else:
            cv2.rectangle(canvas, (x1, y), (x2, y+20), (40,36,54), -1)

        lc = C_WHITE if i <= active_idx else C_GRAY
        txt(canvas, label, mid, y-6, 0.48, lc, 1, anchor="center")

# ── Easing ────────────────────────────────────────────────────────────────────
def ease_out(t):
    return 1 - (1-t)**3

def ease_in_out(t):
    return t*t*(3 - 2*t)

# ── Transition helpers ────────────────────────────────────────────────────────
def frames_fade_in(frame, n=18):
    black = np.zeros_like(frame)
    for i in range(n):
        yield cv2.addWeighted(black, 1-i/n, frame, i/n, 0)

def frames_fade_out(frame, n=18):
    black = np.zeros_like(frame)
    for i in range(n):
        yield cv2.addWeighted(frame, 1-i/n, black, i/n, 0)

def frames_crossfade(a, b, n=22):
    for i in range(n):
        t = ease_in_out(i/(n-1))
        yield cv2.addWeighted(a, 1-t, b, t, 0)

def frames_hold(frame, secs):
    for _ in range(int(secs*FPS)):
        yield frame

# ── Build a section ───────────────────────────────────────────────────────────
def section_frames(ss_name, section_idx, total_sections,
                   section_title, section_subtitle,
                   header, bullets,
                   hold_secs=3.5, phone_scale=1.0,
                   accent=C_PRIMARY, phone_side="right"):
    """Yield all frames for one screen section."""
    frames_total = int((hold_secs + 1.5) * FPS)
    sub_steps    = frames_total

    phone_x = int(VID_W * 0.30) if phone_side == "left" else int(VID_W * 0.68)
    info_x  = int(VID_W * 0.53) if phone_side == "left" else int(VID_W * 0.04)
    info_y  = int(VID_H * 0.18)
    phone_y = VID_H // 2

    SLIDE_IN  = 28
    FADE_INFO = 20
    HOLD_F    = int(hold_secs * FPS)

    # ── slide in phone
    start_x = VID_W + 500 if phone_side == "right" else -500
    for i in range(SLIDE_IN):
        t  = ease_out(i / (SLIDE_IN-1))
        cx = int(start_x + (phone_x - start_x)*t)
        f  = BASE.copy()
        draw_phone(f, ss_name, cx, phone_y, scale=phone_scale)
        draw_progress(f, section_idx, i/SLIDE_IN * 0.3)
        yield f

    # ── fade in info card
    phone_frame = BASE.copy()
    draw_phone(phone_frame, ss_name, phone_x, phone_y, scale=phone_scale)

    for i in range(FADE_INFO):
        fade = ease_in_out(i / (FADE_INFO-1))
        f = phone_frame.copy()
        draw_info_card(f, header, bullets, info_x, info_y,
                       accent=accent, fade=fade)
        # section label top-left
        txt_shadow(f, section_title, 60, 72, 1.4, C_WHITE, 2, bold=True)
        txt(f, section_subtitle, 60, 108, 0.70, C_GRAY, 1)
        draw_progress(f, section_idx, 0.3 + (i/FADE_INFO)*0.4)
        yield f

    # ── hold
    full_frame = phone_frame.copy()
    draw_info_card(full_frame, header, bullets, info_x, info_y,
                   accent=accent, fade=1.0)
    txt_shadow(full_frame, section_title, 60, 72, 1.4, C_WHITE, 2, bold=True)
    txt(full_frame, section_subtitle, 60, 108, 0.70, C_GRAY, 1)

    for i in range(HOLD_F):
        f = full_frame.copy()
        draw_progress(f, section_idx, 0.7 + (i/HOLD_F)*0.3)
        yield f


# ── Intro title card ──────────────────────────────────────────────────────────
def intro_frames():
    TOTAL = int(3.5 * FPS)
    for i in range(TOTAL):
        t = i / (TOTAL-1)
        f = BASE.copy()

        # pulsing accent bar
        bar_h = int(6 + 4*np.sin(t*np.pi*2))
        cv2.rectangle(f, (0, VID_H//2 - 120 - bar_h),
                      (VID_W, VID_H//2 - 120), C_PRIMARY, -1)

        # App name
        txt_shadow(f, "DocBook", VID_W//2, VID_H//2 - 60,
                   3.5, C_WHITE, 4, anchor="center", bold=True)

        # Tagline
        txt(f, "Doctor Booking & Appointment App",
            VID_W//2, VID_H//2 + 10, 1.1, C_GRAY, 1, anchor="center")

        # Sub-tagline
        txt(f, "Find Doctors  |  Book Appointments  |  Pay Securely  |  Manage Bookings",
            VID_W//2, VID_H//2 + 60, 0.70, C_ACCENT_LINE, 1, anchor="center")

        # Bottom bar
        cv2.rectangle(f, (0, VID_H-55), (VID_W, VID_H), C_PRIMARY, -1)
        txt(f, "github.com/ratnapriyaaccenture/doctor_booking_app",
            VID_W//2, VID_H-18, 0.72, C_WHITE, 1, anchor="center")

        # Feature count chips
        chips = ["37 Doctors","8 Cities","4 Payment Methods","6 Screens"]
        chip_y = VID_H//2 + 120
        chip_x = VID_W//2 - 520
        for chip in chips:
            (tw,_),_ = cv2.getTextSize(chip, FONT, 0.65, 1)
            cv2.rectangle(f, (chip_x-14, chip_y-28),
                          (chip_x+tw+14, chip_y+10), C_DARK_CARD, -1)
            cv2.rectangle(f, (chip_x-14, chip_y-28),
                          (chip_x+tw+14, chip_y+10), C_PRIMARY, 2)
            txt(f, chip, chip_x, chip_y, 0.65, C_WHITE, 1)
            chip_x += tw + 48

        alpha = min(1.0, t*4) * min(1.0, (1-t)*4)
        cv2.addWeighted(f, alpha, BASE, 1-alpha, 0, f)
        yield f


# ── Section title card ────────────────────────────────────────────────────────
def section_title_frames(num, title, subtitle, accent):
    TOTAL = int(1.8 * FPS)
    for i in range(TOTAL):
        t = ease_in_out(i/(TOTAL-1))
        f = BASE.copy()
        cv2.rectangle(f, (0,0), (8, VID_H), accent, -1)
        cv2.rectangle(f, (0, VID_H-55), (VID_W, VID_H), accent, -1)
        txt(f, f"DocBook", VID_W-220, 52, 1.0, C_WHITE, 1, bold=True)
        txt_shadow(f, f"{num}. {title}", VID_W//2, VID_H//2-30,
                   2.0, C_WHITE, 3, anchor="center", bold=True)
        txt(f, subtitle, VID_W//2, VID_H//2+40,
            0.85, C_GRAY, 1, anchor="center")
        cv2.addWeighted(f, t, BASE, 1-t, 0, f)
        yield f


# ── Outro card ────────────────────────────────────────────────────────────────
def outro_frames():
    TOTAL = int(3.0 * FPS)
    for i in range(TOTAL):
        t = ease_in_out(i/(TOTAL-1))
        f = BASE.copy()
        cv2.rectangle(f, (0,0), (8, VID_H), C_PRIMARY, -1)
        cv2.rectangle(f, (0, VID_H-55), (VID_W, VID_H), C_PRIMARY, -1)

        txt_shadow(f, "DocBook", VID_W//2, VID_H//2-100,
                   3.2, C_WHITE, 4, anchor="center", bold=True)
        txt(f, "Doctor Booking & Appointment App",
            VID_W//2, VID_H//2-28, 1.05, C_GRAY, 1, anchor="center")

        txt(f, "Flutter  |  Material Design 3  |  37 Doctors  |  8 Cities",
            VID_W//2, VID_H//2+36, 0.72, C_ACCENT_LINE, 1, anchor="center")

        txt(f, "github.com/ratnapriyaaccenture/doctor_booking_app",
            VID_W//2, VID_H//2+90, 0.78, C_PRIMARY, 1, anchor="center")

        txt(f, "github.com/ratnapriyaaccenture/doctor_booking_app",
            VID_W-16, VID_H-18, 0.68, C_WHITE, 1, anchor="right")

        cv2.addWeighted(f, t, BASE, 1-t, 0, f)
        yield f


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — stitch everything together
# ══════════════════════════════════════════════════════════════════════════════

SECTIONS_DATA = [
    # (idx, num, title, subtitle, accent, screens)
    # each screen: (ss_name, header, bullets, hold_secs, phone_side)
    (0, "01", "Home Screen", "Doctor Discovery & Search", C_PRIMARY, [
        ("home_screen.png", "Doctor Discovery", [
            "37 doctors across 8 Indian cities",
            "Search by name, specialty or hospital",
            "Filter by City — 8 cities available",
            "Filter by Specialty — 8 specialties",
            "Filter by Star Rating (All / 3+ / 4+ / 4.5+)",
            "Live result count updates instantly",
            "Tap any card to view full profile",
        ], 4.0, "right"),
        ("home_filtered.png", "Filtered Results", [
            "Mumbai + Cardiologist + 4.5+ applied",
            "5 matching doctors shown",
            "Clear All resets all active filters",
            "Doctor cards show fee, rating & hospital",
        ], 3.0, "left"),
    ]),

    (1, "02", "Doctor Detail", "Full Profile — Qualifications, Slots & Booking CTA", (176,78,16), [
        ("doctor_detail.png", "Doctor Profile", [
            "Gradient header with colour-coded avatar",
            "Name, specialty & qualifications (MBBS, MD, DM)",
            "Star rating (4.4–4.9) + patient review count",
            "Stats: Experience / Patients / Consult Fee",
            "Detailed About bio & expertise",
            "Interactive available days chips",
            "Time slot grid (4–6 slots per day)",
            "In-Person / Video Call / Phone Call types",
            "Book Appointment CTA button",
        ], 5.0, "right"),
    ]),

    (2, "03", "Appointment Booking", "Choose Type, Date & Time — Proceed to Payment", C_TEAL, [
        ("booking_screen.png", "Booking Screen", [
            "Doctor summary bar for quick reference",
            "In-Person = 100%  |  Video = 80%  |  Phone = 60%",
            "Dynamic fee updates on type selection",
            "Horizontal date picker — next 14 available dates",
            "Time slot grid appears after date is chosen",
            "Fee breakdown: Consult + 18% GST = Total",
            "Proceed button enabled only when date & time set",
        ], 5.0, "left"),
    ]),

    (3, "04", "Payment Screen", "UPI | Card | Wallet | Net Banking", C_PURPLE, [
        ("payment_upi.png", "UPI Payment", [
            "Order summary gradient card at top",
            "Custom-painted QR code (docbook@ybl)",
            "Manual UPI ID entry field",
            "Accepted: Google Pay / PhonePe / Paytm / BHIM",
        ], 3.0, "right"),
        ("payment_card.png", "Card Payment", [
            "2 pre-saved cards (Visa / Mastercard)",
            "Live gradient card preview updates as you type",
            "Card number / Holder name / Expiry / CVV",
        ], 3.0, "left"),
        ("payment_wallet.png", "Wallet Payment", [
            "Paytm  |  PhonePe  |  Google Pay  |  Amazon Pay",
            "Colour-coded brand tiles in 2x2 grid",
            "Tap to select — animated border highlight",
        ], 2.5, "right"),
        ("payment_netbanking.png", "Net Banking", [
            "SBI  |  HDFC  |  ICICI  |  Axis  |  Kotak  |  BoB",
            "Colour-coded bank logo tiles",
            "Pay button: 2-sec processing animation",
        ], 2.5, "left"),
    ]),

    (4, "05", "Booking Confirmation", "Success Animation, Summary & Navigation", C_SEC, [
        ("confirmation_screen.png", "Confirmed!", [
            "Animated scale + fade-in success checkmark",
            "Unique 8-character alphanumeric Booking ID",
            "Doctor name, specialty & hospital",
            "Appointment date & time slot",
            "Consultation type (In-Person / Video / Phone)",
            "Amount paid including 18% GST",
            "Transaction ID from payment gateway",
            "Back to Home  |  View My Bookings buttons",
        ], 5.0, "right"),
    ]),

    (5, "06", "My Bookings", "View & Manage All Appointments", C_ORANGE, [
        ("my_bookings.png", "Bookings Dashboard", [
            "All appointments in reverse-chronological order",
            "Booking ID + colour-coded status badge per card",
            "Confirmed (green) / Pending (yellow)",
            "Cancelled (red) / Completed (gray)",
            "Doctor info, date, time, type & fee shown",
        ], 3.5, "left"),
        ("my_bookings_empty.png", "Empty State", [
            "Shown when no bookings exist",
            "Friendly illustration with clear message",
            "Browse Doctors shortcut button",
        ], 2.5, "right"),
    ]),
]


def generate():
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writers = [
        cv2.VideoWriter(MP4_OUT, fourcc, FPS, (VID_W, VID_H)),
        cv2.VideoWriter(MOV_OUT, fourcc, FPS, (VID_W, VID_H)),
    ]

    def emit(frame):
        for w in writers:
            w.write(frame)

    def emit_all(gen):
        for f in gen:
            emit(f)

    print("  [Intro] Title card ...")
    emit_all(frames_fade_in(next(iter(intro_frames())), n=20))
    emit_all(intro_frames())
    last_intro = BASE.copy()

    prev = BASE.copy()

    for sec_idx, num, title, subtitle, accent, screens in SECTIONS_DATA:
        print(f"  [Section {num}] {title} ...")

        # section title card
        emit_all(frames_crossfade(prev, BASE, n=18))
        emit_all(section_title_frames(num, title, subtitle, accent))

        # each screen in this section
        for ss_name, header, bullets, hold_s, phone_side in screens:
            screen_gen = section_frames(
                ss_name, sec_idx, len(SECTIONS_DATA),
                f"{num}. {title}", subtitle,
                header, bullets,
                hold_secs=hold_s,
                phone_scale=0.82,
                accent=accent,
                phone_side=phone_side,
            )
            frames_list = list(screen_gen)
            for f in frames_list:
                emit(f)
            prev = frames_list[-1] if frames_list else BASE.copy()

    print("  [Outro] End card ...")
    emit_all(frames_crossfade(prev, BASE, n=22))
    emit_all(outro_frames())

    for w in writers:
        w.release()


if __name__ == "__main__":
    print(f"\nGenerating DocBook Full Demo Video\n  -> {MP4_OUT}\n  -> {MOV_OUT}\n")

    total_hold = sum(
        sum(s[3] for s in sec[5])
        for sec in SECTIONS_DATA
    )
    est_secs = 3.5 + len(SECTIONS_DATA)*1.8 + total_hold + len(SECTIONS_DATA)*2.5 + 3.0
    print(f"  Estimated duration: ~{int(est_secs)} seconds\n")

    generate()

    print("\nDone!")
    for path in [MP4_OUT, MOV_OUT]:
        size_mb = os.path.getsize(path) / (1024*1024)
        print(f"  {path}  ({size_mb:.1f} MB)")
