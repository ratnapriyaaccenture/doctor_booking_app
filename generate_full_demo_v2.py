# -*- coding: utf-8 -*-
"""
DocBook - Full Interactive Demo Video Generator v2
Simulates real app interaction: moving cursor, tap ripples, scrolling,
screen transitions — covering every screen and functionality.
Run: python generate_full_demo_v2.py
"""

import cv2
import numpy as np
import os, math

# ── Output ────────────────────────────────────────────────────────────────────
SS_DIR  = "assets/screenshots"
MP4_OUT = os.path.join("Video", "MP4", "DocBook_Full_Demo.mp4")
MOV_OUT = os.path.join("Video", "MOV", "DocBook_Full_Demo.mov")

FPS    = 30
VID_W  = 1920
VID_H  = 1080

# ── Phone render config ───────────────────────────────────────────────────────
# Screenshots are 780×1688 (2× logical 390×844)
SS_W, SS_H = 780, 1688
PH_SCALE   = 0.52                      # rendered phone scale
PH_SW      = int(SS_W * PH_SCALE)      # 405 px wide on canvas
PH_SH      = int(SS_H * PH_SCALE)      # 877 px tall on canvas
PH_CX      = 960                       # phone centre X (canvas)
PH_CY      = 530                       # phone centre Y (canvas)
PH_X0      = PH_CX - PH_SW // 2       # 757
PH_Y0      = PH_CY - PH_SH // 2       # 91

# Convert screenshot coords → canvas coords
def sc(x, y):
    return (int(PH_X0 + x * PH_SCALE),
            int(PH_Y0 + y * PH_SCALE))

# ── Colors (BGR) ──────────────────────────────────────────────────────────────
BG1  = ( 14,  10,  24)
BG2  = (  6,   4,  12)
PRIM = (232, 115,  26)
SEC  = ( 83, 168,  52)
PURP = (159,  37,  95)
TEAL = ( 94, 122,   0)
ORG  = (  0,  92, 230)
WHT  = (255, 255, 255)
GRY  = (160, 160, 180)
GOLD = (  4, 188, 251)
DARK = ( 30,  26,  46)

FONT  = cv2.FONT_HERSHEY_SIMPLEX
FONTB = cv2.FONT_HERSHEY_DUPLEX

# ── Easing ────────────────────────────────────────────────────────────────────
def ease_out(t):  return 1-(1-t)**3
def ease_in(t):   return t**3
def ease_io(t):   return t*t*(3-2*t)
def lerp(a,b,t):  return a+(b-a)*t

# ── Helpers ───────────────────────────────────────────────────────────────────
_ss_cache = {}
def load_ss(name):
    if name not in _ss_cache:
        p = os.path.join(SS_DIR, name)
        img = cv2.imread(p)
        if img is None:
            img = np.full((SS_H, SS_W, 3), 30, np.uint8)
        _ss_cache[name] = img
    return _ss_cache[name]

def make_bg():
    f = np.zeros((VID_H, VID_W, 3), np.uint8)
    for y in range(VID_H):
        r = y/VID_H
        f[y] = [int(BG1[i]*(1-r)+BG2[i]*r) for i in range(3)]
    return f

BASE_BG = make_bg()

def label(canvas, text, x, y, scale=0.65, color=WHT, thick=1, bold=False, anchor="left"):
    f = FONTB if bold else FONT
    (tw,th),_ = cv2.getTextSize(text, f, scale, thick)
    if anchor=="center": x-=tw//2
    elif anchor=="right": x-=tw
    cv2.putText(canvas, text, (x,y), f, scale, (0,0,0), thick+2, cv2.LINE_AA)
    cv2.putText(canvas, text, (x,y), f, scale, color, thick, cv2.LINE_AA)

def draw_phone_frame(canvas, ss_img, scroll_y=0, alpha=1.0):
    """Render the phone with optional vertical scroll offset."""
    # Crop screenshot with scroll
    crop_h = min(SS_H, SS_H - scroll_y)
    crop_y = max(0, scroll_y)
    cropped = ss_img[crop_y:crop_y+SS_H, 0:SS_W]
    if cropped.shape[0] < SS_H:
        pad = np.zeros((SS_H-cropped.shape[0], SS_W, 3), np.uint8)
        cropped = np.vstack([cropped, pad])

    resized = cv2.resize(cropped, (PH_SW, PH_SH))

    pad_x, pad_y = 20, 10
    notch_h = 28
    home_h  = 22
    bx1 = PH_X0 - pad_x
    by1 = PH_Y0 - pad_y - notch_h
    bx2 = PH_X0 + PH_SW + pad_x
    by2 = PH_Y0 + PH_SH + pad_y + home_h

    # Shadow
    sh = canvas.copy()
    cv2.rectangle(sh,(bx1+6,by1+10),(bx2+6,by2+10),(3,2,8),-1)
    cv2.addWeighted(sh,0.5,canvas,0.5,0,canvas)

    # Body
    cv2.rectangle(canvas,(bx1,by1),(bx2,by2),(44,38,62),-1)
    cv2.rectangle(canvas,(bx1,by1),(bx2,by2),(80,68,110),3)

    # Screen
    if alpha >= 1.0:
        canvas[PH_Y0:PH_Y0+PH_SH, PH_X0:PH_X0+PH_SW] = resized
    else:
        roi = canvas[PH_Y0:PH_Y0+PH_SH, PH_X0:PH_X0+PH_SW].astype(np.float32)
        canvas[PH_Y0:PH_Y0+PH_SH, PH_X0:PH_X0+PH_SW] = (roi*(1-alpha)+resized.astype(np.float32)*alpha).astype(np.uint8)

    # Notch
    nw,nh = 100,notch_h
    nx1 = PH_CX-nw//2; ny1=by1+pad_y
    cv2.rectangle(canvas,(nx1,ny1),(nx1+nw,ny1+nh),(22,18,32),-1)

    # Home bar
    hy = by2-home_h+6
    cv2.line(canvas,(PH_CX-50,hy),(PH_CX+50,hy),(90,78,118),5)

