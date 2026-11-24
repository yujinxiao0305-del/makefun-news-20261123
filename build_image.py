#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render v2 of the 23 November 2026 world-news summary image.

Development-time builder (uses Pillow). Layout: a compact masthead with
a big date, one dominant hero story (the AI stock sell-off) with a bar
chart of the index drops, a dotted world map built from latitude-band
land spans marking where each story happened, and five compact numbered
story cards. It saves entry.png and rewrites entry_data.py with the PNG
as base64 text, so the shipped entrypoint main.py needs only the
Python standard library.
"""

import base64
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/liberation"

W = 1024
H = 1024

INK = (14, 18, 22)
PANEL = (26, 33, 42)
PANEL_EDGE = (58, 70, 84)
PAPER = (240, 242, 244)
SOFT = (183, 192, 203)
FAINT = (118, 130, 144)
RED = (226, 64, 54)
LAND = (84, 104, 126)
OCEAN_DOT = (30, 40, 52)

MARGIN = 36


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = font("LiberationSerif-Bold.ttf", 56)
F_DATE = font("LiberationSans-Bold.ttf", 31)
F_DATE_SMALL = font("LiberationSans-Bold.ttf", 19)
F_HERO_TAG = font("LiberationSans-Bold.ttf", 21)
F_HERO_HEAD = font("LiberationSans-Bold.ttf", 54)
F_HERO_BODY = font("LiberationSans-Regular.ttf", 25)
F_CHART_LABEL = font("LiberationSans-Bold.ttf", 23)
F_CHART_VALUE = font("LiberationSans-Bold.ttf", 27)
F_CHART_TITLE = font("LiberationSans-Bold.ttf", 19)
F_GOLD = font("LiberationSans-Bold.ttf", 19)
F_MAP_TITLE = font("LiberationSans-Bold.ttf", 20)
F_NUM = font("LiberationSans-Bold.ttf", 18)
F_CARD_TAG = font("LiberationSans-Bold.ttf", 17)
F_CARD_HEAD = font("LiberationSans-Bold.ttf", 27)
F_CARD_BODY = font("LiberationSans-Regular.ttf", 18)
F_FOOT = font("LiberationSans-Regular.ttf", 17)


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


# ---------------------------------------------------------------- hero

def draw_hero(draw, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=16,
                           fill=PANEL, outline=PANEL_EDGE, width=2)
    cx = x + 26
    cy = y + 20
    draw.rounded_rectangle([cx, cy + 2, cx + 15, cy + 19], radius=3, fill=RED)
    draw.text((cx + 25, cy), "3 · MARKETS — THE DAY'S BIGGEST STORY",
              font=F_HERO_TAG, fill=RED)
    cy += 34
    for line in ["AI Stock Sell-Off", "Shakes World", "Markets"]:
        draw.text((cx, cy), line, font=F_HERO_HEAD, fill=PAPER)
        cy += 60
    cy += 6
    for line in wrap(draw, "Investors flee AI bets as tech shares tumble "
                           "and gold jumps.", F_HERO_BODY, 500):
        draw.text((cx, cy), line, font=F_HERO_BODY, fill=SOFT)
        cy += 31

    # bar chart of the index drops, right-hand zone
    gx = x + 612
    gy = y + 52
    draw.text((gx, gy), "THE DAY'S DROP", font=F_CHART_TITLE, fill=FAINT)
    gy += 32
    scale = 42.0  # pixels per percentage point
    rows = [("NIKKEI 225", -5.1, (226, 64, 54)),
            ("S&P 500", -3.7, (240, 140, 60))]
    for label, value, color in rows:
        draw.text((gx, gy), label, font=F_CHART_LABEL, fill=PAPER)
        gy += 30
        bar_w = int(abs(value) * scale)
        draw.rounded_rectangle([gx, gy, gx + bar_w, gy + 25], radius=5,
                               fill=color)
        draw.text((gx + bar_w + 12, gy - 3), "%.1f%%" % value,
                  font=F_CHART_VALUE, fill=color)
        gy += 46
    gy += 4
    draw.rounded_rectangle([gx, gy, gx + 314, gy + 42], radius=8,
                           outline=(240, 190, 60), width=2)
    draw.text((gx + 15, gy + 10), "GOLD  ▲  safe-haven rush",
              font=F_GOLD, fill=(240, 190, 60))


# ----------------------------------------------------------------- map

# Land as longitude spans per latitude band (26 bands, centres from
# about +75 to about -55 degrees). Stylised but geographically placed.
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

MAP_LON0, MAP_LON1 = -170.0, 190.0
MAP_LAT0, MAP_LAT1 = 78.0, -58.0
MAP_ROWS = len(LAND_SPANS)
MAP_COLS = 104

# number, lon, lat, colour, pixel nudge (dx, dy) to separate near markers
MARKERS = [
    (1, 30.7, 36.9, (64, 190, 120), (-7, 7)),     # Antalya — COP31
    (2, 30.5, 50.4, (240, 180, 60), (0, -5)),     # Kyiv region
    (3, 139.7, 35.7, (226, 64, 54), (0, 0)),      # Tokyo — Nikkei
    (4, 51.4, 35.7, (235, 110, 80), (0, 0)),      # Tehran
    (5, -77.0, 38.9, (170, 130, 240), (5, -8)),   # Washington DC
    (6, 127.8, 26.3, (240, 120, 170), (0, 0)),    # Okinawa — Shuri Castle
]


def draw_map(draw, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=16,
                           fill=PANEL, outline=PANEL_EDGE, width=2)
    draw.text((x + 26, y + 15), "WHERE IT HAPPENED — SIX STORIES, SIX PLACES",
              font=F_MAP_TITLE, fill=SOFT)
    mx = x + 30
    my = y + 50
    mw = w - 60
    mh = h - 50 - 12
    cell_x = mw / MAP_COLS
    cell_y = mh / MAP_ROWS
    land = [[False] * MAP_COLS for _ in range(MAP_ROWS)]
    for r, spans in enumerate(LAND_SPANS):
        for lon_a, lon_b in spans:
            c0 = int((lon_a - MAP_LON0) / (MAP_LON1 - MAP_LON0) * MAP_COLS)
            c1 = int((lon_b - MAP_LON0) / (MAP_LON1 - MAP_LON0) * MAP_COLS)
            for c in range(max(0, c0), min(MAP_COLS, c1 + 1)):
                land[r][c] = True
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            px = mx + c * cell_x + cell_x / 2
            py = my + r * cell_y + cell_y / 2
            if land[r][c]:
                draw.ellipse([px - 2.7, py - 2.7, px + 2.7, py + 2.7],
                             fill=LAND)
            else:
                draw.ellipse([px - 1.0, py - 1.0, px + 1.0, py + 1.0],
                             fill=OCEAN_DOT)
    for num, lon, lat, color, (dx, dy) in MARKERS:
        px = mx + (lon - MAP_LON0) / (MAP_LON1 - MAP_LON0) * mw + dx
        py = my + (MAP_LAT0 - lat) / (MAP_LAT0 - MAP_LAT1) * mh + dy
        draw.ellipse([px - 13, py - 13, px + 13, py + 13], fill=color,
                     outline=PAPER, width=2)
        draw.text((px, py - 9), str(num), font=F_NUM, fill=(16, 20, 24),
                  anchor="ma")


# ---------------------------------------------------------------- cards

CARDS = [
    {"num": 1, "tag": "CLIMATE · ANTALYA", "color": (64, 190, 120),
     "headline": "COP31 Ends Without a Deal",
     "body": "Stalled over fossil fuels."},
    {"num": 2, "tag": "UKRAINE · KYIV REGION", "color": (240, 180, 60),
     "headline": "Boy, 7, Pulled Alive From Rubble",
     "body": "Destroyed by a Russian strike."},
    {"num": 4, "tag": "MIDDLE EAST · US-IRAN", "color": (235, 110, 80),
     "headline": "US-Iran Standoff Deepens",
     "body": "Tehran's terms: \"unacceptable\"."},
    {"num": 5, "tag": "US POLITICS · WASHINGTON", "color": (170, 130, 240),
     "headline": "Democrats Win Back the House",
     "body": "Their largest House majority in decades."},
    {"num": 6, "tag": "JAPAN · OKINAWA", "color": (240, 120, 170),
     "headline": "Shuri Castle Reopens After 7 Years",
     "body": "Beloved landmark rebuilt after the fire."},
]


def draw_card(draw, x, y, w, h, card):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14,
                           fill=PANEL, outline=PANEL_EDGE, width=2)
    cx = x + 18
    cy = y + 12
    color = card["color"]
    draw.ellipse([cx, cy, cx + 24, cy + 24], fill=color)
    draw.text((cx + 12, cy + 2), str(card["num"]), font=F_NUM,
              fill=(16, 20, 24), anchor="ma")
    draw.text((cx + 34, cy + 2), card["tag"], font=F_CARD_TAG, fill=color)
    cy += 32
    for line in wrap(draw, card["headline"], F_CARD_HEAD, w - 36)[:2]:
        draw.text((cx, cy), line, font=F_CARD_HEAD, fill=PAPER)
        cy += 33
    draw.text((cx, cy + 2), card["body"], font=F_CARD_BODY, fill=SOFT)


# ---------------------------------------------------------------- page

def render():
    img = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 8], fill=RED)
    draw.text((MARGIN, 24), "THE WORLD TODAY", font=F_TITLE, fill=PAPER)
    draw.text((W - MARGIN, 28), "MONDAY", font=F_DATE_SMALL, fill=FAINT,
              anchor="ra")
    draw.text((W - MARGIN, 50), "23 NOVEMBER 2026", font=F_DATE, fill=RED,
              anchor="ra")
    draw.line([MARGIN, 112, W - MARGIN, 112], fill=PANEL_EDGE, width=2)

    draw_hero(draw, MARGIN, 126, W - 2 * MARGIN, 312)
    draw_map(draw, MARGIN, 452, W - 2 * MARGIN, 216)

    top = 682
    row_h = 138
    gap = 14
    widths_top = [(W - 2 * MARGIN - 2 * gap) // 3] * 3
    x = MARGIN
    for card, cw in zip(CARDS[:3], widths_top):
        draw_card(draw, x, top, cw, row_h, card)
        x += cw + gap
    widths_bottom = [(W - 2 * MARGIN - gap) // 2] * 2
    x = MARGIN
    for card, cw in zip(CARDS[3:], widths_bottom):
        draw_card(draw, x, top + row_h + gap, cw, row_h, card)
        x += cw + gap

    draw.text((MARGIN, H - 28),
              "Compiled from news reports of 23 November 2026.",
              font=F_FOOT, fill=FAINT)
    draw.text((W - MARGIN, H - 28), "23 NOV 2026", font=F_FOOT,
              fill=FAINT, anchor="ra")
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
