#!/usr/bin/env python3
"""Turn a photo into an ASCII-art SVG (warm-white glyphs on charcoal, row-by-row fade-in).

Usage: python scripts/ascii_portrait.py path/to/photo.png [assets/portrait.svg]
Needs Pillow. Run by hand; the output SVG is committed.
"""
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

BG, FG = "#151515", "#f4f1eb"
RAMP = " .:-=+*#%@"  # dark -> bright (photo background is black)
COLS, ROWS = 70, 42            # monospace cells are ~0.55 as wide as tall
W, H = 400, 400
PAD = 14


def main(src, out="assets/portrait.svg"):
    img = Image.open(src).convert("L")
    w, h = img.size
    img = img.crop((int(w * 0.2), int(h * 0.04), int(w * 0.8), int(h * 0.86)))  # tighten on head and collar
    img = ImageOps.autocontrast(img, cutoff=2)
    # blank the near-black backdrop/suit noise, lift mid-tones so the face reads
    img = img.point(lambda v: 0 if v < 22 else int(255 * (v / 255) ** 0.7)).resize((COLS, ROWS), Image.LANCZOS)
    px = img.load()
    rows = ["".join(RAMP[px[x, y] * (len(RAMP) - 1) // 255] for x in range(COLS)) for y in range(ROWS)]

    line_h = (H - 2 * PAD) / ROWS
    text_w = W - 2 * PAD
    total = 2.4  # seconds for the whole reveal
    lines = []
    for i, row in enumerate(rows):
        if not row.strip():
            continue
        t = round(i / ROWS * 0.7, 3)  # this row starts fading at t of the timeline
        y = PAD + (i + 0.8) * line_h
        # base opacity stays 1 so renderers without SMIL still show the picture
        lines.append(
            f'<text x="{PAD}" y="{y:.1f}" textLength="{text_w}" lengthAdjust="spacingAndGlyphs">{escape(row)}'
            f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{t};{min(t + 0.3, 1)}" dur="{total}s" fill="freeze"/></text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait of Mossab">
<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<g fill="{FG}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace" font-size="{line_h * 0.95:.1f}" xml:space="preserve">
{chr(10).join(lines)}
</g>
</svg>
'''
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out} ({len(lines)} rows)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(*sys.argv[1:3])