# ── Cursor / Tap animations ───────────────────────────────────────────────────
def draw_cursor(canvas, cx, cy, state="idle", t=0.0, color=WHT):
    """
    state: 'idle','move','pretap','tap','ripple'
    t: 0..1 within state
    """
    if state == "idle":
        cv2.circle(canvas,(cx,cy),16,(255,255,255,0) if False else color,-1)
        cv2.circle(canvas,(cx,cy),16,DARK,2)
        cv2.circle(canvas,(cx,cy), 5,DARK,-1)

    elif state == "pretap":
        sz = int(lerp(16, 10, ease_io(t)))
        overlay = canvas.copy()
        cv2.circle(overlay,(cx,cy),sz,color,-1)
        cv2.circle(overlay,(cx,cy),sz,DARK,2)
        cv2.addWeighted(overlay,0.85,canvas,0.15,0,canvas)

    elif state == "tap":
        # cursor shrinks then ripple expands
        if t < 0.4:
            sz = int(lerp(10,4,t/0.4))
            overlay=canvas.copy()
            cv2.circle(overlay,(cx,cy),sz,color,-1)
            cv2.addWeighted(overlay,0.9,canvas,0.1,0,canvas)
        else:
            rt = (t-0.4)/0.6
            rsz = int(lerp(4,55,ease_out(rt)))
            alpha_r = lerp(0.7,0.0,rt)
            overlay=canvas.copy()
            cv2.circle(overlay,(cx,cy),rsz,color,-1)
            cv2.addWeighted(overlay,alpha_r,canvas,1-alpha_r,0,canvas)

    elif state == "ripple":
        rsz = int(lerp(20,80,ease_out(t)))
        alpha_r = lerp(0.5,0.0,t)
        overlay=canvas.copy()
        cv2.circle(overlay,(cx,cy),rsz,color,3)
        cv2.addWeighted(overlay,alpha_r,canvas,1-alpha_r,0,canvas)

def draw_scroll_indicator(canvas, direction="up"):
    """Draw a scroll hint arrow."""
    cx,cy = PH_X0+PH_SW-28, PH_CY
    for i in range(3):
        dy = i*14
        if direction=="up":   pts=[(cx,cy-dy-8),(cx-8,cy-dy+4),(cx+8,cy-dy+4)]
        else:                  pts=[(cx,cy+dy+8),(cx-8,cy+dy-4),(cx+8,cy+dy-4)]
        cv2.fillPoly(canvas,[np.array(pts,np.int32)],(180,180,220))

def highlight_box(canvas, x1,y1,x2,y2, color=GOLD, alpha=0.3, thick=2):
    """Draw a semi-transparent highlight box."""
    overlay=canvas.copy()
    cv2.rectangle(overlay,(x1,y1),(x2,y2),color,-1)
    cv2.addWeighted(overlay,alpha,canvas,1-alpha,0,canvas)
    cv2.rectangle(canvas,(x1,y1),(x2,y2),color,thick)

# ── Caption bar ───────────────────────────────────────────────────────────────
def draw_caption(canvas, text, sub="", accent=PRIM):
    y_bar = VID_H - 70
    cv2.rectangle(canvas,(0,y_bar),(VID_W,VID_H),DARK,-1)
    cv2.rectangle(canvas,(0,y_bar),(6,VID_H),accent,-1)
    label(canvas, text, 30, y_bar+30, 0.85, WHT, 2, bold=True)
    if sub:
        label(canvas, sub, 30, y_bar+58, 0.60, GRY, 1)

def draw_section_badge(canvas, text, accent=PRIM):
    (tw,_),_ = cv2.getTextSize(text, FONTB, 0.65, 2)
    cv2.rectangle(canvas,(30,24),(54+tw,62),accent,-1)
    label(canvas, text, 42, 52, 0.65, WHT, 2, bold=True)

def draw_progress_dots(canvas, active, total=6):
    dot_r = 7; gap=22; total_w=(total*dot_r*2+(total-1)*gap)
    sx=(VID_W-total_w)//2; y=VID_H-80
    for i in range(total):
        cx2=sx+i*(dot_r*2+gap)+dot_r
        col=WHT if i==active else (60,55,80)
        cv2.circle(canvas,(cx2,y),dot_r,col,-1)

# ── Screen transition ─────────────────────────────────────────────────────────
def crossfade_frames(f_a, f_b, n=20):
    for i in range(n):
        t=ease_io(i/(n-1))
        yield cv2.addWeighted(f_a,1-t,f_b,t,0)

def slide_transition(from_ss, to_ss, n=28, direction="left"):
    """Phone slides out one direction, new slides in."""
    ss_from = load_ss(from_ss)
    ss_to   = load_ss(to_ss)
    for i in range(n):
        t=ease_io(i/(n-1))
        f=make_bg().copy()
        # scroll_y stays 0 for both
        offset = int(PH_SW * t)
        # Draw from-screen sliding out
        resf = cv2.resize(ss_from,(PH_SW,PH_SH))
        rest = cv2.resize(ss_to,  (PH_SW,PH_SH))
        if direction=="left":
            x_from = PH_X0 - offset
            x_to   = PH_X0 + PH_SW - offset
        else:
            x_from = PH_X0 + offset
            x_to   = PH_X0 - PH_SW + offset
        for x_pos, rimg in [(x_from,resf),(x_to,rest)]:
            xs=max(0,x_pos); xe=min(VID_W,x_pos+PH_SW)
            ixs=xs-x_pos;     ixe=ixs+(xe-xs)
            if xe>xs and ixe>ixs:
                f[PH_Y0:PH_Y0+PH_SH, xs:xe] = rimg[:,ixs:ixe]
        # draw phone chrome over top
        pad_x,pad_y=20,10; notch_h=28; home_h=22
        bx1=PH_X0-pad_x; by1=PH_Y0-pad_y-notch_h
        bx2=PH_X0+PH_SW+pad_x; by2=PH_Y0+PH_SH+pad_y+home_h
        cv2.rectangle(f,(bx1,by1),(bx2,by2),(44,38,62),4)
        yield f

def fade_in_screen(ss_name, n=20, scroll_y=0):
    ss=load_ss(ss_name)
    blank=make_bg().copy()
    for i in range(n):
        t=ease_out(i/(n-1))
        f=make_bg().copy()
        draw_phone_frame(f,ss,scroll_y,alpha=t)
        yield f

