#!/usr/bin/env python3
"""Render the exact D0 versus certified D1 separation enclosures with Pillow."""

from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"

D0 = Fraction(2250986857014815, 2251799813685248)
ORIGINAL = (Fraction(32727, 16384), Fraction(32729, 16384))
INDEPENDENT = (Fraction(16363, 8192), Fraction(16365, 8192))

WIDTH, HEIGHT = 2200, 1180
BLUE = "#0072B2"
GREEN = "#009E73"
ORANGE = "#D55E00"
DARK = "#202124"
MID = "#5F6368"
GRID = "#DADCE0"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        ["/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else
        ["/System/Library/Fonts/Supplemental/Verdana.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for name in names:
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


F_TITLE = font(45, True)
F_SUB = font(24)
F_PANEL = font(29, True)
F_LABEL = font(23)
F_TICK = font(19)
F_NOTE = font(20)
F_SMALL = font(17)


def xpos(value: float, left: int, right: int, lo: float, hi: float) -> float:
    return left + (value - lo) * (right - left) / (hi - lo)


def centered(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str,
             used_font, fill=DARK) -> None:
    box = draw.textbbox((0, 0), text, font=used_font)
    draw.text((xy[0] - (box[2] - box[0]) / 2, xy[1] - (box[3] - box[1]) / 2),
              text, font=used_font, fill=fill)


def diamond(draw: ImageDraw.ImageDraw, x: float, y: float, radius: int, fill: str) -> None:
    draw.polygon([(x, y - radius), (x + radius, y), (x, y + radius),
                  (x - radius, y)], fill=fill)


def axis(draw: ImageDraw.ImageDraw, left: int, right: int, y: int,
         lo: float, hi: float, ticks: list[float]) -> None:
    draw.line((left, y, right, y), fill=DARK, width=3)
    for value in ticks:
        x = xpos(value, left, right, lo, hi)
        draw.line((x, y - 310, x, y), fill=GRID, width=2)
        draw.line((x, y, x, y + 10), fill=DARK, width=2)
        centered(draw, (x, y + 38), f"{value:.4f}", F_TICK, MID)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    draw.text((90, 55), "Certified separation mismatch in the fixed reduced model",
              font=F_TITLE, fill=DARK)
    draw.text((92, 120),
              "Exact D2A separation compared with the original and producer-independent D1 enclosures",
              font=F_SUB, fill=MID)

    gl, gr, gt, gb = 150, 1180, 250, 760
    draw.rounded_rectangle((gl - 45, gt - 55, gr + 35, gb + 105), radius=18,
                           outline=GRID, width=2)
    draw.text((gl - 5, gt - 15), "A. Global scale", font=F_PANEL, fill=DARK)
    axis(draw, gl, gr, gb, 0.93, 2.045, [1.0, 1.25, 1.5, 1.75, 2.0])
    y0, y1 = 610, 405
    draw.text((gl - 10, y0 - 65), "source-bound fixed D0", font=F_LABEL, fill=ORANGE)
    draw.text((gl - 10, y1 - 65), "certified D1 event", font=F_LABEL, fill=BLUE)
    x0 = xpos(float(D0), gl, gr, 0.93, 2.045)
    x1 = xpos(float(sum(ORIGINAL, Fraction(0)) / 2), gl, gr, 0.93, 2.045)
    diamond(draw, x0, y0, 16, ORANGE)
    draw.ellipse((x1 - 16, y1 - 16, x1 + 16, y1 + 16), fill=BLUE)
    draw.line((x0 + 24, 520, x1 - 24, 520), fill=MID, width=4)
    draw.polygon([(x1 - 24, 520), (x1 - 42, 508), (x1 - 42, 532)], fill=MID)
    centered(draw, ((x0 + x1) / 2, 480), "certified gap > 0.9978585", F_NOTE, DARK)
    centered(draw, ((x0 + x1) / 2, 568),
             "D / D0 in [1.998218966, 1.998341081]", F_NOTE, DARK)
    centered(draw, ((gl + gr) / 2, gb + 88), "proper separation D  (ell = 1)", F_LABEL, DARK)

    zl, zr, zt, zb = 1325, 2070, 250, 760
    draw.rounded_rectangle((zl - 45, zt - 55, zr + 35, zb + 105), radius=18,
                           outline=GRID, width=2)
    draw.text((zl - 5, zt - 15), "B. D1 enclosure detail", font=F_PANEL, fill=DARK)
    zlo, zhi = 1.99739, 1.99773
    axis(draw, zl, zr, zb, zlo, zhi, [1.9974, 1.9975, 1.9976, 1.9977])
    yi, yo = 590, 390
    draw.text((zl - 5, yi - 62), "independent, 16,384 steps", font=F_LABEL, fill=BLUE)
    draw.text((zl - 5, yo - 62), "original, 32,768 steps", font=F_LABEL, fill=GREEN)
    for bounds, y, color, width in (
        (INDEPENDENT, yi, BLUE, 20),
        (ORIGINAL, yo, GREEN, 14),
    ):
        lo, hi = (xpos(float(value), zl, zr, zlo, zhi) for value in bounds)
        draw.line((lo, y, hi, y), fill=color, width=width)
        draw.ellipse((lo - 9, y - 9, lo + 9, y + 9), fill=color)
        draw.ellipse((hi - 9, y - 9, hi + 9, y + 9), fill=color)
    centered(draw, ((zl + zr) / 2, zb + 88), "proper separation D  (zoomed)", F_LABEL, DARK)

    draw.line((90, 940, 2110, 940), fill=GRID, width=2)
    draw.text((95, 972),
              "Interpretation: the independent enclosure contains the narrower original certificate; both are disjoint from D0.",
              font=F_NOTE, fill=DARK)
    draw.text((95, 1022),
              "The comparison is an exact interval consequence of two static boundary placements, not a time evolution.",
              font=F_NOTE, fill=DARK)
    draw.text((95, 1080),
              "Source: sealed D1 and D2A certificates; exact rational arithmetic rechecked on macOS and Linux.",
              font=F_SMALL, fill=MID)

    png = OUT / "certified_separation_mismatch.png"
    pdf = OUT / "certified_separation_mismatch.pdf"
    image.save(png, format="PNG", dpi=(240, 240), optimize=True)
    image.save(pdf, format="PDF", resolution=240.0)


if __name__ == "__main__":
    main()
