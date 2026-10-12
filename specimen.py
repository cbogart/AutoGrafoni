#!/usr/bin/env python3
"""
Render a specimen sheet of tricky Grafoni cases to PDF, for checking changes by eye.

    python specimen.py                      # writes output/specimen.pdf
    python specimen.py -o somewhere.pdf --scale 2

Each row shows the English text, the glyph sequence the converter chose, the
Grafoni rendering (same pipeline as the book converter), and what to look for.
Exits non-zero if any case contains a glyph Grafoni can't draw.
"""

import argparse
import io
import sys
from pathlib import Path

import cairosvg
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

import grafoni
import grafoni_utils

# (section, [(text, what to look for), ...])
CASES = [
    ("Dictionary pronunciations (CMU primary, not eng_to_ipa's last variant)", [
        ("hundred asked question already", "not hunnerd / ast / guesshon / aready"),
        ("center enter just I'm does nice", "not cenner / enner / jist / ahm / diz / nis"),
        ("to his him has huge writhing", "not ti / em / hez / yuge; writhing has dh"),
        ("us", "not spelled U.S."),
        ("bought caught cot", "bought/caught keep the open o (lv3)"),
    ]),
    ("Each word always written one way", [
        ("the eve of the war", "the is always the flat line, even before a vowel"),
        ("close the door, a close call", "close is the same both times"),
    ]),
    ("Words not in the dictionary", [
        ("Costigan's lifeboat's clanged lugged", "built from known pieces + 's / ed"),
        ("dyne quixotic cyclic jazzy", "letter rules: no bare c, q, x or y glyphs"),
        ("Nerado Nevian Triplanetario", "invented names: letter-rule guesses"),
        ("complacence dirigible declination", "soft c, -ble, -tion endings"),
        ("DNA FBI NASA XYZ Br", "Latin letters, except NASA (said as a word)"),
        ("I AM HERE, OK?", "all-caps words stay Grafoni; OK is letters"),
    ]),
    ("Numerals", [
        ("Chapter XIV, Henry VIII, 1913", "Roman numerals become Grafoni digits"),
    ]),
    ("Punctuation (ordinary English marks; hyphen doubled as =)", [
        ('"Go," he said.', 'quotes; G has its start form after "'),
        ("Is it Fred? Fred!", "? and !; d has its end form before ? and !"),
        ("'Tis Samms's (word).", "single quote, parentheses"),
        ("know--know ultra-wave; well: yes", "dash and hyphen as =, semicolon, colon"),
    ]),
    ("Joins and spacing", [
        ("withdrawn withdrew bathed", "th/dh rise straight into d, no flat gap"),
        ("things nothing nothingness writhing", "i arch flows into ng; ng loop closed, no tail; short run between ng and n"),
        ("watched church H", "t+sh flows together with no hitch"),
        ("savagely strangely freshly", "d flows into zh; narrow l loop clears the d"),
        ("transmitter endured", "s and m don't collide; d and u visible"),
    ]),
]

SVG_DIVISOR = 2.5      # matches PDFGenerator.BASE_SVG_DIVISOR
WRAP = 240             # stroke units, roughly a book line at scale 1


def render(text):
    """Return (glyph list, list of PNG bytes, list of (width, height) in SVG px)."""
    glyphs = grafoni.to_list(text)
    svgs = grafoni_utils.to_svg_no_display(text, wrap=WRAP, page_height=10000)
    pngs = [cairosvg.svg2png(bytestring=svg.as_svg().encode(), background_color="white", scale=2)
            for svg in svgs]
    return glyphs, pngs, [(svg.width, svg.height) for svg in svgs]


def build(output, scale=1.5):
    page_w, page_h = A4
    margin = 50
    c = canvas.Canvas(str(output), pagesize=A4)
    y = page_h - margin
    unsupported = []

    def new_page():
        nonlocal y
        c.showPage()
        y = page_h - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Grafoni specimen")
    y -= 28

    for section, cases in CASES:
        if y < margin + 80:
            new_page()
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, section)
        y -= 18
        for text, note in cases:
            glyphs, pngs, sizes = render(text)
            bad = [g for g in glyphs if g not in grafoni.letter_forms and g not in grafoni.ligatures]
            unsupported += [(text, g) for g in bad]
            heights = [h / SVG_DIVISOR * scale for _, h in sizes]
            if y - (26 + sum(heights)) < margin:
                new_page()
            c.setFont("Helvetica", 10)
            c.drawString(margin, y, text)
            c.setFont("Helvetica-Oblique", 8)
            c.setFillGray(0.4)
            c.drawString(margin + 230, y, note)
            c.setFont("Courier", 7)
            c.drawString(margin, y - 10, " ".join(glyphs)[:130])
            c.setFillGray(0)
            y -= 14
            for png, (w, h) in zip(pngs, sizes):
                dw, dh = w / SVG_DIVISOR * scale, h / SVG_DIVISOR * scale
                c.drawImage(ImageReader(io.BytesIO(png)), margin, y - dh, dw, dh)
                y -= dh
            y -= 6
        y -= 8

    c.save()
    return unsupported


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--output", default="output/specimen.pdf")
    parser.add_argument("--scale", type=float, default=1.5, help="Grafoni display size (default 1.5)")
    args = parser.parse_args()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    unsupported = build(args.output, args.scale)
    print(f"Specimen saved as: {args.output}")
    for text, glyph in unsupported:
        print(f"Unsupported glyph {glyph!r} in {text!r}")
    sys.exit(1 if unsupported else 0)


if __name__ == "__main__":
    main()