def fade_out_screen(ss_name, n=16, scroll_y=0):
    ss=load_ss(ss_name)
    for i in range(n):
        t=1-ease_in(i/(n-1))
        f=make_bg().copy()
        draw_phone_frame(f,ss,scroll_y,alpha=t)
        yield f

# ── Frame builder convenience ──────────────────────────────────────────────────
def build_frame(ss_name, caption="", sub="", section_name="", section_color=PRIM,
                scroll_y=0, dot_idx=0, highlights=None, cursor_pos=None,
                cursor_state="idle", cursor_t=0.0):
    f=make_bg().copy()
    ss=load_ss(ss_name)
    draw_phone_frame(f,ss,scroll_y)
    if highlights:
        for (x1,y1,x2,y2,col) in highlights:
            cx1,cy1=sc(x1,y1); cx2,cy2=sc(x2,y2)
            highlight_box(f,cx1,cy1,cx2,cy2,col)
    if cursor_pos:
        draw_cursor(f,cursor_pos[0],cursor_pos[1],cursor_state,cursor_t)
    if section_name:
        draw_section_badge(f,section_name,section_color)
    if caption:
        draw_caption(f,caption,sub,section_color)
    draw_progress_dots(f,dot_idx)
    return f

# ── Cursor path animation ─────────────────────────────────────────────────────
def cursor_move(f_start, ss_name, start_xy, end_xy,
                caption="", sub="", section_name="", section_color=PRIM,
                scroll_y=0, dot_idx=0, highlights=None, n=20):
    """Yield frames of cursor moving from start_xy to end_xy."""
    for i in range(n):
        t=ease_io(i/(n-1))
        cx=int(lerp(start_xy[0],end_xy[0],t))
        cy=int(lerp(start_xy[1],end_xy[1],t))
        f=build_frame(ss_name,caption,sub,section_name,section_color,
                      scroll_y,dot_idx,highlights,(cx,cy),"idle")
        yield f

def cursor_tap(ss_name, pos, caption="", sub="", section_name="",
               section_color=PRIM, scroll_y=0, dot_idx=0, highlights=None, n=18):
    """Yield frames of cursor tapping at pos."""
    for i in range(n):
        t=i/(n-1)
        # pretap first half, ripple second half
        state = "pretap" if t < 0.4 else "tap"
        f=build_frame(ss_name,caption,sub,section_name,section_color,
                      scroll_y,dot_idx,highlights,pos,state,t)
        yield f

def hold_frame_gen(frame, secs):
    for _ in range(int(secs*FPS)):
        yield frame.copy()

def scroll_anim(ss_name, from_scroll, to_scroll, n=25,
                caption="", sub="", section_name="", section_color=PRIM, dot_idx=0):
    for i in range(n):
        t=ease_io(i/(n-1))
        sy=int(lerp(from_scroll,to_scroll,t))
        f=make_bg().copy()
        ss=load_ss(ss_name)
        draw_phone_frame(f,ss,sy)
        draw_scroll_indicator(f,"down" if to_scroll>from_scroll else "up")
        if section_name: draw_section_badge(f,section_name,section_color)
        if caption:      draw_caption(f,caption,sub,section_color)
        draw_progress_dots(f,dot_idx)
        yield f

