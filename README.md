# makefun-news-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/yujinxiao0305-del/makefun-news-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/yujinxiao0305-del/makefun-news-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

This program generates one image that sums up the world's news of
Monday, 23 November 2026: a dark, newspaper-style front page carrying
the day's six biggest stories, drawn as a single 1024x1024 picture.

## Run it

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## What it shows

1. COP31 ends without a deal in Antalya amid fossil-fuel divisions.
2. A 7-year-old boy is pulled alive from a destroyed Kyiv-region
   apartment block after a Russian strike.
3. An AI stock sell-off shakes world markets (Nikkei -5.1%,
   S&P 500 -3.7%, gold jumps).
4. The US-Iran standoff deepens over a possible deal.
5. Democrats win back the US House of Representatives.
6. Shuri Castle in Okinawa reopens, rebuilt seven years after the fire.

## How it works

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

<sub>Entered on [make.fun](https://make.fun/?ref=2c7zd5b0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
