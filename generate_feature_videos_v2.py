# -*- coding: utf-8 -*-
"""
DocBook - Interactive Feature Videos Generator
Generates all 6 individual feature videos with the same interactive style
as the full demo: animated cursor, tap ripples, highlights, scroll, transitions.
Run: python generate_feature_videos_v2.py
"""

import cv2
import numpy as np
import os, math

SS_DIR  = "assets/screenshots"
MP4_DIR = os.path.join("Video", "MP4")
MOV_DIR = os.path.join("Video", "MOV")
os.makedirs(MP4_DIR, exist_ok=True)
os.makedirs(MOV_DIR, exist_ok=True)

FPS   = 30
VID_W = 1920
VID_H = 1080

# Screenshot dims
SS_W, SS_H = 780, 1688
PH_SCALE   = 0.52
PH_SW      = int(SS_W * PH_SCALE)   # 405
PH_SH      = int(SS_H * PH_SCALE)   # 877
PH_CX      = 960
PH_CY      = 530
PH_X0      = PH_CX - PH_SW // 2    # 757
PH_Y0      = PH_CY - PH_SH // 2    # 91

def sc(x, y):
    """Screenshot coords → canvas coords."""
    return (int(PH_X0 + x * PH_SCALE), int(PH_Y0 + y * PH_SCALE))

# ── Colors (BGR) ──────────────────────────────────────────────────────────────
BG1  = (14,  10,  24);  BG2  = (6,   4,  12)
PRIM = (232, 115,  26); SEC  = (83,  168,  52)
PURP = (159,  37,  95); TEAL = (94,  122,   0)
ORG  = (0,   92,  230); WHT  = (255, 255, 255)
GRY  = (160, 160, 180); GOLD = (4,   188, 251)
DARK = (30,   26,  46); DET  = (176,  78,  16)

FONT  = cv2.FONT_HERSHEY_SIMPLEX
FONTB = cv2.FONT_HERSHEY_DUPLEX

# ── Easing ────────────────────────────────────────────────────────────────────
def ease_out(t):  return 1-(1-t)**3
def ease_in(t):   return t**3
def ease_io(t):   return t*t*(3-2*t)
def lerp(a,b,t):  return a+(b-a)*t

# ── Base background ───────────────────────────────────────────────────────────
def make_bg():
    f = np.zeros((VID_H, VID_W, 3), np.uint8)
    for y in range(VID_H):
        r = y / VID_H
        f[y] = [int(BG1[i]*(1-r)+BG2[i]*r) for i in range(3)]
    return f

BASE_BG = make_bg()

# ── Screenshot cache ──────────────────────────────────────────────────────────
_cache = {}
def load_ss(name):
    if name not in _cache:
        img = cv2.imread(os.path.join(SS_DIR, name))
        if img is None:
            img = np.full((SS_H, SS_W, 3), 30, np.uint8)
        _cache[name] = img
    return _cache[name]

# ── Phone frame ───────────────────────────────────────────────────────────────
def draw_phone(canvas, ss_name, scroll_y=0, alpha=1.0):
    ss = load_ss(ss_name)
    crop_y = max(0, min(scroll_y, SS_H - 1))
    cropped = ss[crop_y:, :]
    if cropped.shape[0] < SS_H:
        pad = np.zeros((SS_H - cropped.shape[0], SS_W, 3), np.uint8)
        cropped = np.vstack([cropped, pad])
    resized = cv2.resize(cropped, (PH_SW, PH_SH))

    pad_x, pad_y, notch_h, home_h = 20, 10, 28, 22
    bx1=PH_X0-pad_x; by1=PH_Y0-pad_y-notch_h
    bx2=PH_X0+PH_SW+pad_x; by2=PH_Y0+PH_SH+pad_y+home_h

    sh=canvas.copy()
    cv2.rectangle(sh,(bx1+6,by1+10),(bx2+6,by2+10),(3,2,8),-1)
    cv2.addWeighted(sh,0.5,canvas,0.5,0,canvas)
    cv2.rectangle(canvas,(bx1,by1),(bx2,by2),(44,38,62),-1)
    cv2.rectangle(canvas,(bx1,by1),(bx2,by2),(80,68,110),3)

    roi = canvas[PH_Y0:PH_Y0+PH_SH, PH_X0:PH_X0+PH_SW]
    if alpha >= 1.0:
        canvas[PH_Y0:PH_Y0+PH_SH, PH_X0:PH_X0+PH_SW] = resized
    else:
        blended = (roi.astype(np.float32)*(1-alpha) +
                   resized.astype(np.float32)*alpha).astype(np.uint8)
        canvas[PH_Y0:PH_Y0+PH_SH, PH_X0:PH_X0+PH_SW] = blended

    nw=100; nx1=PH_CX-nw//2; ny1=by1+pad_y
    cv2.rectangle(canvas,(nx1,ny1),(nx1+nw,ny1+notch_h),(22,18,32),-1)
    hy=by2-home_h+6
    cv2.line(canvas,(PH_CX-50,hy),(PH_CX+50,hy),(90,78,118),5)

# ── Text helper ───────────────────────────────────────────────────────────────
def lbl(canvas, text, x, y, scale=0.65, color=WHT, thick=1,
        bold=False, anchor="left"):
    f = FONTB if bold else FONT
    (tw,_),_ = cv2.getTextSize(text, f, scale, thick)
    if anchor=="center": x-=tw//2
    elif anchor=="right": x-=tw
    cv2.putText(canvas,text,(x,y),f,scale,(0,0,0),thick+2,cv2.LINE_AA)
    cv2.putText(canvas,text,(x,y),f,scale,color,thick,cv2.LINE_AA)

# ── UI overlays ───────────────────────────────────────────────────────────────
def caption_bar(canvas, title, sub="", accent=PRIM):
    yb = VID_H-70
    cv2.rectangle(canvas,(0,yb),(VID_W,VID_H),DARK,-1)
    cv2.rectangle(canvas,(0,yb),(6,VID_H),accent,-1)
    lbl(canvas,title,30,yb+28,0.88,WHT,2,True)
    if sub: lbl(canvas,sub,30,yb+56,0.60,GRY,1)

def section_badge(canvas, text, accent=PRIM):
    (tw,_),_ = cv2.getTextSize(text,FONTB,0.65,2)
    cv2.rectangle(canvas,(28,22),(58+tw,62),accent,-1)
    lbl(canvas,text,40,50,0.65,WHT,2,True)

