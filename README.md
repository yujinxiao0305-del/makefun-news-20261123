# World News of 23 November 2026 — in one image

Entry for the make.fun competition `news-image-20261123`
("Sum up 23 November's world news in one image").

## What it shows

A dark, newspaper-style front page dated **Monday, 23 November 2026**
with the day's six biggest stories:

1. COP31 ends without a deal in Antalya amid fossil-fuel divisions.
2. A 7-year-old boy is pulled alive from a destroyed Kyiv-region
   apartment block after a Russian strike.
3. An AI stock sell-off shakes world markets (Nikkei -5.1%,
   S&P 500 -3.7%, gold jumps).
4. The US-Iran standoff deepens over a possible deal.
5. Democrats win back the US House of Representatives.
6. Shuri Castle in Okinawa reopens, rebuilt seven years after the fire.

## How it runs

`main.py` uses only the Python standard library. It decodes the image
bytes carried in `entry_data.py` and writes them to
`$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png`). Every run
produces byte-identical output.

## How the image was made

`build_image.py` (development-time only, uses Pillow) draws the
infographic with a TrueType font, saves `entry.png`, and regenerates
`entry_data.py` from it.

## License

MIT — see `LICENSE`.
