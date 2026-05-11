# -*- coding: utf-8 -*-
"""
DocBook - Doctor Booking App
Generates MP4 & MOV demo videos for every feature using OpenCV.
Run: python generate_videos.py
"""

import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "Video"
SCREENSHOTS = "assets/screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

# Video settings
FPS        = 30
VID_W      = 1920
VID_H      = 1080
PHONE_W    = 390
PHONE_H    = 844

# Brand colors
C_PRIMARY      = (232, 115, 26)    # BGR
C_PRIMARY_RGB  = (26, 115, 232)
C_SECONDARY    = (83, 168, 52)
C_BG_DARK      = (22, 22, 32)
C_BG_DARKER    = (12, 12, 20)
C_WHITE        = (255, 255, 255)
C_GRAY         = (160, 160, 180)
C_GOLD         = (4, 188, 251)     # BGR for star gold


def load_screenshot(name):
    """Load a screenshot and resize to phone dimensions."""
    path = os.path.join(SCREENSHOTS, name)
    img = cv2.imread(path)
    if img is None:
        img = np.zeros((PHONE_H * 2, PHONE_W * 2, 3), dtype=np.uint8)
        img[:] = (40, 40, 60)
        cv2.putText(img, name, (20, img.shape[0] // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, C_WHITE, 2)
    img = cv2.resize(img, (PHONE_W * 2, PHONE_H * 2))
    return img


def make_base_frame():
    """Create a dark gradient base frame."""
    frame = np.zeros((VID_H, VID_W, 3), dtype=np.uint8)
    for y in range(VID_H):
        ratio = y / VID_H
        r = int(C_BG_DARK[0] * (1 - ratio) + C_BG_DARKER[0] * ratio)
        g = int(C_BG_DARK[1] * (1 - ratio) + C_BG_DARKER[1] * ratio)
        b = int(C_BG_DARK[2] * (1 - ratio) + C_BG_DARKER[2] * ratio)
        frame[y, :] = (r, g, b)
    return frame


def draw_phone_frame(canvas, phone_img, x_center, y_center):
    """Draw a phone mockup with the screenshot inside."""
    pw = PHONE_W * 2
    ph = PHONE_H * 2
    frame_pad = 18
    radius = 60

    x1 = x_center - pw // 2 - frame_pad
    y1 = y_center - ph // 2 - frame_pad
    x2 = x_center + pw // 2 + frame_pad
    y2 = y_center + ph // 2 + frame_pad

    # Shadow
    shadow = canvas.copy()
    cv2.rectangle(shadow, (x1 + 8, y1 + 12), (x2 + 8, y2 + 12), (5, 5, 10), -1)
    cv2.addWeighted(shadow, 0.5, canvas, 0.5, 0, canvas)

    # Phone body
    cv2.rectangle(canvas, (x1, y1), (x2, y2), (35, 35, 50), -1)
    cv2.rectangle(canvas, (x1, y1), (x2, y2), (60, 60, 90), 3)

    # Screen area
    sx1 = x_center - pw // 2
    sy1 = y_center - ph // 2
    sx2 = x_center + pw // 2
    sy2 = y_center + ph // 2

    if (sx1 >= 0 and sy1 >= 0 and sx2 <= VID_W and sy2 <= VID_H
            and phone_img is not None):
        canvas[sy1:sy2, sx1:sx2] = phone_img

    # Notch
    notch_w = 120
    notch_h = 28
    nx1 = x_center - notch_w // 2
    ny1 = y1 + frame_pad - 4
    cv2.rectangle(canvas, (nx1, ny1), (nx1 + notch_w, ny1 + notch_h), (20, 20, 30), -1)
    # Home indicator
    hi_y = y2 - frame_pad - 8
    cv2.line(canvas, (x_center - 60, hi_y), (x_center + 60, hi_y), (80, 80, 110), 6)


def put_text_cv(canvas, text, x, y, font_scale=1.0, color=C_WHITE,
                thickness=2, align="left"):
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    if align == "center":
        x = x - tw // 2
    elif align == "right":
        x = x - tw
    cv2.putText(canvas, text, (x, y), font, font_scale, color, thickness,
                cv2.LINE_AA)


def draw_title_card(canvas, title, subtitle, accent_color=C_PRIMARY):
    """Draw a full-screen title card."""
    h, w = canvas.shape[:2]
    # Accent left bar
    cv2.rectangle(canvas, (0, 0), (10, h), accent_color, -1)
    # DocBook logo top right
    put_text_cv(canvas, "DocBook", w - 220, 60, 1.2, C_WHITE, 2)
    # Main title (multi-line split on \n)
    lines = title.split("\n")
    y = h // 2 - (len(lines) - 1) * 50
    for line in lines:
        put_text_cv(canvas, line, w // 2, y, 2.2, C_WHITE, 3, align="center")
        y += 90
    # Subtitle
    if subtitle:
        put_text_cv(canvas, subtitle, w // 2, y + 30, 0.9,
                    C_GRAY, 1, align="center")
    # Bottom bar
    cv2.rectangle(canvas, (0, h - 60), (w, h), accent_color, -1)
    put_text_cv(canvas, "DocBook - Doctor Booking & Appointment App",
                40, h - 20, 0.7, C_WHITE, 1)


def draw_info_panel(canvas, lines, x, y_start, width=520,
                    header=None, accent=C_PRIMARY):
    """Draw an info panel with bullet lines on the right side."""
    bg = canvas.copy()
    cv2.rectangle(bg, (x - 20, y_start - 20),
                  (x + width, y_start + len(lines) * 52 + 60), (20, 20, 35), -1)
    cv2.addWeighted(bg, 0.85, canvas, 0.15, 0, canvas)
    cv2.rectangle(canvas, (x - 20, y_start - 20),
                  (x + width, y_start + len(lines) * 52 + 60),
                  accent, 2)
    if header:
        cv2.rectangle(canvas, (x - 20, y_start - 20),
                      (x + width, y_start + 14), accent, -1)
        put_text_cv(canvas, header, x, y_start + 8, 0.75, C_WHITE, 2)
        y_start += 40

    for line in lines:
        cv2.circle(canvas, (x + 8, y_start - 8), 5, accent, -1)
        put_text_cv(canvas, line, x + 24, y_start, 0.65, C_WHITE, 1)
        y_start += 48


def crossfade(frame_a, frame_b, steps=20):
    """Yield crossfade frames between two images."""
    for i in range(steps):
        alpha = i / steps
        yield cv2.addWeighted(frame_a, 1 - alpha, frame_b, alpha, 0)


def slide_in(base_frame, phone_img, from_right=True, steps=25,
             x_center=None, y_center=None):
    """Yield frames for a phone sliding in from side."""
    x_center = x_center or VID_W // 2
    y_center = y_center or VID_H // 2
    pw = PHONE_W * 2 + 36

    if from_right:
        start_x = VID_W + pw // 2
    else:
        start_x = -pw // 2

    for i in range(steps):
        t = i / (steps - 1)
        # Ease out cubic
        t = 1 - (1 - t) ** 3
        cur_x = int(start_x + (x_center - start_x) * t)
        frame = base_frame.copy()
        draw_phone_frame(frame, phone_img, cur_x, y_center)
        yield frame


def open_video_writer(path, fps=FPS, w=VID_W, h=VID_H):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".mp4":
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    else:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    return cv2.VideoWriter(path, fourcc, fps, (w, h))


def write_frames(writer, frames):
    for f in frames:
        writer.write(f)


def hold_frame(frame, seconds):
    """Yield the same frame for a number of seconds."""
    count = int(seconds * FPS)
    for _ in range(count):
        yield frame


def make_video(screens, mp4_path, mov_path,
               feature_title, feature_subtitle,
               info_panels, accent_color=C_PRIMARY):
    """
    Generic video generator.
    screens: list of (screenshot_name, panel_header, panel_lines, hold_secs)
    """
    print(f"  Generating {os.path.basename(mp4_path)} ...")
    writers = [
        open_video_writer(mp4_path),
        open_video_writer(mov_path),
    ]

    def emit(frame):
        for w in writers:
            w.write(frame)

    base = make_base_frame()

    # ── Title card (2.5 sec) ──────────────────────────────────────────────────
    title_frame = base.copy()
    draw_title_card(title_frame, feature_title, feature_subtitle, accent_color)
    for f in hold_frame(title_frame, 2.5):
        emit(f)

    prev_frame = title_frame

    # ── Each screen ───────────────────────────────────────────────────────────
    for i, (scr_name, panel_header, panel_lines, hold_secs) in enumerate(screens):
        phone_img = load_screenshot(scr_name)
        from_right = (i % 2 == 0)

        # Determine phone position
        if panel_lines:
            # Phone on left, info on right
            phone_x = int(VID_W * 0.33)
        else:
            phone_x = VID_W // 2
        phone_y = VID_H // 2

        # Build destination frame
        dest_base = base.copy()
        draw_phone_frame(dest_base, phone_img, phone_x, phone_y)
        if panel_lines:
            info_x = int(VID_W * 0.62)
            info_y = int(VID_H * 0.18)
            draw_info_panel(dest_base, panel_lines, info_x, info_y,
                            header=panel_header, accent=accent_color)

        # Slide-in animation
        for f in slide_in(base.copy(), phone_img, from_right=from_right,
                          steps=22, x_center=phone_x, y_center=phone_y):
            # Add info panel progressively (fade in)
            if panel_lines:
                pass  # just show phone slide first
            emit(f)

        # Fade in info panel
        phone_only = base.copy()
        draw_phone_frame(phone_only, phone_img, phone_x, phone_y)
        if panel_lines:
            for step in range(15):
                alpha = step / 14
                blend = cv2.addWeighted(phone_only, 1 - alpha * 0.0,
                                        dest_base, alpha, 0)
                # Actually just show dest frame with increasing alpha overlay
                f = phone_only.copy()
                overlay = dest_base.copy()
                cv2.addWeighted(overlay, alpha, f, 1 - alpha, 0, f)
                emit(f)

        # Hold
        for f in hold_frame(dest_base, hold_secs):
            emit(f)

        prev_frame = dest_base

    # ── Outro (1.5 sec) ───────────────────────────────────────────────────────
    outro = base.copy()
    cv2.rectangle(outro, (0, 0), (10, VID_H), accent_color, -1)
    put_text_cv(outro, "DocBook", VID_W // 2, VID_H // 2 - 60,
                2.5, C_WHITE, 3, align="center")
    put_text_cv(outro, "Doctor Booking & Appointment App",
                VID_W // 2, VID_H // 2 + 10, 0.9, C_GRAY, 1, align="center")
    put_text_cv(outro, "github.com/ratnapriyaaccenture/doctor_booking_app",
                VID_W // 2, VID_H // 2 + 60, 0.7,
                accent_color, 1, align="center")

    for f in crossfade(prev_frame, outro, steps=20):
        emit(f)
    for f in hold_frame(outro, 1.5):
        emit(f)

    for w in writers:
        w.release()

    for path in [mp4_path, mov_path]:
        size_kb = os.path.getsize(path) // 1024
        print(f"    [OK] {os.path.basename(path)}  ({size_kb:,} KB)")


# ══════════════════════════════════════════════════════════════════════════════

def video_01_home():
    make_video(
        screens=[
            ("home_screen.png",
             "Home Screen",
             ["Browse 37 doctors", "Search by name/specialty",
              "Filter by city", "Filter by specialty",
              "Filter by star rating", "Tap card to view profile"],
             3.5),
            ("home_filtered.png",
             "Filtered Results",
             ["Mumbai + Cardiologist + 4.5+",
              "Live result count updates",
              "Clear All resets filters",
              "5 matching doctors shown"],
             3.0),
        ],
        mp4_path=f"{OUT_DIR}/01_home_discovery.mp4",
        mov_path=f"{OUT_DIR}/01_home_discovery.mov",
        feature_title="Doctor Discovery\n& Search",
        feature_subtitle="Home Screen - Browse, Filter & Find Specialists",
        info_panels=True,
        accent_color=C_PRIMARY,
    )


def video_02_doctor_detail():
    make_video(
        screens=[
            ("doctor_detail.png",
             "Doctor Profile",
             ["Gradient header with avatar",
              "Name, specialty & qualifications",
              "Star rating + review count",
              "Experience / Patients / Fee stats",
              "About bio & expertise",
              "Available days & time slots",
              "In-Person / Video / Phone types",
              "Book Appointment button"],
             5.0),
        ],
        mp4_path=f"{OUT_DIR}/02_doctor_detail.mp4",
        mov_path=f"{OUT_DIR}/02_doctor_detail.mov",
        feature_title="Doctor Profile\nDetail Screen",
        feature_subtitle="Full Doctor Information - Qualifications, Slots & CTA",
        info_panels=True,
        accent_color=(176, 78, 16),   # BGR for #104EA8
    )


def video_03_booking():
    make_video(
        screens=[
            ("booking_screen.png",
             "Appointment Booking",
             ["Doctor summary at top",
              "In-Person / Video / Phone types",
              "Dynamic pricing per type",
              "Horizontal 14-day date picker",
              "Time slot grid appears on date tap",
              "Consultation fee + 18% GST",
              "Proceed button enables on selection"],
             5.0),
        ],
        mp4_path=f"{OUT_DIR}/03_booking_flow.mp4",
        mov_path=f"{OUT_DIR}/03_booking_flow.mov",
        feature_title="Appointment\nBooking Screen",
        feature_subtitle="Choose Type, Date & Time - Proceed to Payment",
        info_panels=True,
        accent_color=(94, 122, 0),    # BGR for #007A5E
    )


def video_04_payment():
    make_video(
        screens=[
            ("payment_upi.png",
             "UPI Payment",
             ["Custom QR code display",
              "UPI ID entry field",
              "Google Pay / PhonePe / Paytm",
              "BHIM UPI supported"],
             2.5),
            ("payment_card.png",
             "Card Payment",
             ["2 pre-saved cards shown",
              "Live gradient card preview",
              "Card number / name / expiry / CVV",
              "Visa & Mastercard support"],
             2.5),
            ("payment_wallet.png",
             "Wallet Payment",
             ["Paytm  |  PhonePe",
              "Google Pay  |  Amazon Pay",
              "Color-coded brand tiles",
              "Instant tap to select"],
             2.5),
            ("payment_netbanking.png",
             "Net Banking",
             ["SBI  |  HDFC  |  ICICI",
              "Axis  |  Kotak  |  Bank of Baroda",
              "Colored bank logo tiles",
              "2-sec processing animation"],
             2.5),
        ],
        mp4_path=f"{OUT_DIR}/04_payment_all_methods.mp4",
        mov_path=f"{OUT_DIR}/04_payment_all_methods.mov",
        feature_title="Payment Screen\n4 Payment Methods",
        feature_subtitle="UPI  |  Card  |  Wallet  |  Net Banking",
        info_panels=True,
        accent_color=(159, 37, 95),   # BGR for #5F259F
    )


def video_05_confirmation():
    make_video(
        screens=[
            ("confirmation_screen.png",
             "Booking Confirmed",
             ["Animated success checkmark",
              "Unique 8-char Booking ID",
              "Doctor name & specialty",
              "Appointment date & time",
              "Consultation type",
              "Amount paid with GST",
              "Transaction ID shown",
              "Back to Home / My Bookings"],
             5.0),
        ],
        mp4_path=f"{OUT_DIR}/05_confirmation.mp4",
        mov_path=f"{OUT_DIR}/05_confirmation.mov",
        feature_title="Booking\nConfirmation",
        feature_subtitle="Success Animation, Booking Summary & Navigation",
        info_panels=True,
        accent_color=C_SECONDARY,
    )


def video_06_my_bookings():
    make_video(
        screens=[
            ("my_bookings.png",
             "My Bookings",
             ["All appointments listed",
              "Booking ID per card",
              "Confirmed (green badge)",
              "Pending (yellow badge)",
              "Cancelled (red badge)",
              "Completed (gray badge)",
              "Date / time / type shown",
              "Amount paid on card"],
             3.5),
            ("my_bookings_empty.png",
             "Empty State",
             ["Shown when no bookings exist",
              "Friendly illustration",
              "Browse Doctors shortcut"],
             2.5),
        ],
        mp4_path=f"{OUT_DIR}/06_my_bookings.mp4",
        mov_path=f"{OUT_DIR}/06_my_bookings.mov",
        feature_title="My Bookings\nDashboard",
        feature_subtitle="View & Manage All Appointments - Status Tracking",
        info_panels=True,
        accent_color=(0, 92, 230),    # BGR for #E65C00
    )


if __name__ == "__main__":
    print("\nGenerating DocBook demo videos -> Video/\n")
    video_01_home()
    video_02_doctor_detail()
    video_03_booking()
    video_04_payment()
    video_05_confirmation()
    video_06_my_bookings()

    print("\nAll videos saved to: " + os.path.abspath(OUT_DIR) + "/")
    files = sorted(f for f in os.listdir(OUT_DIR)
                   if f.endswith((".mp4", ".mov")))
    print(f"Total files: {len(files)}")
    total_kb = 0
    for f in files:
        kb = os.path.getsize(os.path.join(OUT_DIR, f)) // 1024
        total_kb += kb
        print(f"  {f:<40}  {kb:>6,} KB")
    print(f"\n  Total size: {total_kb // 1024:,} MB")