def progress_bar(canvas, section_idx, sub_pct=1.0, accent=PRIM):
    labels=["Home","Detail","Booking","Payment","Confirm","Bookings"]
    n=len(labels); bw=140; gap=10
    sx=(VID_W-n*bw-(n-1)*gap)//2; y=VID_H-80; h=14
    for i,ltext in enumerate(labels):
        x1=sx+i*(bw+gap); x2=x1+bw
        mid=(x1+x2)//2
        if i<section_idx:
            cv2.rectangle(canvas,(x1,y),(x2,y+h),accent,-1)
        elif i==section_idx:
            done=int(bw*sub_pct)
            cv2.rectangle(canvas,(x1,y),(x1+done,y+h),accent,-1)
            cv2.rectangle(canvas,(x1+done,y),(x2,y+h),(50,44,68),-1)
        else:
            cv2.rectangle(canvas,(x1,y),(x2,y+h),(50,44,68),-1)
        c=WHT if i<=section_idx else GRY
        lbl(canvas,ltext,mid,y-5,0.48,c,1,anchor="center")

def highlight_box(canvas, x1,y1,x2,y2, color=GOLD, alpha=0.28, thick=2):
    ov=canvas.copy()
    cv2.rectangle(ov,(x1,y1),(x2,y2),color,-1)
    cv2.addWeighted(ov,alpha,canvas,1-alpha,0,canvas)
    cv2.rectangle(canvas,(x1,y1),(x2,y2),color,thick)

def draw_cursor(canvas, cx, cy, state="idle", t=0.0, color=WHT):
    if state=="idle":
        ov=canvas.copy()
        cv2.circle(ov,(cx,cy),16,color,-1)
        cv2.circle(ov,(cx,cy),16,DARK,2)
        cv2.circle(ov,(cx,cy),5,DARK,-1)
        cv2.addWeighted(ov,0.85,canvas,0.15,0,canvas)
    elif state=="pretap":
        sz=int(lerp(16,8,ease_io(t)))
        ov=canvas.copy()
        cv2.circle(ov,(cx,cy),sz,color,-1)
        cv2.addWeighted(ov,0.88,canvas,0.12,0,canvas)
    elif state=="tap":
        if t<0.45:
            sz=int(lerp(8,3,t/0.45))
            ov=canvas.copy()
            cv2.circle(ov,(cx,cy),sz,color,-1)
            cv2.addWeighted(ov,0.9,canvas,0.1,0,canvas)
        else:
            rt=(t-0.45)/0.55
            rsz=int(lerp(3,60,ease_out(rt)))
            al=lerp(0.7,0.0,rt)
            ov=canvas.copy()
            cv2.circle(ov,(cx,cy),rsz,color,-1)
            cv2.addWeighted(ov,al,canvas,1-al,0,canvas)

def scroll_arrow(canvas, direction="down"):
    cx=PH_X0+PH_SW-22; cy=PH_CY
    for i in range(3):
        d=i*14
        if direction=="down":
            pts=[(cx,cy+d+8),(cx-7,cy+d-4),(cx+7,cy+d-4)]
        else:
            pts=[(cx,cy-d-8),(cx-7,cy-d+4),(cx+7,cy-d+4)]
        cv2.fillPoly(canvas,[np.array(pts,np.int32)],(180,170,210))

# ── Frame builder ─────────────────────────────────────────────────────────────
def frame(ss, cap="", sub="", badge="", accent=PRIM,
          scroll_y=0, sec_idx=0, sub_pct=1.0,
          highlights=None, cur=None, cur_state="idle", cur_t=0.0):
    f = make_bg().copy()
    draw_phone(f, ss, scroll_y)
    if highlights:
        for h in highlights:
            x1,y1,x2,y2 = h[:4]
            col = h[4] if len(h)>4 else GOLD
            cx1,cy1=sc(x1,y1); cx2,cy2=sc(x2,y2)
            highlight_box(f,cx1,cy1,cx2,cy2,col)
    if cur:
        draw_cursor(f,cur[0],cur[1],cur_state,cur_t)
    if badge: section_badge(f,badge,accent)
    if cap:   caption_bar(f,cap,sub,accent)
    progress_bar(f,sec_idx,sub_pct,accent)
    return f

# ── Animation generators ──────────────────────────────────────────────────────
def hold(frm, secs):
    for _ in range(int(secs*FPS)): yield frm.copy()

def fade_in(ss, badge, accent, cap, sub, sec_idx, n=22):
    for i in range(n):
        t=ease_out(i/(n-1))
        f=make_bg().copy()
        draw_phone(f,ss,0,t)
        section_badge(f,badge,accent)
        caption_bar(f,cap,sub,accent)
        progress_bar(f,sec_idx,t*0.2,accent)
        yield f

def slide_tr(ss_from, ss_to, badge, accent, cap, sub, sec_idx,
             direction="left", n=26):
    a_img = cv2.resize(load_ss(ss_from),(PH_SW,PH_SH))
    b_img = cv2.resize(load_ss(ss_to),  (PH_SW,PH_SH))
    for i in range(n):
        t=ease_io(i/(n-1))
        f=make_bg().copy()
        off=int(PH_SW*t)
        xa = PH_X0-(off if direction=="left" else -off)
        xb = PH_X0+(PH_SW-off if direction=="left" else -(PH_SW-off))
        for xp,img in [(xa,a_img),(xb,b_img)]:
            xs=max(0,xp); xe=min(VID_W,xp+PH_SW)
            ixs=xs-xp; ixe=ixs+(xe-xs)
            if xe>xs and ixe>ixs:
                f[PH_Y0:PH_Y0+PH_SH, xs:xe]=img[:,ixs:ixe]
        pad_x,pad_y,notch_h,home_h=20,10,28,22
        bx1=PH_X0-pad_x; by1=PH_Y0-pad_y-notch_h
        bx2=PH_X0+PH_SW+pad_x; by2=PH_Y0+PH_SH+pad_y+home_h
        cv2.rectangle(f,(bx1,by1),(bx2,by2),(80,68,110),3)
        section_badge(f,badge,accent)
        caption_bar(f,cap,sub,accent)
        progress_bar(f,sec_idx,0.5,accent)
        yield f

def move_cur(ss, start, end, badge, accent, cap, sub, sec_idx,
             scroll_y=0, highlights=None, n=22):
    for i in range(n):
        t=ease_io(i/(n-1))
        cx=int(lerp(start[0],end[0],t))
        cy=int(lerp(start[1],end[1],t))
        yield frame(ss,cap,sub,badge,accent,scroll_y,sec_idx,
                    0.5+(i/n)*0.3,highlights,(cx,cy),"idle")

