#!/usr/bin/env python3
"""Render the round-4 design upgrade of the news-image-20261118 front page.

Ensemble front-page layout: classic masthead with boxed ears, double rule,
dateline strip, one large lead story, a two-column row (photo left), a
three-column row (photo top), a footer band of one-line briefs and a folio
line. All type is rendered with PIL on a warm paper background with a
subtle grain overlay. Output: entry.png (JPEG bytes, 1024x1024).
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
PAPER = (244, 241, 234)      # #F4F1EA
INK = (20, 20, 20)           # #141414
ACCENT = (179, 18, 23)       # #B31217
BAND = (237, 233, 224)       # #EDE9E0
MUTED = (85, 80, 73)         # #555049

# ---------------------------------------------------------------- geometry
W = H = 1024
MX = 32                      # outer margin
CW = 960                     # content width
RX = MX + CW                 # right content edge (992)

PANELS_DIR = os.path.expanduser("~/workspace/makefun/news-image-20261118-panels")
PANELS = {
    "lead": "media-generation-panel1-quad-manila-0-701b0b43-3775-4ecf-956c-c73afcc4fb96.webp",
    "crimea": "media-generation-panel2-crimean-bridge-0-6d3a6d9b-8073-42d1-85b3-3c3bd46d18cb.webp",
    "gulf": "media-generation-panel3-iran-drones-0-ae0fc9b4-314f-4052-9157-a59c84029d5c.webp",
    "cyclone": "media-generation-panel4-cyclone-0-c9fe8f91-816b-4e8b-be84-b788feb21c36.webp",
    "nvidia": "media-generation-panel5-nvidia-0-0403bc42-0437-486c-b209-6ec835411acf.webp",
    "eu": "media-generation-panel6-eu-ukraine-0-9ca0146c-6f2c-4b1e-9785-edbbf5b126eb.webp",
}

# ---------------------------------------------------------------- fonts
_FONT_DIRS = ["/usr/share/fonts/truetype/noto",
              "/usr/share/fonts/truetype/liberation",
              "/usr/share/fonts/truetype/dejavu"]


def _font_path(name, fallback):
    for d in _FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return fallback


SERIF_BLACK = _font_path("NotoSerif-Black.ttf",
                         "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
SERIF_BOLD = _font_path("NotoSerif-Bold.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
SERIF_ITALIC = _font_path("NotoSerif-Italic.ttf",
                          "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf")
SANS = _font_path("NotoSans-Regular.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
SANS_BOLD = _font_path("NotoSans-Bold.ttf",
                       "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- helpers
def text_w(draw, text, font, tracking=0):
    """Width of text including optional letter tracking."""
    w = draw.textlength(text, font=font)
    if tracking and len(text) > 1:
        w += tracking * (len(text) - 1)
    return w


def draw_tracked(draw, x, y, text, font, fill, tracking=2):
    """Draw letter-spaced text starting at (x, y); return end x."""
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=font, fill=fill)
        cx += draw.textlength(ch, font=font) + tracking
    return cx - tracking


def draw_tracked_centred(draw, cx, y, text, font, fill, tracking=2):
    total = text_w(draw, text, font, tracking)
    return draw_tracked(draw, cx - total / 2, y, text, font, fill, tracking)


def fit_font(draw, text, path, start, minimum, max_w, tracking=0):
    """Largest font size <= start (and >= minimum) that fits max_w."""
    size = start
    while size > minimum:
        f = F(path, size)
        if text_w(draw, text, f, tracking) <= max_w:
            return f
        size -= 1
    return F(path, minimum)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def crop_to_fill(img, tw, th, fx=0.5, fy=0.5):
    """Crop img to the target aspect around focus (fx, fy), resize to fill."""
    w, h = img.size
    ta = tw / th
    if w / h > ta:                       # too wide: crop width
        cw, ch = int(h * ta), h
    else:                                # too tall: crop height
        cw, ch = w, int(w / ta)
    left = min(max(int(fx * w - cw / 2), 0), w - cw)
    top = min(max(int(fy * h - ch / 2), 0), h - ch)
    return img.crop((left, top, left + cw, top + ch)).resize((tw, th),
                                                             Image.LANCZOS)


def load_panel(key, tw, th, fx=0.5, fy=0.5):
    img = Image.open(os.path.join(PANELS_DIR, PANELS[key])).convert("RGB")
    return crop_to_fill(img, tw, th, fx, fy)


def hairline(draw, y, x0=MX, x1=RX):
    draw.line([(x0, y), (x1, y)], fill=INK, width=1)


def photo(draw, page, key, x, y, tw, th, fx=0.5, fy=0.5):
    """Paste a panel photo with a thin 2px ink border."""
    page.paste(load_panel(key, tw, th, fx, fy), (x, y))
    draw.rectangle([x, y, x + tw - 1, y + th - 1], outline=INK, width=2)


def kicker(draw, x, y, text, size=15):
    """Accent square + tracked small-caps kicker in accent colour."""
    f = F(SANS_BOLD, size)
    sq_y = y + (size - 6) // 2 + 1
    draw.rectangle([x, sq_y, x + 5, sq_y + 5], fill=ACCENT)
    draw_tracked(draw, x + 14, y, text.upper(), f, ACCENT, tracking=2)


# ---------------------------------------------------------------- page
def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)

    # ---- masthead ------------------------------------------------------
    ear_f = F(SANS_BOLD, 15)
    for box_x, cx in ((MX, MX + 75), (842, 842 + 75)):
        d.rectangle([box_x, 24, box_x + 149, 79], outline=INK, width=1)
    d.text((MX + 75, 33), "WEDNESDAY", font=ear_f, fill=INK, anchor="ma")
    d.text((MX + 75, 54), "18 NOV 2026", font=ear_f, fill=INK, anchor="ma")
    d.text((917, 33), "EDITION", font=ear_f, fill=INK, anchor="ma")
    d.text((917, 54), "No. 18", font=ear_f, fill=INK, anchor="ma")

    title = "THE WORLD IN ONE DAY"
    tf = fit_font(d, title, SERIF_BLACK, 68, 40, 628)
    d.text((512, 52), title, font=tf, fill=INK, anchor="mm")

    # ---- double rule + dateline ----------------------------------------
    d.rectangle([MX, 88, RX - 1, 90], fill=INK)          # 3px rule
    d.line([(MX, 95), (RX - 1, 95)], fill=INK, width=1)  # 1px rule
    draw_tracked_centred(d, 512, 103,
                         "WEDNESDAY · 18 NOVEMBER 2026 · SIX STORIES, ONE PAGE",
                         F(SANS_BOLD, 19), INK, tracking=1)
    hairline(d, 133)

    # ---- lead story (APEC) ----------------------------------------------
    photo(d, page, "lead", MX, 141, 960, 244, fx=0.5, fy=0.47)
    d.text((MX, 391),
           "A presidential aircraft on the rain-slicked tarmac at Shenzhen "
           "as leaders arrive for the APEC summit.",
           font=F(SERIF_ITALIC, 15), fill=MUTED)
    kicker(d, MX, 416, "Diplomacy", size=16)
    headline = "Xi Greets Trump as APEC Opens in Shenzhen"
    hf = fit_font(d, headline, SERIF_BOLD, 40, 34, CW)
    d.text((MX, 442), headline, font=hf, fill=INK)
    y = 494
    for line in wrap(d, "APEC opens as Xi and Putin denounce protectionism "
                        "ahead of Thursday's three-way talks in Shenzhen.",
                     F(SANS, 20), CW):
        d.text((MX, y), line, font=F(SANS, 20), fill=INK)
        y += 27
    hairline(d, 556)

    # ---- row A: two stories, photo left ----------------------------------
    row_a = [
        ("crimea", 0.72, 0.55, "War in Europe",
         "Ukraine Cripples the Crimea Bridge",
         "Drones and missiles drop the central arch into the sea on the "
         "second day of strikes."),
        ("gulf", 0.5, 0.5, "Middle East",
         "US and Iran Trade Blows Across the Gulf",
         "US jets hit Qeshm Island; Iran strikes a US base in Kuwait and "
         "sites in Bahrain."),
    ]
    for i, (key, fx, fy, kick, head, summ) in enumerate(row_a):
        x = MX + i * (468 + 24)
        photo(d, page, key, x, 564, 140, 148, fx=fx, fy=fy)
        tx = x + 152
        kicker(d, tx, 564, kick, size=15)
        yy = 586
        for line in wrap(d, head, F(SERIF_BOLD, 25), 316)[:2]:
            d.text((tx, yy), line, font=F(SERIF_BOLD, 25), fill=INK)
            yy += 29
        yy = 648
        for line in wrap(d, summ, F(SANS, 17), 316)[:3]:
            d.text((tx, yy), line, font=F(SANS, 17), fill=INK)
            yy += 21
    hairline(d, 720)

    # ---- row B: three stories, photo top ---------------------------------
    row_b = [
        ("cyclone", 0.5, 0.48, "Weather",
         "Cyclone Akvan Bears Down on India",
         "Landfall due on the Andhra Pradesh coast Friday; winds to "
         "145 km/h."),
        ("nvidia", 0.5, 0.5, "Business",
         "Record Nvidia Quarter, Shares Still Fall",
         "Revenue up 103% to $115.8bn in the first results since Huang "
         "resigned."),
        ("eu", 0.5, 0.45, "Europe",
         "EU Proposes €45bn Ukraine Loan",
         "Repayable only after Russia pays reparations; €25bn for "
         "military aid."),
    ]
    for i, (key, fx, fy, kick, head, summ) in enumerate(row_b):
        x = MX + i * (304 + 24)
        photo(d, page, key, x, 728, 304, 84, fx=fx, fy=fy)
        kicker(d, x, 818, kick, size=14)
        yy = 838
        for line in wrap(d, head, F(SERIF_BOLD, 22), 304)[:2]:
            d.text((x, yy), line, font=F(SERIF_BOLD, 22), fill=INK)
            yy += 26
        yy = 894
        for line in wrap(d, summ, F(SANS, 17), 304)[:2]:
            d.text((x, yy), line, font=F(SANS, 17), fill=INK)
            yy += 21

    # ---- footer band: four one-line briefs --------------------------------
    d.rectangle([MX, 944, RX - 1, 987], fill=BAND)
    briefs = [
        "SHENZHEN — Three-way talks Thursday",
        "BLACK SEA — Bridge hit for a second day",
        "GULF — Kuwait, Bahrain sites struck",
        "AKVAN — Landfall expected Friday",
    ]
    bf_bold = F(SANS_BOLD, 16)
    bf_reg = F(SANS, 16)
    space_w = d.textlength(" ", font=bf_reg)
    for i, brief in enumerate(briefs):
        label, rest = brief.split(" — ", 1)
        words = [(w, bf_bold, ACCENT) for w in label.split()]
        words.append(("—", bf_bold, ACCENT))
        words += [(w, bf_reg, INK) for w in rest.split()]
        col_x = MX + i * 240 + 12
        max_w = 216
        lines, cur, cur_w = [], [], 0.0
        for w, fnt, fill in words:
            ww = d.textlength(w, font=fnt)
            add = ww if not cur else ww + space_w
            if cur and cur_w + add > max_w:
                lines.append(cur)
                cur, cur_w = [(w, fnt, fill)], ww
            else:
                cur.append((w, fnt, fill))
                cur_w += add
        if cur:
            lines.append(cur)
        lines = lines[:2]
        block_h = (len(lines) - 1) * 20 + 16
        yy = 944 + (44 - block_h) // 2
        for line_words in lines:
            xx = col_x
            for w, fnt, fill in line_words:
                d.text((xx, yy), w, font=fnt, fill=fill)
                xx += d.textlength(w, font=fnt) + space_w
            yy += 20
    for sx in (272, 512, 752):
        d.line([(sx, 950), (sx, 982)], fill=INK, width=1)

    # ---- folio ------------------------------------------------------------
    draw_tracked_centred(
        d, 512, 994,
        "THE WORLD IN ONE DAY · PAGE 1 — Images: AI-generated "
        "photorealistic panels · Not real photographs",
        F(SANS, 12), MUTED, tracking=1)

    # ---- paper grain -------------------------------------------------------
    noise = Image.effect_noise((W, H), 48).convert("RGB")
    page = Image.blend(page, noise, 0.05)

    # ---- save (JPEG bytes in entry.png) ------------------------------------
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    page.save(out, format="JPEG", quality=88)
    data = open(out, "rb").read()
    print("entry.png:", len(data), "bytes, sha256",
          hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
