#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render v3 of the 23 November 2026 world-news summary image.

Development-time builder (uses Pillow). Layout: a compressed masthead,
the date as its own high-contrast badge, then three tiers — two hero
stories (the Kyiv rescue and the AI stock sell-off), two mid stories
(COP31, US-Iran) and two small ones (the House, Shuri Castle). Every
story carries its own drawn icon and exactly one event phrase plus one
hard number or result; there are no summary sentences. A dotted world
map sits behind everything as a faint texture only. The builder saves
entry.png and rewrites entry_data.py as base64 text, so the shipped
entrypoint main.py needs only the Python standard library.
"""

import base64
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/liberation"

W = 1024
H = 1024

INK = (13, 17, 21)
PANEL = (25, 32, 41)
PANEL_EDGE = (58, 70, 84)
PAPER = (242, 244, 246)
SOFT = (186, 195, 206)
FAINT = (118, 130, 144)
RED = (228, 60, 50)
TEXTURE = (23, 30, 39)
GOLD = (240, 190, 60)

MARGIN = 36


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = font("LiberationSerif-Bold.ttf", 37)
F_KICKER = font("LiberationSans-Bold.ttf", 19)
F_BADGE = font("LiberationSans-Bold.ttf", 27)
F_TAG = font("LiberationSans-Bold.ttf", 19)
F_HERO_HEAD = font("LiberationSans-Bold.ttf", 43)
F_HERO_RESULT = font("LiberationSans-Bold.ttf", 24)
F_MID_HEAD = font("LiberationSans-Bold.ttf", 33)
F_MID_RESULT = font("LiberationSans-Bold.ttf", 21)
F_LOW_HEAD = font("LiberationSans-Bold.ttf", 29)
F_LOW_RESULT = font("LiberationSans-Bold.ttf", 19)
F_CHART_LABEL = font("LiberationSans-Bold.ttf", 21)
F_CHART_VALUE = font("LiberationSans-Bold.ttf", 25)
F_FOOT = font("LiberationSans-Regular.ttf", 16)


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ------------------------------------------------------- faint map texture

# Land as longitude spans per latitude band (26 bands). In v3 this map
# is only a background texture: no markers, no labels, no information.
LAND_SPANS = [
    [(-125, -105), (-95, -82), (-45, -30), (45, 60), (75, 105), (120, 150), (160, 178)],
    [(-140, -95), (-90, -80), (-50, -35), (18, 32), (38, 178)],
    [(-168, -140), (-135, -85), (-52, -38), (12, 28), (30, 178)],
    [(-165, -145), (-130, -80), (5, 30), (30, 175)],
    [(-125, -95), (-85, -70), (0, 170)],
    [(-125, -67), (-5, 140), (142, 160)],
    [(-124, -68), (-9, 60), (65, 140), (138, 142)],
    [(-124, -70), (-9, 45), (50, 75), (80, 122), (130, 140)],
    [(-120, -75), (-10, 32), (35, 60), (68, 90), (95, 122), (130, 137)],
    [(-118, -77), (-105, -87), (-10, 35), (43, 60), (68, 88), (95, 108), (108, 122)],
    [(-105, -87), (-8, 38), (70, 88), (92, 108), (120, 122)],
    [(-92, -83), (-12, 40), (73, 86), (95, 105), (120, 122)],
    [(-77, -60), (-15, 42), (77, 80), (98, 107), (110, 120)],
    [(-78, -55), (-10, 42), (100, 115), (120, 130)],
    [(-78, -50), (-8, 40), (102, 112), (118, 132)],
    [(-75, -48), (-5, 38), (110, 118), (125, 136), (136, 146)],
    [(-72, -45), (0, 36), (131, 140), (142, 148)],
    [(-70, -42), (8, 35), (113, 130), (135, 146)],
    [(-68, -42), (10, 34), (113, 148)],
    [(-66, -45), (13, 33), (114, 150)],
    [(-64, -48), (16, 31), (115, 148)],
    [(-62, -52), (18, 28), (118, 145), (168, 174)],
    [(-62, -55), (167, 174)],
    [(-64, -58), (167, 171)],
    [(-66, -60)],
    [(-68, -64)],
]


def draw_texture(draw):
    cols = 118
    rows = len(LAND_SPANS)
    cell_x = W / cols
    cell_y = H / rows
    for r, spans in enumerate(LAND_SPANS):
        land_cols = set()
        for lon_a, lon_b in spans:
            c0 = int((lon_a + 170) / 360 * cols)
            c1 = int((lon_b + 170) / 360 * cols)
            land_cols.update(range(max(0, c0), min(cols, c1 + 1)))
        for c in land_cols:
            px = c * cell_x + cell_x / 2
            py = r * cell_y + cell_y / 2
            draw.ellipse([px - 2.4, py - 2.4, px + 2.4, py + 2.4],
                         fill=TEXTURE)


# ------------------------------------------------------------------ icons
# Each icon is drawn with plain PIL lines/shapes inside an s-by-s box at
# (x, y), in the story's accent colour.

def icon_building(draw, x, y, s, color):
    """Apartment block split by a crack, with a heart: the rescue."""
    w = 5
    bx, by, bw, bh = x + s * 0.14, y + s * 0.08, s * 0.54, s * 0.84
    draw.rectangle([bx, by, bx + bw, by + bh], outline=color, width=w)
    crack = [(bx + bw * 0.58, by), (bx + bw * 0.44, by + bh * 0.30),
             (bx + bw * 0.60, by + bh * 0.55), (bx + bw * 0.46, by + bh)]
    draw.line(crack, fill=color, width=4, joint="curve")
    for r in range(3):
        for c in range(2):
            wx = bx + 9 + c * (bw / 2 - 4)
            wy = by + 11 + r * (bh - 28) / 2
            draw.rectangle([wx, wy, wx + 10, wy + 12], outline=color, width=3)
    hx, hy = x + s * 0.84, y + s * 0.50
    draw.polygon([(hx, hy + 16), (hx - 15, hy), (hx - 5, hy - 11),
                  (hx, hy - 4), (hx + 5, hy - 11), (hx + 15, hy)],
                 fill=RED)


def icon_crash(draw, x, y, s, color):
    """A plunging zigzag line with an arrowhead: the sell-off."""
    w = 6
    pts = [(x + s * 0.06, y + s * 0.18), (x + s * 0.34, y + s * 0.40),
           (x + s * 0.52, y + s * 0.26), (x + s * 0.88, y + s * 0.78)]
    draw.line(pts, fill=color, width=w, joint="curve")
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 20, ey - 4), (ex - 4, ey - 20)], fill=color)
    draw.line([x + s * 0.06, y + s * 0.92, x + s * 0.94, y + s * 0.92],
              fill=color, width=3)


def icon_globe(draw, x, y, s, color):
    """A globe with meridians: the climate talks."""
    w = 4
    cx, cy, r = x + s / 2, y + s / 2, s * 0.40
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
                 outline=color, width=3)
    draw.line([cx - r, cy, cx + r, cy], fill=color, width=3)
    draw.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.75], 0, 180,
             fill=color, width=3)
    draw.arc([cx - r, cy - r * 0.75, cx + r, cy + r * 0.55], 180, 360,
             fill=color, width=3)


def icon_clash(draw, x, y, s, color):
    """Two arrows driving at each other with a burst: the standoff."""
    w = 6
    my = y + s * 0.50
    draw.line([x + s * 0.05, my, x + s * 0.40, my], fill=color, width=w)
    draw.polygon([(x + s * 0.52, my), (x + s * 0.36, my - 11),
                  (x + s * 0.36, my + 11)], fill=color)
    draw.line([x + s * 0.95, my, x + s * 0.60, my], fill=color, width=w)
    draw.polygon([(x + s * 0.48, my), (x + s * 0.64, my - 11),
                  (x + s * 0.64, my + 11)], fill=color)
    for dx, dy in [(-16, -22), (0, -28), (16, -22), (-16, 22), (0, 28), (16, 22)]:
        draw.line([x + s / 2 + dx * 0.4, my + dy * 0.4,
                   x + s / 2 + dx, my + dy], fill=GOLD, width=4)


def icon_capitol(draw, x, y, s, color):
    """A dome on columns: the House of Representatives."""
    w = 4
    cx = x + s / 2
    draw.arc([cx - s * 0.26, y + s * 0.16, cx + s * 0.26, y + s * 0.62],
             180, 360, fill=color, width=w)
    draw.line([cx, y + s * 0.06, cx, y + s * 0.18], fill=color, width=w)
    draw.line([x + s * 0.14, y + s * 0.46, x + s * 0.86, y + s * 0.46],
              fill=color, width=w)
    for fx in (0.24, 0.42, 0.58, 0.76):
        draw.line([x + s * fx, y + s * 0.52, x + s * fx, y + s * 0.82],
                  fill=color, width=w)
    draw.line([x + s * 0.10, y + s * 0.88, x + s * 0.90, y + s * 0.88],
              fill=color, width=w)


def icon_castle(draw, x, y, s, color):
    """Tiered castle roofs: Shuri Castle."""
    w = 4
    cx = x + s / 2
    tiers = [(0.30, 0.30, 0.16), (0.52, 0.52, 0.20), (0.74, 0.74, 0.24)]
    for top, width_f, height_f in tiers:
        ty = y + s * top
        hw = s * width_f / 2
        draw.polygon([(cx - hw, ty), (cx, ty - s * height_f * 0.55),
                      (cx + hw, ty)], outline=color, width=w)
        draw.line([cx - hw * 0.62, ty, cx - hw * 0.62, ty + s * 0.10],
                  fill=color, width=w)
        draw.line([cx + hw * 0.62, ty, cx + hw * 0.62, ty + s * 0.10],
                  fill=color, width=w)
    draw.line([cx - s * 0.30, y + s * 0.92, cx + s * 0.30, y + s * 0.92],
              fill=color, width=w)


# ----------------------------------------------------------------- panels

def panel(draw, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=16,
                           fill=PANEL, outline=PANEL_EDGE, width=2)


def tag_row(draw, x, y, color, tag):
    draw.rounded_rectangle([x, y + 2, x + 15, y + 19], radius=3, fill=color)
    draw.text((x + 25, y), tag, font=F_TAG, fill=color)


def draw_hero_kyiv(draw, x, y, w, h):
    color = (240, 180, 60)
    panel(draw, x, y, w, h)
    icon_building(draw, x + w - 128, y + 18, 104, color)
    cx = x + 24
    tag_row(draw, cx, y + 20, color, "UKRAINE · KYIV REGION")
    cy = y + 58
    for line in wrap(draw, "Boy, 7, Pulled Alive From Rubble",
                     F_HERO_HEAD, w - 170):
        draw.text((cx, cy), line, font=F_HERO_HEAD, fill=PAPER)
        cy += 52
    result = "APARTMENT BLOCK DESTROYED"
    chip_w = int(draw.textlength(result, font=F_HERO_RESULT)) + 32
    draw.rounded_rectangle([cx, y + h - 62, cx + chip_w, y + h - 18],
                           radius=9, outline=color, width=2)
    draw.text((cx + 16, y + h - 52), result, font=F_HERO_RESULT, fill=color)


def draw_hero_markets(draw, x, y, w, h):
    # This story's visual symbol is the drop chart itself (bars below),
    # so the headline gets the panel's full width instead of an icon box.
    color = RED
    panel(draw, x, y, w, h)
    cx = x + 24
    tag_row(draw, cx, y + 20, color, "MARKETS · GLOBAL")
    cy = y + 58
    for line in wrap(draw, "AI Stock Sell-Off Shakes Markets",
                     F_HERO_HEAD, w - 48):
        draw.text((cx, cy), line, font=F_HERO_HEAD, fill=PAPER)
        cy += 52
    gy = y + h - 118
    scale = 40.0
    for label, value, bar_color in [("NIKKEI", -5.1, (226, 64, 54)),
                                    ("S&P 500", -3.7, (240, 140, 60))]:
        draw.text((cx, gy), label, font=F_CHART_LABEL, fill=PAPER)
        bar_x = cx + 118
        bar_w = int(abs(value) * scale)
        draw.rounded_rectangle([bar_x, gy + 1, bar_x + bar_w, gy + 23],
                               radius=5, fill=bar_color)
        draw.text((bar_x + bar_w + 10, gy - 2), "%.1f%%" % value,
                  font=F_CHART_VALUE, fill=bar_color)
        gy += 34
    draw.text((cx, gy + 2), "GOLD  ▲  JUMPS", font=F_CHART_LABEL, fill=GOLD)


def draw_mid(draw, x, y, w, h, icon, color, tag, headline, result):
    panel(draw, x, y, w, h)
    icon(draw, x + w - 104, y + 16, 82, color)
    cx = x + 24
    tag_row(draw, cx, y + 18, color, tag)
    cy = y + 54
    for line in wrap(draw, headline, F_MID_HEAD, w - 150):
        draw.text((cx, cy), line, font=F_MID_HEAD, fill=PAPER)
        cy += 41
    draw.text((cx, y + h - 44), result, font=F_MID_RESULT, fill=color)


def draw_low(draw, x, y, w, h, icon, color, tag, headline, result):
    panel(draw, x, y, w, h)
    icon(draw, x + 22, y + 18, 76, color)
    cx = x + 118
    tag_row(draw, cx, y + 18, color, tag)
    cy = y + 52
    for line in wrap(draw, headline, F_LOW_HEAD, w - 142):
        draw.text((cx, cy), line, font=F_LOW_HEAD, fill=PAPER)
        cy += 37
    draw.text((cx, y + h - 42), result, font=F_LOW_RESULT, fill=color)


# ------------------------------------------------------------------- page

def render():
    img = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(img)
    draw_texture(draw)

    # compressed masthead: one line, content gets the rest of the page
    draw.text((MARGIN, 20), "THE WORLD TODAY", font=F_TITLE, fill=PAPER)
    draw.text((W - MARGIN, 30), "ONE DAY · SIX STORIES", font=F_KICKER,
              fill=FAINT, anchor="ra")

    # the date as its own high-contrast badge, clear of the masthead
    badge_text = "MONDAY · 23 NOVEMBER 2026"
    bw = int(draw.textlength(badge_text, font=F_BADGE)) + 44
    draw.rounded_rectangle([MARGIN, 76, MARGIN + bw, 124], radius=12,
                           fill=RED)
    draw.text((MARGIN + 22, 87), badge_text, font=F_BADGE,
              fill=(255, 255, 255))

    # tier 1: the two hero stories
    hero_y, hero_h = 146, 330
    half = (W - 2 * MARGIN - 18) // 2
    draw_hero_kyiv(draw, MARGIN, hero_y, half, hero_h)
    draw_hero_markets(draw, MARGIN + half + 18, hero_y, half, hero_h)

    # tier 2: COP31 and the US-Iran standoff
    mid_y, mid_h = 494, 246
    draw_mid(draw, MARGIN, mid_y, half, mid_h, icon_globe, (64, 190, 120),
             "CLIMATE · ANTALYA", "COP31 Ends Without a Deal",
             "2 WEEKS OF TALKS — NO AGREEMENT")
    draw_mid(draw, MARGIN + half + 18, mid_y, half, mid_h, icon_clash,
             (235, 110, 80), "MIDDLE EAST · US-IRAN",
             "US-Iran Standoff Deepens",
             "TEHRAN'S TERMS: \"UNACCEPTABLE\"")

    # tier 3: the House and Shuri Castle, icon-led strips
    low_y, low_h = 758, 196
    draw_low(draw, MARGIN, low_y, half, low_h, icon_capitol,
             (170, 130, 240), "US POLITICS · WASHINGTON",
             "Democrats Win Back the House",
             "LARGEST MAJORITY IN DECADES")
    draw_low(draw, MARGIN + half + 18, low_y, half, low_h, icon_castle,
             (240, 120, 170), "JAPAN · OKINAWA",
             "Shuri Castle Reopens",
             "7 YEARS AFTER THE FIRE")

    draw.text((MARGIN, H - 26),
              "Compiled from news reports of 23 November 2026.",
              font=F_FOOT, fill=FAINT)
    return img


def main():
    img = render()
    png_path = os.path.join(HERE, "entry.png")
    img.save(png_path, format="PNG", optimize=True)
    with open(png_path, "rb") as fh:
        data = fh.read()
    b64 = base64.b64encode(data).decode("ascii")
    data_path = os.path.join(HERE, "entry_data.py")
    with open(data_path, "w", encoding="ascii") as fh:
        fh.write('"""The rendered entry image, carried as base64 text."""\n\n')
        fh.write('PNG_B64 = "%s"\n' % b64)
    print("entry.png bytes:", len(data))
    print("entry_data.py written")


if __name__ == "__main__":
    main()
