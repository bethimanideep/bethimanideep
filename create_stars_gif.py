from PIL import Image, ImageDraw, ImageFont
import random
import math
import os

WIDTH, HEIGHT = 1200, 400
FRAMES = 90
OUTPUT = "/Users/manidinuu/Desktop/bethimanideep/stars_banner.gif"

# ── Font loading ─────────────────────────────────────────────────────────────
font_paths = [
    "/System/Library/Fonts/Supplemental/Futura.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Arial.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]

def load_font(size):
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
    return ImageFont.load_default()

name_font = load_font(76)
sub_font  = load_font(30)

# ── Stars ─────────────────────────────────────────────────────────────────────
random.seed(42)
NUM_STARS = 220
stars = [
    {
        "x": random.uniform(0, WIDTH),
        "y": random.uniform(0, HEIGHT),
        "size": random.choice([1, 1, 1, 2, 2, 3]),
        "twinkle_off": random.uniform(0, 2 * math.pi),
        "twinkle_sp":  random.uniform(0.04, 0.13),
    }
    for _ in range(NUM_STARS)
]

NUM_SHOOT = 3
random.seed(7)
shooting = [
    {
        "sx":     random.uniform(50, WIDTH - 200),
        "sy":     random.uniform(20, HEIGHT // 3),
        "dx":     random.uniform(8, 14),
        "dy":     random.uniform(2, 5),
        "offset": i * (FRAMES // NUM_SHOOT),
    }
    for i in range(NUM_SHOOT)
]

# ── Animation timing ──────────────────────────────────────────────────────────
# Phase 0  (0 → 14):  name fades + slides up
# Phase 1  (15 → 34): "AI Engineer" types in char by char  (20 chars, 1 frame each)
# Phase 2  (35 → 39): cursor blinks alone after "AI Engineer"
# Phase 3  (40 → 65): "  ·  Full Stack Developer" types in (25 chars, ~1 frame each)
# Phase 4  (66 → 89): everything glows / pulses; cursor blinks then vanishes

LINE1 = "AI Engineer"
LINE2 = "  ·  Full Stack Developer"
FULL  = LINE1 + LINE2

PHASE_NAME_END   = 14
PHASE_L1_START   = 15
PHASE_L1_END     = PHASE_L1_START + len(LINE1)          # 26
PHASE_PAUSE_END  = PHASE_L1_END + 5                     # 31
PHASE_L2_START   = PHASE_PAUSE_END                      # 31
PHASE_L2_END     = PHASE_L2_START + len(LINE2)          # 56
PHASE_GLOW_END   = FRAMES                               # 90


def ease_out(t):
    return 1 - (1 - t) ** 3

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_frame(fi):
    img  = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 8))
    draw = ImageDraw.Draw(img)

    # ── Background gradient ──────────────────────────────────────────────────
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = lerp_color((4, 8, 38), (0, 0, 6), t)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    # ── Stars ────────────────────────────────────────────────────────────────
    for s in stars:
        tw = 0.5 + 0.5 * math.sin(s["twinkle_off"] + fi * s["twinkle_sp"] * 2 * math.pi)
        a  = int(90 + 165 * tw)
        col = (a, a, min(255, a + 25))
        x, y, sz = int(s["x"]), int(s["y"]), s["size"]
        if sz == 1:
            draw.point((x, y), fill=col)
        elif sz == 2:
            draw.ellipse([x-1, y-1, x+1, y+1], fill=col)
        else:
            draw.line([(x-3, y), (x+3, y)], fill=col, width=1)
            draw.line([(x, y-3), (x, y+3)], fill=col, width=1)
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(255, 255, 255))

    # ── Shooting stars ───────────────────────────────────────────────────────
    for ss in shooting:
        phase = (fi - ss["offset"]) % FRAMES
        if phase < FRAMES * 0.35:
            prog  = phase / (FRAMES * 0.35)
            sx    = ss["sx"] + ss["dx"] * phase
            sy    = ss["sy"] + ss["dy"] * phase
            ta    = int(255 * (1 - prog * 0.6))
            for k in range(10):
                tx = sx - k * ss["dx"] * 0.45
                ty = sy - k * ss["dy"] * 0.45
                a  = max(0, ta - k * 25)
                draw.ellipse([tx-1, ty-1, tx+1, ty+1], fill=(a, a, min(255, a + 50)))

    # ── Name text ────────────────────────────────────────────────────────────
    cx = WIDTH  // 2
    cy = HEIGHT // 2 - 28

    # name fade + float in
    if fi <= PHASE_NAME_END:
        t_name = fi / PHASE_NAME_END
        e      = ease_out(t_name)
        name_alpha  = int(255 * e)
        name_offset = int(24 * (1 - e))
    else:
        name_alpha  = 255
        name_offset = 0

    pulse = 0.93 + 0.07 * math.sin(fi * 0.11)

    bbox = draw.textbbox((0, 0), "Manideep Bethi", font=name_font)
    tw   = bbox[2] - bbox[0]
    th   = bbox[3] - bbox[1]
    nx   = cx - tw // 2
    ny   = cy - th // 2 + name_offset

    # soft glow passes
    for gr in [20, 12, 6]:
        ga = int(18 * pulse * name_alpha / 255)
        draw.text((nx, ny), "Manideep Bethi", font=name_font,
                  fill=(ga, ga * 2, min(255, ga * 7)))

    bright = int((210 + 45 * pulse) * name_alpha / 255)
    draw.text((nx, ny), "Manideep Bethi", font=name_font,
              fill=(bright, bright, 255))

    # ── Subtitle typewriter ───────────────────────────────────────────────────
    sub_y = cy + th // 2 + 20

    # How many chars of full text to reveal
    if fi < PHASE_L1_START:
        visible_chars = 0
    elif fi <= PHASE_L1_END:
        visible_chars = fi - PHASE_L1_START + 1
    elif fi <= PHASE_PAUSE_END:
        visible_chars = len(LINE1)
    elif fi <= PHASE_L2_END:
        visible_chars = len(LINE1) + (fi - PHASE_L2_START + 1)
    else:
        visible_chars = len(FULL)

    visible_chars = min(visible_chars, len(FULL))
    visible_text  = FULL[:visible_chars]

    # cursor blink: visible while still typing OR blinking in glow phase
    typing_done = visible_chars >= len(FULL)
    if not typing_done:
        show_cursor = True
    else:
        # blink every 6 frames
        show_cursor = (fi % 12) < 6

    # measure full text for centering anchor
    full_bbox = draw.textbbox((0, 0), FULL, font=sub_font)
    full_w    = full_bbox[2] - full_bbox[0]
    text_x    = cx - full_w // 2

    # Draw LINE1 part in cyan, LINE2 part in soft violet
    l1_vis = visible_text[:len(LINE1)]
    l2_vis = visible_text[len(LINE1):]

    # glow alpha for settled text
    if typing_done:
        g_alpha = int(200 + 55 * math.sin(fi * 0.14))
    else:
        g_alpha = 220

    if l1_vis:
        draw.text((text_x, sub_y), l1_vis, font=sub_font,
                  fill=(min(255, g_alpha), min(255, int(g_alpha * 0.85)), 100))

    if l2_vis:
        l1_bbox = draw.textbbox((0, 0), LINE1, font=sub_font)
        l1_w    = l1_bbox[2] - l1_bbox[0]
        draw.text((text_x + l1_w, sub_y), l2_vis, font=sub_font,
                  fill=(min(255, int(g_alpha * 0.65)), min(255, int(g_alpha * 0.55)), min(255, g_alpha)))

    # cursor
    if show_cursor:
        vis_bbox  = draw.textbbox((0, 0), visible_text, font=sub_font)
        cursor_x  = text_x + (vis_bbox[2] - vis_bbox[0]) + 3
        cursor_y1 = sub_y + 3
        cursor_y2 = sub_y + (vis_bbox[3] - vis_bbox[1]) - 3
        draw.line([(cursor_x, cursor_y1), (cursor_x, cursor_y2)],
                  fill=(180, 220, 255), width=2)

    return img


print("Generating star banner GIF...")
frames = []
for i in range(FRAMES):
    frames.append(draw_frame(i))
    if i % 15 == 0:
        print(f"  Frame {i+1}/{FRAMES}")

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    optimize=False,
    duration=55,
    loop=0,
)
print(f"\nDone! Saved to: {OUTPUT}")
