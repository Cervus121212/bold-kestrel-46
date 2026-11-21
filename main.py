#!/usr/bin/env python3
"""THE WORLD TODAY - Saturday 21 November 2026.
One-page world news front page, drawn from scratch with a hand-built
5x7 bitmap font and a stdlib-only PNG encoder. No network, no PIL.
Render: python3 main.py  ->  entry.png (1024x1024, deterministic).
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---- palette: paper + three inks only -------------------------------------
PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (155, 27, 27)
NAVY = (27, 58, 92)
TINT = (232, 224, 206)   # pale tint of the paper, for bands

# ---- 5x7 bitmap font (all caps; '#' = ink, '.' = empty) -------------------
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '\u2022': ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    '\u2019': ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '\u2013': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
}


def char_adv(scale):
    return 6 * scale


def text_w(s, scale):
    return len(s) * char_adv(scale) - scale if s else 0


def wrap(s, scale, max_w):
    """Greedy word wrap; returns list of lines, each fitting max_w."""
    words = s.split(' ')
    lines, cur = [], ''
    for w_ in words:
        trial = w_ if not cur else cur + ' ' + w_
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

# ---- canvas -----------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:(i + (x1 - x0) * 3)] = bytes(c) * (x1 - x0)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d2 <= r * r:
                    self.set(xx, yy, c)

    def text(self, x, y, s, scale, c):
        """Draw string s, top-left at (x, y). Unknown chars raise."""
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                raise ValueError('missing glyph for %r' % ch)
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += char_adv(scale)
        return cx

    def text_c(self, y, s, scale, c, cx0=36, cx1=988):
        """Centred text between cx0 and cx1."""
        w_ = text_w(s, scale)
        self.text(cx0 + (cx1 - cx0 - w_) // 2, y, s, scale, c)


def png_bytes(cv):
    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return out
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))

# ---- copy: 9 stories, all verified 21 Nov 2026 ------------------------------
# 01 hero: COP31 overtime, Antalya (Reuters / AP, 21 Nov 01:56 UTC).
# 02 Kyiv barrage + missiles land in Poland (Reuters / AFP).
# 03 Denmark expels Russian attache over alleged plot (AP).
# 04 Wall Street AI sell-off, Friday close (Reuters).
# 05 BepiColombo enters Mercury orbit, 21 Nov (ESA).
# 06 Cyclone Akvan aftermath, Odisha (IMD / PTI).
# 07 Saudi intercepts of Houthi missiles at Riyadh (Al Arabiya).
# 08 Trump press conference after Shenzhen summit (Reuters).
# 09 Congress shutdown fight, Iran war divide (Reuters).

HERO_KICKER = "CLIMATE  •  ANTALYA, TURKIYE"
HERO_TITLE = ["NO DEAL IN ANTALYA", "COP31 RUNS OVERTIME"]
HERO_CAPTION = "ANTALYA - NEARLY 200 NATIONS TALKED PAST FRIDAY'S DEADLINE."
HERO_STANDFIRST = ("WO WEEKS OF TALKS IN ANTALYA ENDED WITHOUT A DEAL ON "
                    "FRIDAY. THE LATEST DRAFT NAMES NO FOSSIL FUELS AND "
                    "DROPS A $120BN AID TARGET. A THIRD DRAFT IS DUE ON "
                    "SATURDAY MORNING.")
HERO_BYLINE = "BY THE WORLD TODAY STAFF  •  ANTALYA"
HERO_SOURCE = "SOURCE: REUTERS / AP  •  CONFIRMED  •  DRAFT TEXT, NOT A DEAL"
HERO_JUMP = "FULL REPORT INSIDE  •  PAGE A7"

# (number, region, title, body, source)
SECONDARY = [
    ("02", "UKRAINE AND POLAND",
     "RAID ON KYIV, MISSILES IN POLAND",
     "110+ MISSILES, 400+ DRONES. NINE KILLED. NATO CHIEF TO WARSAW.",
     "SOURCE: REUTERS / AFP  •  CONFIRMED"),
    ("03", "DENMARK",
     "DENMARK EXPELS RUSSIAN DIPLOMAT",
     "DENMARK SAYS RUSSIA PLOTTED TO KILL RAPPER KYIVSTONER. TWO MEN CHARGED.",
     "SOURCE: AP  •  REPORTED"),
    ("04", "UNITED STATES",
     "WALL ST IN FREEFALL AS AI TRADE CRACKS",
     "NASDAQ -5.3%, S&P 500 -3.7%, DOW -1.9%. NVIDIA FELL 14% IN A DAY.",
     "SOURCE: REUTERS  •  CONFIRMED"),
    ("05", "SPACE",
     "A DATE WITH MERCURY AFTER EIGHT YEARS",
     "ESA-JAXA PROBE ENTERS MERCURY ORBIT TODAY, EIGHT YEARS AFTER LAUNCH.",
     "SOURCE: ESA  •  CONFIRMED"),
    ("06", "INDIA",
     "AKVAN HITS INDIA'S EAST COAST",
     "THE STORM CROSSED ODISHA AT 80 KM/H. HEAVY RAIN RUNS ON INTO SATURDAY.",
     "SOURCE: IMD / PTI  •  CONFIRMED"),
    ("07", "SAUDI ARABIA",
     "MISSILES AT RIYADH SHOT DOWN",
     "SAUDI DEFENCES STOPPED THREE HOUTHI MISSILES AIMED AT THE CAPITAL.",
     "SOURCE: AL ARABIYA  •  REPORTED"),
]

ALSO = [
    ("08", "TRUMP, BACK FROM SHENZHEN, DEFENDS SUMMIT WITH XI AND PUTIN  •  REUTERS"),
    ("09", "CONGRESS RACES TO AVERT SHUTDOWN AS IRAN WAR DIVIDES LAWMAKERS  •  REUTERS"),
]

MARKETS = "MARKETS: NASDAQ -5.3%  •  S&P 500 -3.7%  •  DOW -1.9%  •  VIX 36  •  ANT -9%"
WEATHER = "WEATHER: HEAVY RAIN EASES OVER EAST INDIA  •  COLD BITES IN KYIV"


def check_copy():
    all_text = [HERO_KICKER, HERO_CAPTION, HERO_STANDFIRST, HERO_BYLINE,
                HERO_SOURCE, HERO_JUMP, MARKETS, WEATHER,
                "THE WORLD TODAY", "SATURDAY 21 NOVEMBER 2026",
                "EDITION NO. 325  •  PRICE $2.50", "ILLUSTRATION"]
    for s in SECONDARY:
        all_text += list(s)
    for _, s in ALSO:
        all_text.append(s)
    for t in all_text:
        for ch in t:
            if ch not in FONT:
                raise ValueError('no glyph for %r in %r' % (ch, t))


def draw_illustration(cv):
    x0, y0, x1, y1 = 36, 240, 988, 400
    # red sun over the Mediterranean
    cv.circle(880, 292, 46, RED)
    # skyline silhouettes on the coast
    for bx, bw, bh in [(60, 54, 50), (130, 40, 70), (186, 64, 36),
                       (266, 44, 60), (326, 70, 32), (700, 48, 46),
                       (764, 36, 64), (816, 60, 36)]:
        cv.rect(bx, 332 - bh, bw, bh, INK)
    for wx, wy in [(72, 292), (140, 276), (200, 306), (278, 284),
                   (712, 298), (774, 282)]:
        cv.rect(wx, wy, 5, 7, PAPER)
    # conference hall with a dome rising above its roof, flags flying
    for yy in range(262, 301):
        hw = int((38 ** 2 - (yy - 300) ** 2) ** 0.5)
        cv.rect(520 - hw, yy, 2 * hw, 1, NAVY)
    cv.rect(430, 300, 180, 32, NAVY)
    for fx in (448, 592):
        cv.vline(fx, 268, 32, INK, 3)
        cv.rect(fx + 3, 268, 20, 11, RED)
    cv.vline(520, 238, 62, INK, 3)
    cv.rect(523, 238, 20, 11, RED)
    # sea + white waves
    cv.rect(x0, 332, x1 - x0, y1 - 332, NAVY)
    for wx, ww, wy in [(60, 240, 350), (700, 260, 362), (120, 300, 378)]:
        cv.hline(wx, wy, ww, PAPER, 3)
    # frame + label
    cv.hline(x0, y0, x1 - x0, INK, 2)
    cv.hline(x0, y1 - 2, x1 - x0, INK, 2)
    cv.vline(x0, y0, y1 - y0, INK, 2)
    cv.vline(x1 - 2, y0, y1 - y0, INK, 2)
    cv.rect(48, 248, 172, 22, PAPER)
    cv.hline(48, 248, 172, RED, 2)
    cv.hline(48, 268, 172, RED, 2)
    cv.vline(48, 248, 22, RED, 2)
    cv.vline(218, 248, 22, RED, 2)
    cv.text(56, 252, "ILLUSTRATION", 2, RED)


def draw(cv):
    check_copy()
    cv.rect(0, 0, W, H, PAPER)
    # ---- nameplate + dateline ---------------------------------------------
    cv.text_c(12, "THE WORLD TODAY", 7, INK)
    cv.hline(36, 70, 952, RED, 6)
    cv.hline(36, 80, 952, INK, 2)
    cv.text(36, 88, "SATURDAY 21 NOVEMBER 2026", 2, INK)
    cv.text(988 - text_w("EDITION NO. 325  •  PRICE $2.50", 2), 88,
            "EDITION NO. 325  •  PRICE $2.50", 2, INK)
    cv.hline(36, 110, 952, INK, 2)
    # ---- hero ---------------------------------------------------------------
    cv.text(36, 120, HERO_KICKER, 2, RED)
    y = 140
    for line in HERO_TITLE:
        cv.text(36, y, line, 6, INK)
        y += 48
    draw_illustration(cv)
    cv.text(36, 408, HERO_CAPTION, 2, INK)
    # standfirst with drop cap
    cv.text(36, 424, "T", 5, RED)
    slines = wrap(HERO_STANDFIRST, 2, 914)
    assert len(slines) == 3, slines
    y = 424
    for line in slines:
        cv.text(74, y, line, 2, INK)
        y += 18
    cv.text(36, 482, HERO_BYLINE, 2, INK)
    cv.text(36, 500, HERO_SOURCE, 2, INK)
    cv.text(36, 518, HERO_JUMP, 2, RED)
    cv.hline(36, 544, 952, INK, 2)
    # ---- secondary grid: 2 cols x 3 rows ------------------------------------
    rows_y = [564, 682, 800]
    for i, (num, region, title, body, src) in enumerate(SECONDARY):
        cx = 36 if i % 2 == 0 else 524
        top = rows_y[i // 2]
        cv.text(cx, top, num, 2, RED)
        cv.text(cx + 48, top, region, 2, INK)
        tlines = wrap(title, 3, 464)
        assert 1 <= len(tlines) <= 2, (title, tlines)
        y = top + 20
        for line in tlines:
            cv.text(cx, y, line, 3, INK)
            y += 24
        blines = wrap(body, 2, 464)
        assert len(blines) == 2, (body, blines)
        y = top + 69
        for line in blines:
            cv.text(cx, y, line, 2, INK)
            y += 16
        cv.text(cx, top + 101, src, 2, INK)
    cv.vline(512, 564, 351, TINT, 2)
    cv.hline(36, 679, 952, TINT, 2)
    cv.hline(36, 797, 952, TINT, 2)
    # ---- also today + market/weather strip ------------------------------------
    cv.hline(36, 922, 952, INK, 2)
    y = 930
    for num, line in ALSO:
        cv.text(36, y, num, 2, RED)
        cv.text(84, y, line, 2, INK)
        y += 18
    cv.hline(36, 970, 952, INK, 2)
    cv.text(36, 978, MARKETS, 2, INK)
    cv.text(36, 996, WEATHER, 2, INK)


def main():
    # Server runs /bot read-only: write into MAKEFUN_OUTPUT_DIR when set.
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(
        os.path.abspath(__file__))
    out = os.path.join(outdir, "entry.png")
    cv = Canvas(W, H, PAPER)
    draw(cv)
    data = png_bytes(cv)
    assert len(data) <= 1048576, len(data)
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s %d bytes" % (out, len(data)))


if __name__ == "__main__":
    main()