# ══════════════════════════════════════════════════════════════════════════════
# INTRO
# ══════════════════════════════════════════════════════════════════════════════
def gen_intro():
    total=int(4*FPS)
    for i in range(total):
        t=i/total
        f=make_bg().copy()
        # animated gradient bar
        bar_y=VID_H//2-140
        bar_h=6+int(4*math.sin(t*math.pi*4))
        cv2.rectangle(f,(0,bar_y),(VID_W,bar_y+bar_h),PRIM,-1)

        # title
        fade=min(1.0,t*3)*min(1.0,(1-t)*5)
        overlay=f.copy()
        label(overlay,"DocBook",VID_W//2,VID_H//2-80,3.8,WHT,5,True,"center")
        label(overlay,"Doctor Booking & Appointment App",VID_W//2,VID_H//2,1.05,GRY,1,False,"center")
        label(overlay,"Find  |  Book  |  Pay  |  Manage",VID_W//2,VID_H//2+52,0.78,GOLD,1,False,"center")
        cv2.addWeighted(overlay,fade,f,1-fade,0,f)

        # feature chips
        chips=[("37 Doctors",PRIM),("8 Cities",SEC),("4 Payment Methods",PURP),("6 Screens",ORG)]
        chip_y=VID_H//2+120; cx2=VID_W//2-560
        for chip_txt,chip_col in chips:
            (tw,_),_=cv2.getTextSize(chip_txt,FONT,0.68,1)
            cv2.rectangle(f,(cx2-12,chip_y-28),(cx2+tw+12,chip_y+10),DARK,-1)
            cv2.rectangle(f,(cx2-12,chip_y-28),(cx2+tw+12,chip_y+10),chip_col,2)
            label(f,chip_txt,cx2,chip_y,0.68,WHT,1)
            cx2+=tw+46

        # bottom bar
        cv2.rectangle(f,(0,VID_H-52),(VID_W,VID_H),PRIM,-1)
        label(f,"github.com/ratnapriyaaccenture/doctor_booking_app",
              VID_W//2,VID_H-18,0.70,WHT,1,False,"center")
        yield f

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — HOME SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def gen_home():
    SC="home_screen.png"; COL=PRIM; NM="01 Home Screen"; DI=0

    # ── 1.1 Fade in home screen
    for f in fade_in_screen(SC,20):
        draw_section_badge(f,NM,COL)
        draw_caption(f,"Home Screen — 37 doctors available",
                     "Browse all doctors across 8 Indian cities",COL)
        draw_progress_dots(f,DI); yield f

    # Hold
    ref=build_frame(SC,"Home Screen — 37 doctors available",
                    "Browse all doctors across 8 Indian cities",NM,COL,dot_idx=DI)
    yield from hold_frame_gen(ref,1.2)

    # ── 1.2 Cursor appears at centre, moves to search bar
    search_pos=sc(390,294)   # centre of search bar
    cursor_pos=sc(390,800)   # start: middle of screen
    yield from cursor_move(ref,SC,cursor_pos,search_pos,
        "Search Bar — find by name, specialty or hospital",
        "Tap to start typing",NM,COL,dot_idx=DI,n=22)

    yield from cursor_tap(SC,search_pos,
        "Tapping Search Bar","Type to filter doctors",NM,COL,dot_idx=DI,n=16)

    # ── 1.3 Show search result (home_filtered simulates "Cardio" typed)
    for f in slide_transition(SC,"home_filtered.png",n=22,direction="left"):
        draw_section_badge(f,NM,COL)
        draw_caption(f,"Search: typing 'Cardiologist'",
                     "Results filter live as you type",COL)
        draw_progress_dots(f,DI); yield f

    ref2=build_frame("home_filtered.png",
                     "Live Search — 5 matching doctors shown",
                     "Filter by name, specialty or hospital name",NM,COL,dot_idx=DI)
    yield from hold_frame_gen(ref2,1.5)

    # ── 1.4 Show clear (X) button area & go back to full list
    x_pos=sc(738,294)   # clear X button in search bar
    last_cursor=search_pos
    yield from cursor_move(ref2,"home_filtered.png",last_cursor,x_pos,
        "Clear Search","Tap X to reset search results",NM,COL,dot_idx=DI,n=18)
    yield from cursor_tap("home_filtered.png",x_pos,
        "Clearing Search","Returning to full doctor list",NM,COL,dot_idx=DI,n=14)

    # back to full list
    for f in slide_transition("home_filtered.png",SC,n=22,direction="right"):
        draw_section_badge(f,NM,COL)
        draw_caption(f,"Full list restored — 37 doctors",
                     "All filters cleared",COL)
        draw_progress_dots(f,DI); yield f

    # ── 1.5 City filter — tap Mumbai
    mumbai_chip=sc(83,416)   # centre of Mumbai chip
    yield from cursor_move(None,SC,(VID_W//2,VID_H//2),mumbai_chip,
        "City Filter — 8 cities available",
        "Tap a city chip to filter doctors",NM,COL,dot_idx=DI,n=22)

    hl_city=[(36,390,136,442,PRIM)]
    yield from cursor_tap(SC,mumbai_chip,
        "Selecting Mumbai","Filtering doctors in Mumbai",NM,COL,dot_idx=DI,
        highlights=hl_city,n=16)
    yield from hold_frame_gen(
        build_frame(SC,"Mumbai selected — 5 doctors shown",
                    "City chip highlighted in blue",NM,COL,
                    highlights=hl_city,dot_idx=DI),1.0)

    # ── 1.6 Specialty filter — tap Cardiologist
    cardio_chip=sc(105,528)
    hl_spec=[(36,502,178,554,SEC)]
    yield from cursor_move(None,SC,mumbai_chip,cardio_chip,
        "Specialty Filter — 8 specialties","Tap a specialty to narrow results",
        NM,COL,dot_idx=DI,n=20)
    yield from cursor_tap(SC,cardio_chip,
        "Selecting Cardiologist","Combining city + specialty filters",
        NM,COL,dot_idx=DI,highlights=hl_spec,n=16)
    yield from hold_frame_gen(
        build_frame(SC,"Mumbai + Cardiologist applied",
                    "Filters stack — results narrow further",
                    NM,COL,highlights=hl_city+hl_spec,dot_idx=DI),1.0)

    # ── 1.7 Rating filter — tap 4.5+
    rating_pos=sc(484,592)
    hl_rate=[(460,566,514,618,GOLD)]
    yield from cursor_move(None,SC,cardio_chip,rating_pos,
        "Star Rating Filter","Choose minimum rating: All / 3+ / 3.5+ / 4+ / 4.5+",
        NM,COL,dot_idx=DI,n=20)
    yield from cursor_tap(SC,rating_pos,
        "4.5+ Rating selected","Top-rated doctors only",
        NM,COL,dot_idx=DI,highlights=hl_rate,n=16)

    # Show filtered state
    for f in slide_transition(SC,"home_filtered.png",n=22,direction="left"):
        draw_section_badge(f,NM,COL)
        draw_caption(f,"Mumbai + Cardiologist + 4.5★ — 5 doctors",
                     "All three filters active simultaneously",COL)
        draw_progress_dots(f,DI); yield f

    ref3=build_frame("home_filtered.png",
                     "Filtered Results — 5 top-rated cardiologists in Mumbai",
                     "Doctor cards show: name, specialty, rating, hospital & fee",
                     NM,COL,dot_idx=DI)
    yield from hold_frame_gen(ref3,1.8)

    # ── 1.8 Clear all
    clear_pos=sc(650,585)   # "Clear all" button
    yield from cursor_move(ref3,"home_filtered.png",rating_pos,clear_pos,
        "Clear All Filters","One tap resets all active filters",NM,COL,dot_idx=DI,n=18)
    yield from cursor_tap("home_filtered.png",clear_pos,
        "Clearing all filters","Back to 37 doctors",NM,COL,dot_idx=DI,n=14)

    for f in slide_transition("home_filtered.png",SC,n=20,direction="right"):
        draw_section_badge(f,NM,COL); draw_progress_dots(f,DI)
        draw_caption(f,"All 37 doctors restored","Filters cleared",COL); yield f

    # ── 1.9 Tap first doctor card → navigate to detail
    card_pos=sc(390,778)
    yield from cursor_move(None,SC,(VID_W//2,VID_H//2),card_pos,
        "Doctor Card — tap to view full profile",
        "Shows: name, specialty, rating, hospital, consultation fee",
        NM,COL,dot_idx=DI,n=22)

    hl_card=[(20,680,760,876,PRIM)]
    yield from cursor_tap(SC,card_pos,
        "Opening Doctor Profile","Navigating to Doctor Detail Screen",
        NM,COL,dot_idx=DI,highlights=hl_card,n=18)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DOCTOR DETAIL
# ══════════════════════════════════════════════════════════════════════════════
def gen_doctor_detail():
    SC="doctor_detail.png"; COL=(176,78,16); NM="02 Doctor Detail"; DI=1

    for f in fade_in_screen(SC,22):
        draw_section_badge(f,NM,COL)
        draw_caption(f,"Doctor Detail Screen",
                     "Full profile: qualifications, stats, slots & consultation types",COL)
        draw_progress_dots(f,DI); yield f

    ref=build_frame(SC,"Doctor Profile — Dr. Priya Sharma, Cardiologist",
                    "Gradient header with colour-coded avatar",NM,COL,dot_idx=DI)
    yield from hold_frame_gen(ref,1.2)

    # Highlight header area
    yield from hold_frame_gen(
        build_frame(SC,"Name, Specialty & Qualifications",
                    "MBBS, MD (Cardiology), DM — shown below avatar",
                    NM,COL,highlights=[(0,60,780,450,COL)],dot_idx=DI),1.2)

    # Highlight stats row
    yield from hold_frame_gen(
        build_frame(SC,"Stats: Experience  |  Patients  |  Fee",
                    "15 yrs experience  •  1,200+ patients  •  Rs.900 consult fee",
                    NM,COL,highlights=[(30,510,750,630,GOLD)],dot_idx=DI),1.5)

    # Scroll down to show About & available days
    yield from scroll_anim(SC,0,300,n=28,
        caption="Scrolling — About bio & expertise",
        sub="Detailed description of doctor's specialisation and approach",
        section_name=NM,section_color=COL,dot_idx=DI)

    ref_s=build_frame(SC,"About Doctor — expertise & approach",
                      "Full bio with areas of specialisation",NM,COL,scroll_y=300,dot_idx=DI)
    yield from hold_frame_gen(ref_s,1.2)

    # Scroll to time slots
    yield from scroll_anim(SC,300,550,n=22,
        caption="Available Days & Time Slots",
        sub="Interactive day chips + slot grid",
        section_name=NM,section_color=COL,dot_idx=DI)

    ref_slots=build_frame(SC,"Time Slots — 6 slots per day",
                          "Tap a day to see available time slots",NM,COL,scroll_y=550,dot_idx=DI)
    yield from hold_frame_gen(ref_slots,1.2)

    # Scroll to consultation types
    yield from scroll_anim(SC,550,800,n=22,
        caption="Consultation Types",
        sub="In-Person / Video Call / Phone Call — each with different pricing",
        section_name=NM,section_color=COL,dot_idx=DI)

    # Tap Video Call
    video_pos=sc(380,1355)
    yield from cursor_move(None,SC,(PH_CX,PH_CY),video_pos,
        "Selecting Video Call Consultation","80% of base fee — Rs.720",
        NM,COL,scroll_y=800,dot_idx=DI,n=20)
    yield from cursor_tap(SC,video_pos,
        "Video Call selected","Price dynamically updates to 80%",
        NM,COL,scroll_y=800,dot_idx=DI,
        highlights=[(274,1304,492,1404,(176,78,16))],n=16)
    yield from hold_frame_gen(
        build_frame(SC,"Video Call — 80% of fee",
                    "Pricing: In-Person=100%  Video=80%  Phone=60%",
                    NM,COL,scroll_y=800,
                    highlights=[(274,1304,492,1404,(176,78,16))],dot_idx=DI),1.2)

    # Tap In-Person back
    inperson_pos=sc(145,1355)
    yield from cursor_move(None,SC,video_pos,inperson_pos,
        "Switching back to In-Person","Full consultation fee — Rs.900",
        NM,COL,scroll_y=800,dot_idx=DI,n=18)
    yield from cursor_tap(SC,inperson_pos,
        "In-Person selected","Full fee: Rs.900 + 18% GST",
        NM,COL,scroll_y=800,dot_idx=DI,
        highlights=[(36,1304,254,1404,PRIM)],n=14)

    # Scroll to Book button & tap
    yield from scroll_anim(SC,800,980,n=18,
        caption="Book Appointment CTA",sub="",
        section_name=NM,section_color=COL,dot_idx=DI)

    book_pos=sc(390,1608)
    yield from cursor_move(None,SC,(PH_CX,PH_CY+300),book_pos,
        "Book Appointment — tap to proceed",
        "Navigating to Booking Screen",NM,COL,scroll_y=980,dot_idx=DI,n=18)
    yield from cursor_tap(SC,book_pos,
        "Booking appointment","Opening Appointment Booking Screen",
        NM,COL,scroll_y=980,dot_idx=DI,
        highlights=[(40,1560,740,1660,SEC)],n=16)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — BOOKING SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def gen_booking():
    SC="booking_screen.png"; COL=TEAL; NM="03 Booking"; DI=2

    for f in fade_in_screen(SC,22):
        draw_section_badge(f,NM,COL)
        draw_caption(f,"Appointment Booking Screen",
                     "Choose consultation type, date & time slot",COL)
        draw_progress_dots(f,DI); yield f

    ref=build_frame(SC,"Doctor Summary — quick reference at top",
                    "Dr. Priya Sharma  |  Cardiologist  |  Fortis Hospital",
                    NM,COL,dot_idx=DI)
    yield from hold_frame_gen(ref,1.2)

    # Highlight doctor summary
    yield from hold_frame_gen(
        build_frame(SC,"Doctor Summary Bar",
                    "Always visible for reference during booking",
                    NM,COL,highlights=[(20,148,760,264,COL)],dot_idx=DI),1.0)

    # Tap Video Call consultation type
    video_pos=sc(380,388)
    yield from cursor_move(None,SC,(PH_CX,PH_CY),video_pos,
        "Consultation Type — 3 options","In-Person / Video Call / Phone Call",
        NM,COL,dot_idx=DI,n=20)
    yield from cursor_tap(SC,video_pos,
        "Video Call selected","Fee updates to 80%: Rs.900 × 0.8 = Rs.720",
        NM,COL,dot_idx=DI,
        highlights=[(274,338,492,438,TEAL)],n=16)
    yield from hold_frame_gen(
        build_frame(SC,"Video Call: Rs.720  (80% of base fee)",
                    "Phone Call would be 60% = Rs.540",
                    NM,COL,highlights=[(274,338,492,438,TEAL)],dot_idx=DI),1.0)

    # Back to In-Person
    inperson_pos=sc(145,388)
    yield from cursor_move(None,SC,video_pos,inperson_pos,
        "Selecting In-Person","Full fee: Rs.900",
        NM,COL,dot_idx=DI,n=16)
    yield from cursor_tap(SC,inperson_pos,
        "In-Person Consultation selected","Full fee Rs.900 + 18% GST = Rs.1,062",
        NM,COL,dot_idx=DI,
        highlights=[(36,338,254,438,PRIM)],n=14)

    # Tap date May 15 (4th chip, index 3)
    date_pos=sc(378,560)    # 4th date chip centre
    yield from cursor_move(None,SC,inperson_pos,date_pos,
        "Date Picker — next 14 available dates",
        "Horizontal scroll  •  Only doctor's available days shown",
        NM,COL,dot_idx=DI,n=22)
    yield from cursor_tap(SC,date_pos,
        "Thu May 15 selected","Time slot grid appears below",
        NM,COL,dot_idx=DI,
        highlights=[(336,508,422,612,PRIM)],n=16)
    yield from hold_frame_gen(
        build_frame(SC,"Date selected — time slots now visible",
                    "Slot grid only appears after a date is chosen",
                    NM,COL,highlights=[(336,508,422,612,PRIM)],dot_idx=DI),1.0)

    # Tap 10:00 AM slot
    slot_pos=sc(389,717)     # 10:00 AM (row1, col2)
    yield from cursor_move(None,SC,date_pos,slot_pos,
        "Time Slot Grid","Choose a time: 09:00 AM / 10:00 AM / 11:00 AM ...",
        NM,COL,dot_idx=DI,n=20)
    yield from cursor_tap(SC,slot_pos,
        "10:00 AM selected","Slot highlights — only one slot at a time",
        NM,COL,dot_idx=DI,
        highlights=[(278,684,500,750,PRIM)],n=16)
    yield from hold_frame_gen(
        build_frame(SC,"Time slot confirmed — 10:00 AM",
                    "Both date AND time must be selected to enable Proceed",
                    NM,COL,highlights=[(278,684,500,750,PRIM)],dot_idx=DI),1.2)

    # Highlight fee breakdown
    yield from hold_frame_gen(
        build_frame(SC,"Fee Breakdown — Consultation + 18% GST",
                    "Rs.900 + Rs.162 GST = Rs.1,062 Total",
                    NM,COL,highlights=[(20,866,760,1100,GOLD)],dot_idx=DI),1.5)

    # Tap Proceed
    proceed_pos=sc(390,1608)
    yield from cursor_move(None,SC,slot_pos,proceed_pos,
        "Proceed to Payment","Button enabled — date & time both selected",
        NM,COL,dot_idx=DI,n=20)
    yield from cursor_tap(SC,proceed_pos,
        "Proceeding to Payment","Opening Payment Screen",
        NM,COL,dot_idx=DI,
        highlights=[(40,1560,740,1660,PRIM)],n=16)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — PAYMENT SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def gen_payment():
    COL=PURP; NM="04 Payment"; DI=3

    # ── UPI tab (default) ─────────────────────────────────────────────────────
    SC="payment_upi.png"
    for f in fade_in_screen(SC,22):
        draw_section_badge(f,NM,COL)
        draw_caption(f,"Payment Screen — 4 Payment Methods",
                     "UPI  |  Card  |  Wallet  |  Net Banking",COL)
        draw_progress_dots(f,DI); yield f

    # Highlight order summary card
    yield from hold_frame_gen(
        build_frame(SC,"Order Summary — Dr. Priya Sharma  |  Thu May 15  |  10:00 AM",
                    "Total: Rs.1,062  (consultation + 18% GST)  •  Lock icon = Secure",
                    NM,COL,highlights=[(20,130,760,360,COL)],dot_idx=DI),1.5)

    # UPI — QR code
    yield from hold_frame_gen(
        build_frame(SC,"UPI Payment — Scan QR Code",
                    "docbook@ybl  •  Google Pay / PhonePe / Paytm / BHIM supported",
                    NM,COL,highlights=[(120,600,660,900,PURP)],dot_idx=DI),1.5)

    # Type UPI ID
    upi_field=sc(390,991)
    yield from cursor_move(None,SC,(PH_CX,PH_CY),upi_field,
        "UPI ID Entry — type your UPI ID","yourname@upi format",
        NM,COL,dot_idx=DI,n=18)
    yield from cursor_tap(SC,upi_field,
        "Typing UPI ID","ratna@paytm",
        NM,COL,dot_idx=DI,
        highlights=[(40,948,740,1034,PURP)],n=14)
    yield from hold_frame_gen(
        build_frame(SC,"UPI ID entered — ready to pay",
                    "Alternatively scan the QR code directly in your UPI app",
                    NM,COL,highlights=[(40,948,740,1034,PURP)],dot_idx=DI),1.0)

    # ── Card tab ──────────────────────────────────────────────────────────────
    SC2="payment_card.png"
    tab_card=sc(580,459)
    yield from cursor_move(None,SC,(PH_CX,PH_CY),tab_card,
        "Switching to Card Payment","Tap Card tab",NM,COL,dot_idx=DI,n=18)
    yield from cursor_tap(SC,tab_card,
        "Card tab selected","Opening Card Payment form",NM,COL,dot_idx=DI,n=14)

    for f in slide_transition(SC,SC2,n=20,direction="left"):
        draw_section_badge(f,NM,COL); draw_progress_dots(f,DI)
        draw_caption(f,"Card Payment","Saved cards + add new card with live preview",COL)
        yield f

    # Highlight saved cards
    yield from hold_frame_gen(
        build_frame(SC2,"Saved Cards — Visa 4242  |  Mastercard 8888",
                    "Tap a saved card to select it instantly",
                    NM,COL,highlights=[(40,566,740,774,PURP)],dot_idx=DI),1.5)

    # Tap Visa card
    visa_pos=sc(390,610)
    yield from cursor_tap(SC2,visa_pos,
        "Visa •••• 4242 selected","Checkmark appears on selected card",
        NM,COL,dot_idx=DI,
        highlights=[(40,566,740,660,PRIM)],n=14)

    # Highlight card preview
    yield from hold_frame_gen(
        build_frame(SC2,"Live Card Preview","Updates in real-time as you type card details",
                    NM,COL,highlights=[(40,818,740,978,PURP)],dot_idx=DI),1.5)

    # Highlight new card fields
    yield from hold_frame_gen(
        build_frame(SC2,"Add New Card — Card Number / Name / Expiry / CVV",
                    "Preview card shows your details as you type",
                    NM,COL,highlights=[(40,998,740,1290,PURP)],dot_idx=DI),1.2)

    # ── Wallet tab ────────────────────────────────────────────────────────────
    SC3="payment_wallet.png"
    tab_wallet=sc(490,459)
    for f in slide_transition(SC2,SC3,n=20,direction="left"):
        draw_section_badge(f,NM,COL); draw_progress_dots(f,DI)
        draw_caption(f,"Wallet Payment","Paytm  |  PhonePe  |  Google Pay  |  Amazon Pay",COL)
        yield f

    yield from hold_frame_gen(
        build_frame(SC3,"Digital Wallets — 4 options","Colour-coded brand tiles in 2×2 grid",
                    NM,COL,highlights=[(50,340,730,620,PURP)],dot_idx=DI),1.2)

    # Tap PhonePe
    phonpe_pos=sc(500,418)
    yield from cursor_move(None,SC3,(PH_CX,PH_CY),phonpe_pos,
        "Selecting PhonePe wallet","Animated border highlights selection",
        NM,COL,dot_idx=DI,n=16)
    yield from cursor_tap(SC3,phonpe_pos,
        "PhonePe selected","Border colour changes to wallet brand colour",
        NM,COL,dot_idx=DI,
        highlights=[(380,340,730,480,PURP)],n=14)
    yield from hold_frame_gen(
        build_frame(SC3,"PhonePe selected","Tap Pay to process instantly",
                    NM,COL,highlights=[(380,340,730,480,PURP)],dot_idx=DI),0.8)

    # ── Net Banking tab ───────────────────────────────────────────────────────
    SC4="payment_netbanking.png"
    for f in slide_transition(SC3,SC4,n=20,direction="left"):
        draw_section_badge(f,NM,COL); draw_progress_dots(f,DI)
        draw_caption(f,"Net Banking","SBI  |  HDFC  |  ICICI  |  Axis  |  Kotak  |  Bank of Baroda",COL)
        yield f

    yield from hold_frame_gen(
        build_frame(SC4,"6 Major Banks — colour-coded logo tiles",
                    "Tap your bank to redirect to net banking portal",
                    NM,COL,highlights=[(40,378,740,1050,PURP)],dot_idx=DI),1.2)

    # Tap SBI
    sbi_pos=sc(390,426)
    yield from cursor_move(None,SC4,(PH_CX,PH_CY),sbi_pos,
        "Tapping SBI","Redirects to SBI net banking",NM,COL,dot_idx=DI,n=16)
    yield from cursor_tap(SC4,sbi_pos,
        "SBI selected","Secure bank portal opens",
        NM,COL,dot_idx=DI,
        highlights=[(40,378,740,474,PURP)],n=14)

    # ── Back to UPI, tap Pay ──────────────────────────────────────────────────
    for f in slide_transition(SC4,"payment_upi.png",n=20,direction="right"):
        draw_section_badge(f,NM,COL); draw_progress_dots(f,DI)
        draw_caption(f,"Back to UPI — processing payment","Tap Pay button",COL)
        yield f

    pay_btn=sc(390,1608)
    yield from cursor_move(None,"payment_upi.png",(PH_CX,PH_CY),pay_btn,
        "Pay Rs.1,062 Securely","Processing with 2-second animation",
        NM,COL,dot_idx=DI,n=20)
    yield from cursor_tap("payment_upi.png",pay_btn,
        "Payment initiated","Processing spinner appears for 2 seconds",
        NM,COL,dot_idx=DI,
        highlights=[(40,1560,740,1660,SEC)],n=20)

    # Processing animation (spinner effect)
    for i in range(int(2.2*FPS)):
        t=i/(2.2*FPS)
        f=build_frame("payment_upi.png",
                      "Processing Payment...","Please wait — secure transaction",
                      NM,COL,dot_idx=DI)
        # Spinner
        angle=int(t*360*3)
        cx2,cy2=sc(390,820)
        cv2.ellipse(f,(cx2,cy2),(28,28),angle,0,270,WHT,5)
        yield f

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — CONFIRMATION
# ══════════════════════════════════════════════════════════════════════════════
def gen_confirmation():
    SC="confirmation_screen.png"; COL=SEC; NM="05 Confirmed!"; DI=4

    # Animated fade in with pulse on success circle
    for i in range(int(2.5*FPS)):
        t=i/(2.5*FPS)
        f=make_bg().copy()
        draw_phone_frame(f,load_ss(SC),0,min(1.0,t*2))
        # Pulse ring over success circle
        pulse_r=int(lerp(70,130,ease_out((t*3)%1.0)))
        pulse_a=max(0.0, 0.6-((t*3)%1.0)*0.6)
        cx2,cy2=sc(390,238)
        ov=f.copy()
        cv2.circle(ov,(cx2,cy2),pulse_r,SEC,4)
        cv2.addWeighted(ov,pulse_a,f,1-pulse_a,0,f)
        draw_section_badge(f,NM,COL)
        draw_caption(f,"Booking Confirmed!",
                     "Animated success screen with booking summary",COL)
        draw_progress_dots(f,DI); yield f

    # Highlight Booking ID
    yield from hold_frame_gen(
        build_frame(SC,"Unique Booking ID — 8-character alphanumeric",
                    "e.g. A3F7BC12  •  Use this ID for any queries",
                    NM,COL,highlights=[(60,470,720,542,GOLD)],dot_idx=DI),1.5)

    # Highlight appointment details
    yield from hold_frame_gen(
        build_frame(SC,"Appointment Details — Doctor, Date, Time, Type",
                    "Thu May 15  •  10:00 AM  •  In-Person Consultation",
                    NM,COL,highlights=[(60,542,720,758,COL)],dot_idx=DI),1.5)

    # Highlight amount & payment
    yield from hold_frame_gen(
        build_frame(SC,"Payment Confirmed — Rs.1,062  |  Transaction ID",
                    "Payment method + unique Transaction ID for records",
                    NM,COL,highlights=[(60,758,720,902,GOLD)],dot_idx=DI),1.5)

    # Tap View My Bookings
    mybookings_btn=sc(580,1274)
    yield from cursor_move(None,SC,(PH_CX,PH_CY),mybookings_btn,
        "View My Bookings","See all booked appointments",NM,COL,dot_idx=DI,n=20)
    yield from cursor_tap(SC,mybookings_btn,
        "Opening My Bookings","Navigating to bookings dashboard",
        NM,COL,dot_idx=DI,
        highlights=[(W//2+20 if False else 410,1226,740,1322,COL)],n=16)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — MY BOOKINGS
# ══════════════════════════════════════════════════════════════════════════════
def gen_my_bookings():
    SC="my_bookings.png"; COL=ORG; NM="06 My Bookings"; DI=5

    for f in fade_in_screen(SC,22):
        draw_section_badge(f,NM,COL)
        draw_caption(f,"My Bookings Dashboard",
                     "All appointments with status tracking",COL)
        draw_progress_dots(f,DI); yield f

    ref=build_frame(SC,"My Bookings — all appointments listed",
                    "Reverse-chronological order",NM,COL,dot_idx=DI)
    yield from hold_frame_gen(ref,1.0)

    # Highlight first booking card
    yield from hold_frame_gen(
        build_frame(SC,"Booking Card — Booking ID + Status Badge",
                    "Confirmed (green)  |  Pending (yellow)  |  Cancelled (red)  |  Completed (gray)",
                    NM,COL,highlights=[(20,150,760,370,GOLD)],dot_idx=DI),1.8)

    # Highlight doctor info on card
    yield from hold_frame_gen(
        build_frame(SC,"Card Details — Doctor, Specialty, Hospital, Date, Time, Type, Amount",
                    "Everything at a glance — no need to open individual bookings",
                    NM,COL,highlights=[(20,150,760,370,ORG)],dot_idx=DI),1.5)

    # Scroll to show second booking
    yield from scroll_anim(SC,0,240,n=22,
        caption="More bookings — scroll to see all",
        sub="Each booking shows its own status and details",
        section_name=NM,section_color=COL,dot_idx=DI)
    yield from hold_frame_gen(
        build_frame(SC,"Multiple Bookings — different statuses",
                    "Confirmed / Pending / Cancelled — colour-coded at a glance",
                    NM,COL,scroll_y=240,dot_idx=DI),1.5)

    # Show empty state
    for f in slide_transition(SC,"my_bookings_empty.png",n=22,direction="left"):
        draw_section_badge(f,NM,COL); draw_progress_dots(f,DI)
        draw_caption(f,"Empty State — when no bookings exist",
                     "Friendly message + Browse Doctors shortcut",COL)
        yield f

    yield from hold_frame_gen(
        build_frame("my_bookings_empty.png","Empty State — Browse Doctors CTA",
                    "Quick link back to Home Screen to book a new appointment",
                    NM,COL,highlights=[(290,840,490,924,COL)],dot_idx=DI),1.8)

    # Browse Doctors button tap
    browse_pos=sc(390,882)
    yield from cursor_tap("my_bookings_empty.png",browse_pos,
        "Browse Doctors — back to Home Screen",
        "Complete user journey demonstrated",
        NM,COL,dot_idx=DI,highlights=[(290,840,490,924,COL)],n=16)

# ══════════════════════════════════════════════════════════════════════════════
# OUTRO
# ══════════════════════════════════════════════════════════════════════════════
def gen_outro():
    total=int(3.5*FPS)
    for i in range(total):
        t=ease_io(i/total)
        f=make_bg().copy()
        cv2.rectangle(f,(0,0),(8,VID_H),PRIM,-1)
        cv2.rectangle(f,(0,VID_H-52),(VID_W,VID_H),PRIM,-1)
        label(f,"DocBook",VID_W//2,VID_H//2-90,3.5,WHT,5,True,"center")
        label(f,"Doctor Booking & Appointment App",VID_W//2,VID_H//2-18,1.1,GRY,1,False,"center")
        label(f,"Flutter  |  Material Design 3  |  Google Fonts Poppins",
              VID_W//2,VID_H//2+40,0.72,GOLD,1,False,"center")
        label(f,"github.com/ratnapriyaaccenture/doctor_booking_app",
              VID_W//2,VID_H//2+95,0.80,PRIM,1,False,"center")
        label(f,"github.com/ratnapriyaaccenture/doctor_booking_app",
              VID_W-16,VID_H-18,0.65,WHT,1,False,"right")
        cv2.addWeighted(f,t,make_bg(),1-t,0,f)
        yield f

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    os.makedirs(os.path.dirname(MP4_OUT), exist_ok=True)
    os.makedirs(os.path.dirname(MOV_OUT), exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writers = [
        cv2.VideoWriter(MP4_OUT, fourcc, FPS, (VID_W, VID_H)),
        cv2.VideoWriter(MOV_OUT, fourcc, FPS, (VID_W, VID_H)),
    ]

    def emit(gen, label_txt=""):
        count=0
        for frame in gen:
            for w in writers: w.write(frame)
            count+=1
        if label_txt: print(f"    {label_txt}: {count} frames ({count/FPS:.1f}s)")
        return count

    total=0
    print("\nGenerating DocBook Full Interactive Demo Video\n")

    print("  [Intro]")
    total+=emit(gen_intro(),"Intro title card")

    print("  [Section 1] Home Screen — Search & Filters")
    total+=emit(gen_home(),"Home Screen")

    print("  [Section 2] Doctor Detail Screen")
    total+=emit(gen_doctor_detail(),"Doctor Detail")

    print("  [Section 3] Appointment Booking")
    total+=emit(gen_booking(),"Booking Screen")

    print("  [Section 4] Payment — UPI / Card / Wallet / Net Banking")
    total+=emit(gen_payment(),"Payment Screen")

    print("  [Section 5] Booking Confirmation")
    total+=emit(gen_confirmation(),"Confirmation")

    print("  [Section 6] My Bookings Dashboard")
    total+=emit(gen_my_bookings(),"My Bookings")

    print("  [Outro]")
    total+=emit(gen_outro(),"Outro card")

    for w in writers: w.release()

    print(f"\n  Total: {total} frames = {total/FPS:.0f} seconds")
    for path in [MP4_OUT, MOV_OUT]:
        mb=os.path.getsize(path)/1024/1024
        print(f"  {path}  ({mb:.1f} MB)")

if __name__=="__main__":
    main()
