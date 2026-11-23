#!/usr/bin/env python3
"""THE WORLD IN ONE IMAGE - the world's news of Monday 23 November 2026 in one PNG.

Entry for make.fun's "news-image-20261123" bounty. Pure Python 3 standard
library: the front page is drawn pixel by pixel into an RGB framebuffer with
a built-in 5x7 bitmap font and written out with a hand-rolled PNG encoder
(zlib + struct). No network, no external assets, fully deterministic: every
run writes exactly the same bytes to entry.png (next to this script).
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 234)
INK = (20, 22, 26)
RED = (178, 32, 42)
DARK = (58, 58, 58)
HAIR = (178, 171, 152)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 pixels, '#' = ink.
# ---------------------------------------------------------------------------
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
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".####"),
    "f": ("..##.", ".#...", "#####", ".#...", ".#...", ".#...", ".#..."),
    "g": (".....", ".....", ".####", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "####.", "#....", "#...."),
    "q": (".....", ".....", ".####", "#...#", ".####", "....#", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "#####", ".#...", ".#...", ".#..#", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
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
    ",": (".....", ".....", ".....", ".##..", ".##..", ".##..", ".#..."),
    ";": (".....", ".....", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".....", ".##..", ".....", ".....", ".##..", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
}

# ---------------------------------------------------------------------------
# Page content: the day's eight stories (see sources.md for the reporting).
# ---------------------------------------------------------------------------
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

MARGIN = 36
CONTENT_W = W - 2 * MARGIN


class Canvas:
    def __init__(self):
        self.px = bytearray(bytes(PAPER) * (W * H))

    def rect(self, x, y, w, h, color):
        row = bytes(color) * w
        for yy in range(y, y + h):
            off = (yy * W + x) * 3
            self.px[off:off + 3 * w] = row

    def text_width(self, text, scale):
        if not text:
            return 0
        return len(text) * 6 * scale - scale

    def text(self, x, y, text, scale, color):
        for ch in text:
            glyph = FONT[ch]
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "#":
                        self.rect(x + c * scale, y + r * scale,
                                  scale, scale, color)
            x += 6 * scale
        return x

    def text_centered(self, y, text, scale, color):
        x = (W - self.text_width(text, scale)) // 2
        self.text(x, y, text, scale, color)

    def wrap(self, text, scale, max_width):
        """Split text into lines that fit max_width at the given scale."""
        max_chars = (max_width + scale) // (6 * scale)
        lines = []
        current = ""
        for word in text.split(" "):
            trial = word if not current else current + " " + word
            if len(trial) <= max_chars:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines


def draw():
    cv = Canvas()
    y = 28

    # Masthead.
    cv.text_centered(y, MASTHEAD, 5, INK)
    y += 35 + 9
    # Newspaper double rule.
    cv.rect(MARGIN, y, CONTENT_W, 5, INK)
    cv.rect(MARGIN, y + 8, CONTENT_W, 2, INK)
    y += 10 + 10

    # Dateline.
    cv.text_centered(y, DATELINE, 4, RED)
    y += 28 + 12

    # Lead story, with a red side bar matched to the block's real height.
    lead_x = MARGIN + 24
    lead_lines = cv.wrap(LEAD_KICKER, 3, W - lead_x - MARGIN)
    bar_h = 42 + 8 + len(lead_lines) * 21 + (len(lead_lines) - 1) * 3
    cv.rect(MARGIN, y, 10, bar_h, RED)
    cv.text(lead_x, y, LEAD_HEADLINE, 6, INK)
    y += 42 + 8
    for line in lead_lines:
        cv.text(lead_x, y, line, 3, DARK)
        y += 21 + 3
    y += 10

    # The other seven stories. Kickers wrap to the headline column width so
    # no line ever crosses the right margin.
    for i, (headline, kicker) in enumerate(STORIES):
        cv.rect(MARGIN, y, CONTENT_W, 2, HAIR)
        y += 8
        num = str(i + 1) + "."
        cv.text(MARGIN, y, num, 4, RED)
        head_x = MARGIN + 48
        head_lines = cv.wrap(headline, 4, W - head_x - MARGIN)
        for line in head_lines:
            cv.text(head_x, y, line, 4, INK)
            y += 28 + 3
        y += 1
        for line in cv.wrap(kicker, 3, W - head_x - MARGIN):
            cv.text(head_x, y, line, 3, DARK)
            y += 21 + 3
        y += 9

    # Closing rule.
    cv.rect(MARGIN, y, CONTENT_W, 5, INK)
    return cv


def encode_png(cv):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)  # filter type 0 (None) for every row
        raw += cv.px[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    return png


def main():
    png = encode_png(draw())
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    main()