def tap_cur(ss, pos, badge, accent, cap, sub, sec_idx,
            scroll_y=0, highlights=None, n=18):
    for i in range(n):
        t=i/(n-1)
        st="pretap" if t<0.4 else "tap"
        yield frame(ss,cap,sub,badge,accent,scroll_y,sec_idx,
                    0.8,highlights,pos,st,t)

def scroll_anim(ss, y0, y1, badge, accent, cap, sub, sec_idx, n=26):
    for i in range(n):
        t=ease_io(i/(n-1))
        sy=int(lerp(y0,y1,t))
        f=make_bg().copy()
        draw_phone(f,ss,sy)
        scroll_arrow(f,"down" if y1>y0 else "up")
        section_badge(f,badge,accent)
        caption_bar(f,cap,sub,accent)
        progress_bar(f,sec_idx,0.6,accent)
        yield f

def title_card(num, title, sub, accent, n=None):
    total=int(2.0*FPS) if n is None else n
    for i in range(total):
        t=ease_io(i/total)
        f=make_bg().copy()
        cv2.rectangle(f,(0,0),(8,VID_H),accent,-1)
        cv2.rectangle(f,(0,VID_H-52),(VID_W,VID_H),accent,-1)
        lbl(f,"DocBook",VID_W-200,46,0.95,WHT,1,True)
        lbl(f,f"{num}",VID_W//2,VID_H//2-70,2.5,accent,4,True,"center")
        lbl(f,title,VID_W//2,VID_H//2,2.0,WHT,3,True,"center")
        lbl(f,sub,VID_W//2,VID_H//2+52,0.88,GRY,1,False,"center")
        lbl(f,"github.com/ratnapriyaaccenture/doctor_booking_app",
            VID_W//2,VID_H-18,0.65,WHT,1,False,"center")
        cv2.addWeighted(f,min(1.0,t*2)*min(1.0,(1-t/total)*6),
                        make_bg(),1-min(1.0,t*2)*min(1.0,(1-t/total)*6),0,f)
        yield f

def outro_card(accent=PRIM, n=None):
    total=int(2.5*FPS) if n is None else n
    for i in range(total):
        t=ease_io(i/total)
        f=make_bg().copy()
        cv2.rectangle(f,(0,0),(8,VID_H),accent,-1)
        cv2.rectangle(f,(0,VID_H-52),(VID_W,VID_H),accent,-1)
        lbl(f,"DocBook",VID_W//2,VID_H//2-50,2.8,WHT,4,True,"center")
        lbl(f,"Doctor Booking & Appointment App",
            VID_W//2,VID_H//2+14,0.95,GRY,1,False,"center")
        lbl(f,"github.com/ratnapriyaaccenture/doctor_booking_app",
            VID_W//2,VID_H//2+62,0.82,accent,1,False,"center")
        lbl(f,"github.com/ratnapriyaaccenture/doctor_booking_app",
            VID_W-16,VID_H-18,0.62,WHT,1,False,"right")
        cv2.addWeighted(f,t,make_bg(),1-t,0,f)
        yield f

# ── Writer helper ─────────────────────────────────────────────────────────────
def write_video(mp4_path, mov_path, generators):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    ws = [cv2.VideoWriter(mp4_path,fourcc,FPS,(VID_W,VID_H)),
          cv2.VideoWriter(mov_path,fourcc,FPS,(VID_W,VID_H))]
    total=0
    for gen in generators:
        for frm in gen:
            for w in ws: w.write(frm)
            total+=1
    for w in ws: w.release()
    dur=total/FPS
    for p in [mp4_path,mov_path]:
        mb=os.path.getsize(p)/1024/1024
        print(f"    {os.path.basename(p)}  {dur:.0f}s  ({mb:.1f} MB)")

# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 1 — HOME SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def make_v01():
    print("  [01] Home Screen — Doctor Discovery & Search")
    A="PRIM"; SS="home_screen.png"; SSF="home_filtered.png"
    BD="01 Home Screen"; AC=PRIM; SI=0
    search_c=sc(390,294); clear_c=sc(738,294)
    mumbai_c=sc(83,416); cardio_c=sc(105,528)
    rating_c=sc(484,592); clearall_c=sc(650,585)
    card_c=sc(390,778)

    def gen():
        yield from title_card("01","Home Screen","Doctor Discovery  |  Search  |  Filters",AC)
        yield from fade_in(SS,BD,AC,"Home Screen — 37 doctors available",
                           "Browse all doctors across 8 Indian cities",SI)
        ref=frame(SS,"Home Screen — 37 doctors available",
                  "Doctor cards: name, specialty, rating, hospital, fee",BD,AC,sec_idx=SI)
        yield from hold(ref,1.2)

        # Search bar
        yield from move_cur(SS,(PH_CX,PH_CY+200),search_c,BD,AC,
            "Search Bar — find by name, specialty or hospital",
            "Real-time filtering as you type",SI,n=22)
        yield from tap_cur(SS,search_c,BD,AC,
            "Tapping Search Bar","Typing to filter doctors...",SI,
            highlights=[(20,256,760,332,PRIM)],n=16)
        yield from slide_tr(SS,SSF,BD,AC,
            "Search: typing 'Cardiologist'",
            "Results filter live — showing 5 matching doctors",SI,"left")
        ref2=frame(SSF,"5 doctors found — live search active",
                   "Search matches name, specialty and hospital",BD,AC,sec_idx=SI)
        yield from hold(ref2,1.5)

        # Clear search
        yield from move_cur(SSF,search_c,clear_c,BD,AC,
            "Clear button — tap X to reset search","",SI,n=16)
        yield from tap_cur(SSF,clear_c,BD,AC,
            "Clearing search","Returning to full 37-doctor list",SI,
            highlights=[(700,256,760,332,PRIM)],n=14)
        yield from slide_tr(SSF,SS,BD,AC,
            "All 37 doctors restored","Full list visible again",SI,"right")

        # City filter
        yield from move_cur(SS,(PH_CX,PH_CY),mumbai_c,BD,AC,
            "City Filter — 8 cities available",
            "Tap a city chip to filter by location",SI,n=22)
        yield from tap_cur(SS,mumbai_c,BD,AC,
            "Mumbai selected","Showing doctors in Mumbai only",SI,
            highlights=[(36,390,136,442,PRIM)],n=16)
        yield from hold(frame(SS,"Mumbai filter active — 5 doctors",
            "City chip highlighted in blue",BD,AC,
            highlights=[(36,390,136,442,PRIM)],sec_idx=SI),1.2)

        # Specialty filter
        yield from move_cur(SS,mumbai_c,cardio_c,BD,AC,
            "Specialty Filter — 8 specialties available",
            "Stack with city filter for narrower results",SI,n=20)
        yield from tap_cur(SS,cardio_c,BD,AC,
            "Cardiologist selected","Mumbai + Cardiologist combined",SI,
            highlights=[(36,502,178,554,SEC)],n=16)
        yield from hold(frame(SS,"Mumbai + Cardiologist active",
            "Filters stack — results narrow automatically",BD,AC,
            highlights=[(36,390,136,442,PRIM),(36,502,178,554,SEC)],sec_idx=SI),1.2)

        # Rating filter
        yield from move_cur(SS,cardio_c,rating_c,BD,AC,
            "Rating Filter — All / 3★+ / 3.5★+ / 4★+ / 4.5★+",
            "Choose minimum star rating",SI,n=20)
        yield from tap_cur(SS,rating_c,BD,AC,
            "4.5★+ selected","Top-rated doctors only",SI,
            highlights=[(460,566,514,618,GOLD)],n=16)
        yield from slide_tr(SS,SSF,BD,AC,
            "Mumbai + Cardiologist + 4.5★ — 5 doctors shown",
            "All three filters active simultaneously",SI,"left")
        yield from hold(frame(SSF,"Filtered Results — top-rated cardiologists in Mumbai",
            "Doctor cards: name, specialty, rating, hospital, consultation fee",
            BD,AC,sec_idx=SI),1.8)

        # Clear all
        yield from move_cur(SSF,rating_c,clearall_c,BD,AC,
            "Clear All Filters","One tap resets every active filter",SI,n=18)
        yield from tap_cur(SSF,clearall_c,BD,AC,
            "All filters cleared","Back to 37 doctors",SI,
            highlights=[(600,566,740,618,PRIM)],n=14)
        yield from slide_tr(SSF,SS,BD,AC,
            "Full list restored — 37 doctors","All filters reset",SI,"right")

        # Tap doctor card
        yield from move_cur(SS,(PH_CX,PH_CY),card_c,BD,AC,
            "Doctor Card — tap to open full profile",
            "Shows name, specialty, experience, rating, hospital & fee",SI,n=22)
        yield from tap_cur(SS,card_c,BD,AC,
            "Opening Doctor Profile","Navigating to Doctor Detail Screen →",SI,
            highlights=[(20,680,760,876,PRIM)],n=18)
        yield from outro_card(AC)

    write_video(f"{MP4_DIR}/01_home_discovery.mp4",
                f"{MOV_DIR}/01_home_discovery.mov", [gen()])


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 2 — DOCTOR DETAIL
# ══════════════════════════════════════════════════════════════════════════════
def make_v02():
    print("  [02] Doctor Detail Screen")
    SS="doctor_detail.png"; BD="02 Doctor Detail"; AC=DET; SI=1

    def gen():
        yield from title_card("02","Doctor Detail","Full Profile  |  Qualifications  |  Slots  |  Book",AC)
        yield from fade_in(SS,BD,AC,"Doctor Detail Screen",
                           "Full profile: qualifications, stats, slots & consultation types",SI)
        yield from hold(frame(SS,"Dr. Priya Sharma — Cardiologist",
            "Gradient header with colour-coded initials avatar",BD,AC,sec_idx=SI),1.2)

        # Header highlight
        yield from hold(frame(SS,"Name, Specialty & Qualifications",
            "MBBS, MD (Cardiology), DM — gradient header",BD,AC,
            highlights=[(0,60,780,370,AC)],sec_idx=SI),1.5)

        # Star rating
        yield from hold(frame(SS,"Star Rating — 4.9★ with 287 patient reviews",
            "Ratings based on verified patient feedback",BD,AC,
            highlights=[(0,440,780,480,GOLD)],sec_idx=SI),1.2)

        # Stats row
        yield from hold(frame(SS,"Stats: 15 yrs experience  |  1,200+ patients  |  Rs.900 fee",
            "Three key metrics at a glance",BD,AC,
            highlights=[(30,510,750,630,GOLD)],sec_idx=SI),1.5)

        # Hospital
        yield from hold(frame(SS,"Hospital — Fortis Hospital, Mulund, Mumbai",
            "Location shown with map pin icon",BD,AC,
            highlights=[(30,638,750,672,AC)],sec_idx=SI),1.0)

        # Scroll to About
        yield from scroll_anim(SS,0,300,BD,AC,
            "Scrolling — About doctor & expertise",
            "Bio describing specialisation and clinical approach",SI)
        yield from hold(frame(SS,"About Doctor — detailed bio & expertise",
            "Areas of specialisation: interventional cardiology, heart failure",
            BD,AC,scroll_y=300,sec_idx=SI),1.5)

        # Scroll to available days
        yield from scroll_anim(SS,300,500,BD,AC,
            "Available Days — interactive chips","Mon / Tue / Wed / Thu / Fri / Sat",SI)
        yield from hold(frame(SS,"Available Days — Mon to Sat working schedule",
            "Chip is greyed out on unavailable days",
            BD,AC,scroll_y=500,
            highlights=[(36,958,740,1010,AC)],sec_idx=SI),1.5)

        # Scroll to time slots
        yield from scroll_anim(SS,500,680,BD,AC,
            "Time Slots Grid","4–6 available slots per working day",SI)
        yield from hold(frame(SS,"Time Slots — 09:00 AM to 04:00 PM",
            "Select a slot when booking — grid shows all options",
            BD,AC,scroll_y=680,
            highlights=[(36,1084,760,1236,AC)],sec_idx=SI),1.5)

        # Scroll to consultation types
        yield from scroll_anim(SS,680,830,BD,AC,
            "Consultation Types","In-Person / Video Call / Phone Call",SI)

        # Tap Video Call
        vid_p=sc(380,1355)
        yield from move_cur(SS,(PH_CX,PH_CY),vid_p,BD,AC,
            "Consultation Types — 3 modes with dynamic pricing",
            "In-Person=100%  Video=80%  Phone=60%",SI,scroll_y=830,n=20)
        yield from tap_cur(SS,vid_p,BD,AC,
            "Video Call selected — Rs.720 (80% of Rs.900)",
            "Pricing updates dynamically on selection",SI,scroll_y=830,
            highlights=[(274,1304,492,1404,AC)],n=16)
        yield from hold(frame(SS,"Video Call: Rs.720 — 20% discount for remote consult",
            "Phone Call would be Rs.540 — 40% discount",
            BD,AC,scroll_y=830,highlights=[(274,1304,492,1404,AC)],sec_idx=SI),1.2)

        # Tap In-Person back
        inp_p=sc(145,1355)
        yield from move_cur(SS,vid_p,inp_p,BD,AC,
            "Switching to In-Person","Full fee restored: Rs.900",SI,scroll_y=830,n=16)
        yield from tap_cur(SS,inp_p,BD,AC,
            "In-Person selected — full fee Rs.900 + 18% GST",
            "Total payable: Rs.1,062",SI,scroll_y=830,
            highlights=[(36,1304,254,1404,PRIM)],n=14)

        # Scroll to Book button
        yield from scroll_anim(SS,830,1000,BD,AC,
            "Book Appointment button at bottom","CTA to proceed to booking",SI)
        book_p=sc(390,1608)
        yield from move_cur(SS,(PH_CX,PH_CY+280),book_p,BD,AC,
            "Book Appointment — large CTA button",
            "Navigates to Booking Screen with doctor pre-filled",SI,scroll_y=1000,n=18)
        yield from tap_cur(SS,book_p,BD,AC,
            "Booking appointment","Opening Appointment Booking Screen →",SI,
            scroll_y=1000,highlights=[(40,1560,740,1660,SEC)],n=16)
        yield from outro_card(AC)

    write_video(f"{MP4_DIR}/02_doctor_detail.mp4",
                f"{MOV_DIR}/02_doctor_detail.mov", [gen()])


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 3 — BOOKING SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def make_v03():
    print("  [03] Booking Screen")
    SS="booking_screen.png"; BD="03 Booking"; AC=TEAL; SI=2

    def gen():
        yield from title_card("03","Appointment Booking",
                               "Consultation Type  |  Date Picker  |  Time Slots  |  Fee",AC)
        yield from fade_in(SS,BD,AC,"Appointment Booking Screen",
                           "Choose consultation type, date & time slot",SI)

        # Doctor summary
        yield from hold(frame(SS,"Doctor Summary Bar — always visible for reference",
            "Dr. Priya Sharma  |  Cardiologist  |  Fortis Hospital, Mumbai",
            BD,AC,highlights=[(20,148,760,264,AC)],sec_idx=SI),1.5)

        # Consultation type — show all 3
        yield from hold(frame(SS,"Consultation Type — 3 options with dynamic pricing",
            "In-Person=100%  |  Video Call=80%  |  Phone Call=60%",
            BD,AC,highlights=[(36,338,760,438,AC)],sec_idx=SI),1.2)

        vid_p=sc(380,388)
        yield from move_cur(SS,(PH_CX,PH_CY),vid_p,BD,AC,
            "Selecting Video Call","Fee updates to 80% instantly",SI,n=18)
        yield from tap_cur(SS,vid_p,BD,AC,
            "Video Call — Rs.720 (80% of Rs.900)",
            "Dynamic pricing reflects selected consultation mode",SI,
            highlights=[(274,338,492,438,TEAL)],n=16)
        yield from hold(frame(SS,"Video Call selected: Rs.720",
            "Phone Call would be Rs.540 (60%)",
            BD,AC,highlights=[(274,338,492,438,TEAL)],sec_idx=SI),1.0)

        phone_p=sc(620,388)
        yield from move_cur(SS,vid_p,phone_p,BD,AC,
            "Trying Phone Call consultation","Lowest fee: 60% of base",SI,n=16)
        yield from tap_cur(SS,phone_p,BD,AC,
            "Phone Call — Rs.540 (60% of Rs.900)",
            "Convenient for follow-up consultations",SI,
            highlights=[(512,338,730,438,TEAL)],n=14)
        yield from hold(frame(SS,"Phone Call: Rs.540 selected",
            "Suitable for quick queries and follow-ups",
            BD,AC,highlights=[(512,338,730,438,TEAL)],sec_idx=SI),1.0)

        inp_p=sc(145,388)
        yield from move_cur(SS,phone_p,inp_p,BD,AC,
            "Back to In-Person — full fee Rs.900","",SI,n=16)
        yield from tap_cur(SS,inp_p,BD,AC,
            "In-Person selected — Rs.900","Full in-clinic consultation",SI,
            highlights=[(36,338,254,438,PRIM)],n=14)

        # Date picker
        yield from hold(frame(SS,"Date Picker — next 14 available dates",
            "Horizontal scroll  •  Only doctor's working days are shown",
            BD,AC,highlights=[(36,508,750,612,AC)],sec_idx=SI),1.5)

        d1=sc(79,560); d2=sc(165,560); d3=sc(251,560); d4=sc(378,560)
        yield from move_cur(SS,inp_p,d1,BD,AC,
            "Date Picker — scroll left/right to see all 14 dates","",SI,n=20)
        yield from tap_cur(SS,d1,BD,AC,
            "Mon May 12 tapped","Time slot grid appears below",SI,
            highlights=[(36,508,122,612,PRIM)],n=14)
        yield from move_cur(SS,d1,d4,BD,AC,
            "Choosing Thu May 15","Preferred appointment date",SI,n=18)
        yield from tap_cur(SS,d4,BD,AC,
            "Thu May 15 selected — time slots now visible",
            "Grid only appears after a date is chosen",SI,
            highlights=[(336,508,422,612,PRIM)],n=16)
        yield from hold(frame(SS,"Date selected — time slot grid appears",
            "Slots shown for the chosen day only",
            BD,AC,highlights=[(336,508,422,612,PRIM)],sec_idx=SI),1.2)

        # Time slots
        yield from hold(frame(SS,"Time Slot Grid — 6 available slots",
            "09:00 AM / 10:00 AM / 11:00 AM / 02:00 PM / 03:00 PM / 04:00 PM",
            BD,AC,highlights=[(36,684,760,832,AC)],sec_idx=SI),1.2)

        s1=sc(147,717); s2=sc(389,717); s3=sc(631,717)
        yield from move_cur(SS,d4,s1,BD,AC,
            "Browsing time slots","Tap any slot to select",SI,n=16)
        yield from tap_cur(SS,s1,BD,AC,
            "09:00 AM tapped","Slot highlights in blue",SI,
            highlights=[(36,684,258,750,PRIM)],n=14)
        yield from move_cur(SS,s1,s2,BD,AC,
            "Choosing 10:00 AM instead","",SI,n=14)
        yield from tap_cur(SS,s2,BD,AC,
            "10:00 AM selected","Only one slot can be selected at a time",SI,
            highlights=[(278,684,500,750,PRIM)],n=16)
        yield from hold(frame(SS,"10:00 AM confirmed",
            "Date + time both selected — Proceed button now enabled",
            BD,AC,highlights=[(278,684,500,750,PRIM)],sec_idx=SI),1.2)

        # Fee breakdown
        yield from hold(frame(SS,"Fee Breakdown — Consultation Fee + 18% GST",
            "Rs.900 consultation  +  Rs.162 GST  =  Rs.1,062 total",
            BD,AC,highlights=[(20,866,760,1100,GOLD)],sec_idx=SI),1.8)

        # Proceed button
        proceed_p=sc(390,1608)
        yield from move_cur(SS,s2,proceed_p,BD,AC,
            "Proceed to Payment — button enabled",
            "Both date (May 15) and time (10:00 AM) are selected",SI,n=20)
        yield from tap_cur(SS,proceed_p,BD,AC,
            "Proceeding to Payment Screen","Rs.1,062 payable →",SI,
            highlights=[(40,1560,740,1660,PRIM)],n=16)
        yield from outro_card(AC)

    write_video(f"{MP4_DIR}/03_booking_flow.mp4",
                f"{MOV_DIR}/03_booking_flow.mov", [gen()])


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 4 — PAYMENT SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def make_v04():
    print("  [04] Payment Screen — all 4 methods")
    AC=PURP; SI=3

    def gen():
        yield from title_card("04","Payment Screen",
                               "UPI  |  Card  |  Wallet  |  Net Banking",AC)

        # ── UPI ──────────────────────────────────────────────────────────────
        SS="payment_upi.png"; BD="04 Payment — UPI"
        yield from fade_in(SS,BD,AC,"Payment Screen — 4 methods",
                           "UPI  |  Card  |  Wallet  |  Net Banking",SI)

        # Order summary
        yield from hold(frame(SS,"Order Summary — secure payment overview",
            "Dr. Priya Sharma  |  Thu May 15 10:00 AM  |  Total: Rs.1,062",
            BD,AC,highlights=[(20,130,760,360,AC)],sec_idx=SI),1.5)

        # Lock secure badge
        yield from hold(frame(SS,"Secure Payment badge — top-right lock icon",
            "All transactions are encrypted end-to-end",
            BD,AC,highlights=[(580,58,740,106,SEC)],sec_idx=SI),1.0)

        # UPI tabs highlight
        yield from hold(frame(SS,"Payment Method Tabs — 4 options",
            "UPI  |  Card  |  Wallet  |  Net Banking",
            BD,AC,highlights=[(30,368,760,500,AC)],sec_idx=SI),1.2)

        # QR code
        yield from hold(frame(SS,"UPI — Scan QR Code",
            "docbook@ybl  •  Google Pay / PhonePe / Paytm / BHIM supported",
            BD,AC,highlights=[(120,600,660,900,PURP)],sec_idx=SI),1.5)

        upi_f=sc(390,991)
        yield from move_cur(SS,(PH_CX,PH_CY),upi_f,BD,AC,
            "UPI ID Entry field","Enter UPI ID: yourname@upi",SI,n=18)
        yield from tap_cur(SS,upi_f,BD,AC,
            "Typing UPI ID — ratna@paytm","Alternatively scan QR in any UPI app",SI,
            highlights=[(40,948,740,1034,PURP)],n=14)
        yield from hold(frame(SS,"UPI ID entered — ready to pay",
            "Supports Google Pay, PhonePe, Paytm, BHIM UPI",
            BD,AC,highlights=[(40,948,740,1034,PURP)],sec_idx=SI),1.2)

        # ── Card ─────────────────────────────────────────────────────────────
        SS2="payment_card.png"; BD2="04 Payment — Card"
        tab_c=sc(580,459)
        yield from move_cur(SS,(PH_CX,PH_CY),tab_c,BD,AC,
            "Switching to Card Payment","",SI,n=16)
        yield from tap_cur(SS,tab_c,BD,AC,
            "Card tab selected","",SI,
            highlights=[(410,430,580,492,AC)],n=12)
        yield from slide_tr(SS,SS2,BD2,AC,
            "Card Payment","Saved cards + add new card with live preview",SI,"left")
        yield from hold(frame(SS2,"Card Payment screen",
            "Pre-saved cards + add new card form",
            BD2,AC,sec_idx=SI),1.0)

        # Saved cards
        yield from hold(frame(SS2,"Saved Cards — Visa 4242  |  Mastercard 8888",
            "Tap a saved card to select it instantly",
            BD2,AC,highlights=[(40,566,740,774,PURP)],sec_idx=SI),1.5)

        visa_p=sc(390,610)
        yield from move_cur(SS2,(PH_CX,PH_CY),visa_p,BD2,AC,
            "Selecting Visa •••• 4242","",SI,n=16)
        yield from tap_cur(SS2,visa_p,BD2,AC,
            "Visa card selected — checkmark appears","",SI,
            highlights=[(40,566,740,660,PRIM)],n=14)

        # Live card preview
        yield from hold(frame(SS2,"Live Card Preview — updates as you type",
            "Shows card number, holder name and expiry in real-time",
            BD2,AC,highlights=[(40,818,740,978,PURP)],sec_idx=SI),1.5)

        # Form fields
        yield from hold(frame(SS2,"New Card Form — Number / Name / Expiry / CVV",
            "Card preview updates in real-time as each field is filled",
            BD2,AC,highlights=[(40,998,740,1290,PURP)],sec_idx=SI),1.5)

        # ── Wallet ───────────────────────────────────────────────────────────
        SS3="payment_wallet.png"; BD3="04 Payment — Wallet"
        tab_w=sc(490,459)
        yield from move_cur(SS2,(PH_CX,PH_CY),tab_w,BD2,AC,
            "Switching to Wallet Payment","",SI,n=16)
        yield from tap_cur(SS2,tab_w,BD2,AC,
            "Wallet tab selected","",SI,
            highlights=[(405,430,575,492,AC)],n=12)
        yield from slide_tr(SS2,SS3,BD3,AC,
            "Wallet Payment","Paytm  |  PhonePe  |  Google Pay  |  Amazon Pay",SI,"left")
        yield from hold(frame(SS3,"4 Digital Wallets — colour-coded brand tiles",
            "2×2 grid layout with animated selection highlight",
            BD3,AC,highlights=[(50,340,730,620,PURP)],sec_idx=SI),1.5)

        paytm_p=sc(190,418)
        phonpe_p=sc(500,418)
        gpay_p=sc(190,558)
        amzn_p=sc(500,558)

        yield from move_cur(SS3,(PH_CX,PH_CY),paytm_p,BD3,AC,
            "Paytm Wallet","Brand colour: #00BAF2",SI,n=14)
        yield from tap_cur(SS3,paytm_p,BD3,AC,
            "Paytm selected","Border highlights in Paytm blue",SI,
            highlights=[(50,340,380,480,PURP)],n=12)

        yield from move_cur(SS3,paytm_p,phonpe_p,BD3,AC,
            "PhonePe Wallet","Brand colour: #5F259F",SI,n=14)
        yield from tap_cur(SS3,phonpe_p,BD3,AC,
            "PhonePe selected","Brand colour border",SI,
            highlights=[(380,340,730,480,PURP)],n=12)

        yield from move_cur(SS3,phonpe_p,gpay_p,BD3,AC,
            "Google Pay Wallet","Brand colour: #4285F4",SI,n=14)
        yield from tap_cur(SS3,gpay_p,BD3,AC,
            "Google Pay selected","",SI,
            highlights=[(50,480,380,620,PURP)],n=12)

        yield from move_cur(SS3,gpay_p,amzn_p,BD3,AC,
            "Amazon Pay Wallet","Brand colour: #FF9900",SI,n=14)
        yield from tap_cur(SS3,amzn_p,BD3,AC,
            "Amazon Pay selected","Animated border colour change",SI,
            highlights=[(380,480,730,620,PURP)],n=12)

        # ── Net Banking ───────────────────────────────────────────────────────
        SS4="payment_netbanking.png"; BD4="04 Payment — Net Banking"
        tab_nb=sc(685,459)
        yield from move_cur(SS3,(PH_CX,PH_CY),tab_nb,BD3,AC,
            "Switching to Net Banking","",SI,n=16)
        yield from tap_cur(SS3,tab_nb,BD3,AC,
            "Net Banking tab selected","",SI,
            highlights=[(590,430,760,492,AC)],n=12)
        yield from slide_tr(SS3,SS4,BD4,AC,
            "Net Banking","SBI  |  HDFC  |  ICICI  |  Axis  |  Kotak  |  Bank of Baroda",SI,"left")
        yield from hold(frame(SS4,"6 Major Banks — colour-coded tiles",
            "Tap any bank to open its net banking portal",
            BD4,AC,highlights=[(40,378,740,1050,PURP)],sec_idx=SI),1.5)

        banks_y=[426,538,650,762,874,986]
        bank_names=["SBI","HDFC Bank","ICICI Bank","Axis Bank","Kotak Bank","Bank of Baroda"]
        prev_p=sc(390,426)
        for bank_name,bank_y in zip(bank_names,banks_y):
            bank_p=sc(390,bank_y)
            yield from move_cur(SS4,prev_p,bank_p,BD4,AC,
                f"Tapping {bank_name}","",SI,n=12)
            yield from tap_cur(SS4,bank_p,BD4,AC,
                f"{bank_name} selected","Redirects to bank's net banking portal",SI,
                highlights=[(40,bank_y-48,740,bank_y+48,PURP)],n=12)
            prev_p=bank_p

        # ── Pay button ────────────────────────────────────────────────────────
        yield from slide_tr(SS4,"payment_upi.png","04 Payment — UPI",AC,
            "Back to UPI — processing payment","Tap Pay button to complete",SI,"right")
        pay_p=sc(390,1608)
        yield from move_cur("payment_upi.png",prev_p,pay_p,
            "04 Payment",AC,
            "Pay Rs.1,062 Securely","Secure payment processing",SI,n=20)
        yield from tap_cur("payment_upi.png",pay_p,"04 Payment",AC,
            "Payment initiated!","2-second processing animation",SI,
            highlights=[(40,1560,740,1660,SEC)],n=20)

        # Spinner
        for i in range(int(2.2*FPS)):
            t=i/(2.2*FPS)
            f=frame("payment_upi.png","Processing Payment...","Please wait — secure transaction",
                    "04 Payment",AC,sec_idx=SI)
            ang=int(t*360*4); cx2,cy2=sc(390,820)
            cv2.ellipse(f,(cx2,cy2),(28,28),ang,0,270,WHT,5)
            yield f

        yield from outro_card(AC)

    write_video(f"{MP4_DIR}/04_payment_all_methods.mp4",
                f"{MOV_DIR}/04_payment_all_methods.mov", [gen()])


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 5 — CONFIRMATION SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def make_v05():
    print("  [05] Booking Confirmation")
    SS="confirmation_screen.png"; BD="05 Confirmed!"; AC=SEC; SI=4

    def gen():
        yield from title_card("05","Booking Confirmed!",
                               "Success Animation  |  Booking Summary  |  Transaction ID",AC)

        # Animated fade in with success pulse
        for i in range(int(2.8*FPS)):
            t=i/(2.8*FPS)
            f=make_bg().copy()
            draw_phone(f,SS,0,min(1.0,t*2.5))
            r=int(lerp(70,140,ease_out((t*2.5)%1.0)))
            a=max(0.0,0.65-((t*2.5)%1.0)*0.65)
            cx2,cy2=sc(390,238)
            ov=f.copy()
            cv2.circle(ov,(cx2,cy2),r,AC,4)
            cv2.addWeighted(ov,a,f,1-a,0,f)
            section_badge(f,BD,AC)
            caption_bar(f,"Booking Confirmed!",
                        "Animated success checkmark with scale + fade-in",AC)
            progress_bar(f,SI,t*0.3,AC)
            yield f

        # Success circle
        yield from hold(frame(SS,"Success Checkmark — animated on screen load",
            "Scale + fade-in animation confirms payment success",
            BD,AC,highlights=[(300,148,480,328,AC)],sec_idx=SI),1.5)

        # Booking ID
        yield from hold(frame(SS,"Booking ID — unique 8-character alphanumeric code",
            "e.g. A3F7BC12  •  Use this ID for any support queries",
            BD,AC,highlights=[(60,470,720,542,GOLD)],sec_idx=SI),1.8)

        # Doctor info
        yield from hold(frame(SS,"Doctor & Hospital Details",
            "Dr. Priya Sharma  |  Cardiologist  |  Fortis Hospital, Mumbai",
            BD,AC,highlights=[(60,542,720,686,AC)],sec_idx=SI),1.5)

        # Date/time/type
        yield from hold(frame(SS,"Appointment Details — Date, Time & Consultation Type",
            "Thu May 15, 2026  |  10:00 AM  |  In-Person Consultation",
            BD,AC,highlights=[(60,686,720,830,AC)],sec_idx=SI),1.5)

        # Amount paid
        yield from hold(frame(SS,"Amount Paid — Rs.1,062 (including 18% GST)",
            "Consultation: Rs.900  +  GST Rs.162  =  Total Rs.1,062",
            BD,AC,highlights=[(60,830,720,902,GOLD)],sec_idx=SI),1.5)

        # Payment method + transaction ID
        yield from hold(frame(SS,"Payment Method & Transaction ID",
            "UPI — docbook@ybl  |  TXN1715123456789  (keep for records)",
            BD,AC,highlights=[(60,902,720,1050,AC)],sec_idx=SI),1.8)

        # Back to Home button
        home_btn=sc(200,1274)
        bkmb_btn=sc(580,1274)
        yield from move_cur(SS,(PH_CX,PH_CY),home_btn,BD,AC,
            "Back to Home button","Returns to doctor discovery screen",SI,n=20)
        yield from tap_cur(SS,home_btn,BD,AC,
            "Back to Home","One tap to start a new booking",SI,
            highlights=[(36,1226,390,1322,AC)],n=14)

        # View My Bookings
        yield from move_cur(SS,home_btn,bkmb_btn,BD,AC,
            "View My Bookings button","Opens the bookings dashboard",SI,n=18)
        yield from tap_cur(SS,bkmb_btn,BD,AC,
            "Opening My Bookings Dashboard","All appointments listed →",SI,
            highlights=[(410,1226,744,1322,SEC)],n=16)
        yield from outro_card(AC)

    write_video(f"{MP4_DIR}/05_confirmation.mp4",
                f"{MOV_DIR}/05_confirmation.mov", [gen()])


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 6 — MY BOOKINGS
# ══════════════════════════════════════════════════════════════════════════════
def make_v06():
    print("  [06] My Bookings Dashboard")
    SS="my_bookings.png"; SSE="my_bookings_empty.png"
    BD="06 My Bookings"; AC=ORG; SI=5

    def gen():
        yield from title_card("06","My Bookings",
                               "All Appointments  |  Status Tracking  |  Empty State",AC)
        yield from fade_in(SS,BD,AC,"My Bookings Dashboard",
                           "All appointments with status tracking",SI)
        yield from hold(frame(SS,"My Bookings — all appointments listed",
            "Reverse-chronological order with status badges",
            BD,AC,sec_idx=SI),1.2)

        # First booking card highlight
        yield from hold(frame(SS,"Booking Card — Booking ID in header",
            "Unique ID  +  colour-coded status badge per card",
            BD,AC,highlights=[(20,150,760,200,GOLD)],sec_idx=SI),1.5)

        # Status badge
        yield from hold(frame(SS,"Status Badge — Confirmed (green)",
            "Confirmed=green  |  Pending=yellow  |  Cancelled=red  |  Completed=gray",
            BD,AC,highlights=[(540,154,760,196,AC)],sec_idx=SI),1.8)

        # Doctor + specialty + hospital
        yield from hold(frame(SS,"Doctor Info — Name, Specialty & Hospital",
            "Dr. Priya Sharma  |  Cardiologist  |  Fortis Hospital, Mumbai",
            BD,AC,highlights=[(20,200,760,290,AC)],sec_idx=SI),1.5)

        # Date/time/type/amount
        yield from hold(frame(SS,"Appointment Details — Date, Time, Type & Fee",
            "Thu May 15  |  10:00 AM  |  In-Person  |  Rs.1,062",
            BD,AC,highlights=[(20,290,760,372,GOLD)],sec_idx=SI),1.5)

        # Scroll to second booking
        yield from scroll_anim(SS,0,220,BD,AC,
            "Scrolling — more bookings below",
            "Each booking has its own status and details",SI)
        yield from hold(frame(SS,"Second Booking — Pending status (yellow badge)",
            "Pending = awaiting confirmation from doctor",
            BD,AC,scroll_y=220,
            highlights=[(540,374,760,414,ORG)],sec_idx=SI),1.5)

        # Scroll to third
        yield from scroll_anim(SS,220,460,BD,AC,
            "Third Booking — another Confirmed appointment","",SI)
        yield from hold(frame(SS,"Multiple Bookings — complete appointment history",
            "All past and upcoming appointments in one place",
            BD,AC,scroll_y=460,sec_idx=SI),1.2)

        # Empty state transition
        yield from slide_tr(SS,SSE,BD,AC,
            "Empty State — when no bookings exist",
            "Friendly message + Browse Doctors shortcut",SI,"left")
        yield from hold(frame(SSE,"Empty State — no appointments yet",
            "Shown to first-time users before any booking",
            BD,AC,sec_idx=SI),1.2)

        # Empty state illustration
        yield from hold(frame(SSE,"Friendly illustration with clear message",
            "Find a doctor and book your first appointment!",
            BD,AC,highlights=[(260,400,520,640,AC)],sec_idx=SI),1.5)

        # Browse Doctors button
        browse_p=sc(390,882)
        yield from move_cur(SSE,(PH_CX,PH_CY),browse_p,BD,AC,
            "Browse Doctors button — quick shortcut to Home Screen",
            "One tap to start a new booking",SI,n=20)
        yield from tap_cur(SSE,browse_p,BD,AC,
            "Back to Home Screen","Complete user journey — from Home to Bookings",SI,
            highlights=[(290,840,490,924,AC)],n=16)
        yield from outro_card(AC)

    write_video(f"{MP4_DIR}/06_my_bookings.mp4",
                f"{MOV_DIR}/06_my_bookings.mov", [gen()])


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\nGenerating all 6 interactive feature videos\n")
    make_v01()
    make_v02()
    make_v03()
    make_v04()
    make_v05()
    make_v06()

    print("\nAll done! Files in Video/MP4/ and Video/MOV/:")
    total_mb=0
    for d in [MP4_DIR, MOV_DIR]:
        for f in sorted(os.listdir(d)):
            if f.endswith((".mp4",".mov")) and "Full" not in f:
                mb=os.path.getsize(os.path.join(d,f))/1024/1024
                total_mb+=mb
    print(f"  Feature videos total: {total_mb:.0f} MB")
