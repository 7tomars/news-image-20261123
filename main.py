#!/usr/bin/env python3
"""The World in One Image -- Monday 23 November 2026.

A self-contained, standard-library-only Python 3 program that renders a
one-page newspaper front page as a 1024x1024 PNG. The page is drawn pixel
by pixel into an RGB framebuffer with a built-in 5x7 bitmap font and
written out with a hand-rolled PNG encoder (zlib + struct). The render is
fully deterministic: every run produces byte-identical output.

The image is written as entry.png into the directory named by the
MAKEFUN_OUTPUT_DIR environment variable, or into the current directory
when that variable is unset.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- canvas --

WIDTH = 1024
HEIGHT = 1024

CREAM = (244, 239, 228)   # page background
INK = (26, 24, 20)        # body text
RED = (178, 32, 32)       # dateline, lead bar, story numbers
RULE = (120, 114, 100)    # thin rules between stories

MARGIN = 64               # left/right page margin
CONTENT_W = WIDTH - 2 * MARGIN

# ------------------------------------------------------------------ font --
# 5x7 bitmap glyphs, one string per row, '#' = ink. Only the characters the
# page actually uses are defined; text is upper-cased before rendering.

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
}

GLYPH_W = 5
GLYPH_H = 7

# --------------------------------------------------------------- content --

MASTHEAD = "THE WORLD IN ONE IMAGE"
DATELINE = "MONDAY 23 NOVEMBER 2026"

LEAD_HEADLINE = "RUSSIAN WARSHIP SUNK"
LEAD_KICKER = "Sea drones sink corvette Merkury in Benghazi port"

STORIES = [
    ("BIGGEST US HOUSE MAJORITY SINCE 1992",
     "Democrats hit 258 seats after Carolina flip"),
    ("PRABOWO TO NAME VP CANDIDATES TODAY",
     "Two names go to the MPR; parliament votes in December"),
    ("M6.5 QUAKE STRIKES DEEP BELOW VANUATU",
     "601 km down; no tsunami threat, agencies say"),
    ("OIL SLIPS AS AI SELLOFF SPREADS",
     "Brent at 92.29 dollars; Gulf attacks cap losses"),
    ("SEARCH GOES ON IN DYMER RUBBLE",
     "Boy, 7, pulled alive after 14 hours under rubble"),
    ("FIFA TO CONFIRM UK AS 2035 HOSTS",
     "Unopposed four-nation bid; first UK cup since 1966"),
    ("NEW ZEALAND HOLD ON FOR DRAW",
     "Mitchell, Phillips bat out day five to deny India"),
]

# -------------------------------------------------------------- drawing ---

def new_framebuffer():
    """A WIDTH x HEIGHT RGB buffer filled with the page colour."""
    return bytearray(bytes(CREAM) * (WIDTH * HEIGHT))


def fill_rect(buf, x, y, w, h, color):
    row = bytes(color) * w
    for yy in range(y, y + h):
        start = (yy * WIDTH + x) * 3
        buf[start:start + w * 3] = row


def text_width(text, scale, tracking=1):
    """Pixel width of a string rendered at the given integer scale.

    tracking is the letter spacing in font units (1 = the standard one
    blank column between glyphs); wider values letterspace the line.
    """
    if not text:
        return 0
    return (len(text) * (GLYPH_W + tracking) - tracking) * scale


def draw_text(buf, x, y, text, scale, color, bold=False, tracking=1):
    """Draw text with its top-left corner at (x, y); return its width."""
    extra = 1 if bold else 0  # bold = strokes one pixel wider per unit
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "#":
                    fill_rect(buf,
                              cx + col_i * scale, y + row_i * scale,
                              scale + extra, scale, color)
        cx += (GLYPH_W + tracking) * scale
    return text_width(text, scale, tracking)


def draw_centered(buf, y, text, scale, color, bold=False, tracking=1):
    draw_text(buf, (WIDTH - text_width(text, scale, tracking)) // 2, y,
              text, scale, color, bold, tracking)


def wrap(text, scale, max_width):
    """Greedy word wrap so every line fits within max_width pixels."""
    lines = []
    current = ""
    for word in text.upper().split():
        trial = word if not current else current + " " + word
        if current and text_width(trial, scale) > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines

# ---------------------------------------------------------------- layout --

def render():
    buf = new_framebuffer()

    # Masthead and dateline.
    y = 54
    draw_centered(buf, y, MASTHEAD, 6, INK, bold=True)
    y += GLYPH_H * 6 + 16
    draw_centered(buf, y, DATELINE, 3, RED, bold=True, tracking=3)
    y += GLYPH_H * 3 + 20

    # Thick black rule under the header.
    fill_rect(buf, MARGIN, y, CONTENT_W, 5, INK)
    y += 30

    # Lead story: red bar down the left, headline in large type, kicker
    # wrapped underneath.
    lead_x = MARGIN + 32
    lead_w = WIDTH - MARGIN - lead_x
    kicker_lines = wrap(LEAD_KICKER, 3, lead_w)
    lead_h = GLYPH_H * 5 + 12 + len(kicker_lines) * (GLYPH_H * 3 + 8) - 8
    fill_rect(buf, MARGIN, y, 12, lead_h, RED)
    draw_text(buf, lead_x, y, LEAD_HEADLINE, 5, INK, bold=True)
    ky = y + GLYPH_H * 5 + 12
    for line in kicker_lines:
        draw_text(buf, lead_x, ky, line, 3, INK)
        ky += GLYPH_H * 3 + 8
    y += lead_h + 26

    # Numbered stories, thin rules between them.
    num_w = text_width("0", 3) + 14
    story_x = MARGIN + num_w
    story_w = WIDTH - MARGIN - story_x
    for i, (headline, kicker) in enumerate(STORIES):
        if i > 0:
            fill_rect(buf, MARGIN, y, CONTENT_W, 2, RULE)
            y += 24
        draw_text(buf, MARGIN, y, str(i + 1), 3, RED, bold=True)
        draw_text(buf, story_x, y, headline, 3, INK, bold=True)
        ky = y + GLYPH_H * 3 + 8
        for line in wrap(kicker, 2, story_w):
            draw_text(buf, story_x, ky, line, 2, INK)
            ky += GLYPH_H * 2 + 6
        y = ky + 16

    # Black rule at the bottom of the page.
    fill_rect(buf, MARGIN, y + 6, CONTENT_W, 5, INK)
    return buf

# ------------------------------------------------------------ PNG output --

def encode_png(buf):
    """Encode the RGB framebuffer as PNG bytes (filter 0, one IDAT)."""
    raw = bytearray()
    stride = WIDTH * 3
    for yy in range(HEIGHT):
        raw.append(0)
        raw += buf[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    png = encode_png(render())
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)
    print(len(png))


if __name__ == "__main__":
    main()
