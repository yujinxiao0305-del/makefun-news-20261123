#!/usr/bin/env python3
"""Render the 23 November 2026 world-news summary image.

This builder runs at development time only (it uses Pillow). It draws a
dark, newspaper-style infographic at 1024x1024, saves entry.png, and then
writes entry_data.py holding the PNG as base64 text so that the shipped
entrypoint main.py needs nothing beyond the Python standard library.
"""

import base64
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/liberation"

W = 1024
H = 1024

INK = (16, 20, 24)          # page background
PANEL = (27, 34, 43)        # panel background
PANEL_EDGE = (58, 70, 84)   # panel border
PAPER = (238, 240, 242)     # main text
SOFT = (178, 188, 199)      # secondary text
FAINT = (120, 132, 146)     # footer text
RED = (224, 62, 52)         # masthead accent

MARGIN = 36
GAP = 20


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = font("LiberationSerif-Bold.ttf", 64)
F_DATE = font("LiberationSans-Bold.ttf", 27)
F_SUB = font("LiberationSans-Regular.ttf", 24)
F_TAG = font("LiberationSans-Bold.ttf", 20)
F_HEAD = font("LiberationSans-Bold.ttf", 33)
F_BODY = font("LiberationSans-Regular.ttf", 24)
F_FOOT = font("LiberationSans-Regular.ttf", 19)


STORIES = [
    {
        "tag": "CLIMATE  ·  ANTALYA",
        "color": (64, 190, 120),
        "headline": "COP31 Ends Without a Deal in Antalya",
        "body": "Two weeks of climate talks closed with no agreement, "
                "as nations split over how fast to phase out fossil fuels.",
    },
    {
        "tag": "UKRAINE  ·  KYIV REGION",
        "color": (240, 180, 60),
        "headline": "Boy, 7, Pulled Alive From Kyiv Rubble",
        "body": "A Russian strike destroyed an apartment block. "
                "Rescuers freed the boy, seven, alive.",
    },
    {
        "tag": "MARKETS  ·  GLOBAL",
        "color": (90, 160, 240),
        "headline": "AI Stock Sell-Off Shakes World Markets",
        "body": "Tech shares tumbled — Nikkei -5.1%, S&P 500 -3.7% — "
                "as investors fled AI bets and gold jumped.",
    },
    {
        "tag": "MIDDLE EAST  ·  US-IRAN",
        "color": (235, 110, 80),
        "headline": "US-Iran Standoff Deepens Over Deal",
        "body": "Trump said Tehran wants an agreement but called its "
                "terms \"unacceptable\", raising tensions again.",
    },
    {
        "tag": "US POLITICS  ·  WASHINGTON",
        "color": (170, 130, 240),
        "headline": "Democrats Win Back the House",
        "body": "Democrats seized the House of Representatives with "
                "their largest majority in decades, reports said.",
    },
    {
        "tag": "JAPAN  ·  OKINAWA",
        "color": (240, 120, 170),
        "headline": "Shuri Castle Rises Again in Okinawa",
        "body": "Seven years after fire gutted the beloved landmark, "
                "the rebuilt Shuri Castle reopened to the public.",
    },
]


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap measured in pixels."""
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


def draw_panel(draw, x, y, w, h, story):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14,
                           fill=PANEL, outline=PANEL_EDGE, width=2)
    cx = x + 24
    cy = y + 20
    # category tag with a small colour chip
    draw.rounded_rectangle([cx, cy + 2, cx + 14, cy + 18], radius=3,
                           fill=story["color"])
    draw.text((cx + 24, cy), story["tag"], font=F_TAG, fill=story["color"])
    cy += 34
    for line in wrap(draw, story["headline"], F_HEAD, w - 48):
        draw.text((cx, cy), line, font=F_HEAD, fill=PAPER)
        cy += 39
    cy += 5
    for line in wrap(draw, story["body"], F_BODY, w - 48):
        draw.text((cx, cy), line, font=F_BODY, fill=SOFT)
        cy += 30


def render():
    img = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(img)

    # masthead
    draw.rectangle([0, 0, W, 8], fill=RED)
    y = 30
    draw.text((MARGIN, y), "THE WORLD TODAY", font=F_TITLE, fill=PAPER)
    title_w = draw.textlength("THE WORLD TODAY", font=F_TITLE)
    draw.text((MARGIN, y + 78), "MONDAY · 23 NOVEMBER 2026",
              font=F_DATE, fill=RED)
    draw.text((W - MARGIN, y + 78), "ONE DAY · SIX STORIES", font=F_DATE,
              fill=FAINT, anchor="ra")
    y += 122
    draw.line([MARGIN, y, W - MARGIN, y], fill=PANEL_EDGE, width=2)
    y += 14
    draw.text((MARGIN, y),
              "The day's biggest stories from every continent, in one picture.",
              font=F_SUB, fill=SOFT)
    y += 44

    # panels: two columns, three rows
    footer_h = 40
    grid_top = y
    grid_bottom = H - MARGIN - footer_h
    rows = 3
    panel_h = (grid_bottom - grid_top - GAP * (rows - 1)) // rows
    panel_w = (W - 2 * MARGIN - GAP) // 2
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        px = MARGIN + col * (panel_w + GAP)
        py = grid_top + row * (panel_h + GAP)
        draw_panel(draw, px, py, panel_w, panel_h, story)

    draw.text((MARGIN, H - MARGIN - 24),
              "Compiled from news reports of 23 November 2026.",
              font=F_FOOT, fill=FAINT)
    draw.text((W - MARGIN, H - MARGIN - 24), "23 NOV 2026",
              font=F_FOOT, fill=FAINT, anchor="ra")
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
