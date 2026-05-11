# DocBook — 4K Video Recording Guide

This guide explains how to record 4K MP4 and MOV demo videos for each DocBook feature.

## Required Videos (per feature)

| Video File (MP4) | Video File (MOV) | Feature |
|---|---|---|
| `01_home_discovery.mp4` | `01_home_discovery.mov` | Doctor Search & Filter |
| `02_doctor_detail.mp4` | `02_doctor_detail.mov` | Doctor Profile |
| `03_booking_flow.mp4` | `03_booking_flow.mov` | Appointment Booking |
| `04_payment_all_methods.mp4` | `04_payment_all_methods.mov` | All 4 Payment Methods |
| `05_confirmation.mp4` | `05_confirmation.mov` | Booking Confirmation |
| `06_my_bookings.mp4` | `06_my_bookings.mov` | My Bookings Dashboard |

---

## Method 1: Android Emulator (Recommended for 4K)

### Step 1 — Set up a 4K emulator in Android Studio
```
Tools > Device Manager > Create Device
  > Category: Phone
  > Device: Pixel 6 Pro (or custom 3840x2160 resolution)
  > API: 34 (Android 14)
  > Scale: 4K
```

### Step 2 — Run the app
```bash
cd doctor_booking_app
flutter run -d emulator-5554
```

### Step 3 — Record each flow
In Android Studio Device Manager, click the **Record** button (camera icon) before each demo.

Or via ADB:
```bash
# Start recording
adb shell screenrecord --size 3840x2160 --bit-rate 40000000 /sdcard/demo.mp4

# Stop recording (Ctrl+C)
adb pull /sdcard/demo.mp4 demos/01_home_discovery.mp4
```

---

## Method 2: iOS Simulator on macOS (QuickTime MOV)

### Step 1 — Set up a 4K simulator
```bash
xcrun simctl list devices
flutter run -d "iPhone 15 Pro Max"
```

### Step 2 — Record with QuickTime
```
1. Open QuickTime Player
2. File > New Movie Recording
3. Click dropdown arrow next to record button
4. Select the iPhone Simulator as source
5. Quality: Maximum (4K)
6. Click Record
7. Perform the demo flow in Simulator
8. Stop recording → Save as .mov
```

---

## Method 3: OBS Studio (Windows / Mac / Linux)

### Setup
1. Download OBS Studio from obsproject.com
2. Add "Window Capture" source → select the Flutter app window
3. Set output resolution to 3840x2160 (4K)
4. Set bitrate to 40,000 Kbps for best quality
5. Output format: MP4 (H.264) or MOV (ProRes/H.265)

### Recording
```
1. Start OBS
2. Run: flutter run -d chrome  (for web version)
3. Set Chrome window to full screen
4. Click "Start Recording" in OBS
5. Perform the demo flow
6. Click "Stop Recording"
7. File is saved to your OBS output folder
```

---

## Demo Scripts (What to Show in Each Video)

### Video 1: Home Discovery (60 sec)
```
1. App opens on Home Screen — 37 doctors listed
2. Scroll through doctor cards (5 seconds)
3. Type "Cardio" in search bar — results filter live
4. Clear search
5. Tap "Mumbai" city filter chip — results update
6. Tap "Cardiologist" specialty chip — results filter to 5
7. Tap "4.5+" rating — narrows to top doctors
8. Tap "Clear all" — all 37 doctors shown again
9. Tap a doctor card to navigate to profile
```

### Video 2: Doctor Profile (30 sec)
```
1. Doctor Detail Screen opens with gradient header
2. Scroll down to see: stats, about bio, available days
3. Tap different day chips to show interaction
4. Review time slots grid
5. Tap "Video Call" consultation type — price updates
6. Tap "Book Appointment" button
```

### Video 3: Appointment Booking (45 sec)
```
1. Booking Screen opens with doctor summary
2. Tap "Video Call" — fee shows 80% (Rs.720)
3. Tap "Phone Call" — fee shows 60% (Rs.540)
4. Tap "In-Person" — full fee (Rs.900)
5. Scroll date picker left and right
6. Tap a date chip — time slots appear below
7. Tap a time slot — slot highlights
8. Show fee breakdown: consultation + GST = total
9. Tap "Proceed to Payment"
```

### Video 4: All 4 Payment Methods (90 sec)
```
1. Payment Screen opens — Order Summary shows
2. UPI tab (default):
   - Show QR code
   - Type UPI ID in field
3. Tap "Card" tab:
   - Show saved Visa card
   - Tap to select it (checkmark appears)
   - Type in card number field — live preview updates
4. Tap "Wallet" tab:
   - Show 4 wallets
   - Tap each to select
5. Tap "Net Banking" tab:
   - Show 6 banks
   - Tap SBI
6. Go back to UPI, tap "Pay Rs.1,062 Securely"
7. Processing animation (spinner) for 2 seconds
```

### Video 5: Confirmation (20 sec)
```
1. Confirmation screen appears with success animation
2. Read out booking ID
3. Scroll through full booking details
4. Tap "View My Bookings"
```

### Video 6: My Bookings (30 sec)
```
1. My Bookings screen shows list of bookings
2. Scroll through booking cards
3. Show status badges: Confirmed (green)
4. Show empty state (if bookings list is empty)
5. Tap "Browse Doctors" from empty state
```

---

## Exporting Final Videos

### MP4 (for Android / Windows sharing)
- Format: H.264 or H.265
- Resolution: 3840x2160 (4K UHD)
- Frame Rate: 60fps
- Bitrate: 40 Mbps

### MOV (for iOS / macOS / QuickTime)
- Format: ProRes 422 or H.264
- Resolution: 3840x2160 (4K UHD)
- Frame Rate: 60fps
- Bitrate: 40-80 Mbps

Use HandBrake (free) to convert between formats if needed.

---

## File Naming Convention
```
demos/
├── 01_home_discovery.mp4
├── 01_home_discovery.mov
├── 02_doctor_detail.mp4
├── 02_doctor_detail.mov
├── 03_booking_flow.mp4
├── 03_booking_flow.mov
├── 04_payment_all_methods.mp4
├── 04_payment_all_methods.mov
├── 05_confirmation.mp4
├── 05_confirmation.mov
├── 06_my_bookings.mp4
└── 06_my_bookings.mov
```
