#!/usr/bin/env python3
"""Generate the neofetch-style info card SVG. Stdlib only.

Usage: python scripts/neofetch.py [assets/neofetch.svg]
"""
import sys
from xml.sax.saxutils import escape

BG, BAR, FG, MUTED, ACCENT = "#151515", "#1f1f1f", "#f4f1eb", "#b8b6b0", "#F05A2A"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
W, H = 861, 420  # W matches heatmap.svg (53 weeks) so both scale alike at width=100%

INFO = [
    ("Role", "Digital Product Builder"),
    ("Languages", "JavaScript, TypeScript, Python, Go, Dart, Java, C, Bash"),
    ("Frontend", "HTML, CSS, React, Bootstrap"),
    ("Mobile", "Flutter, Android"),
    ("Backend", "Node.js, PHP / Laravel, Spring Boot"),
    ("Databases", "PostgreSQL, MySQL, SQLite, MongoDB"),
    ("Automation", "n8n, Bash, Python scripts"),
    ("AI tools", "Claude Code, ChatGPT, Gemini, Ollama"),
    ("DevOps", "Docker, Git, GitHub Actions, Linux"),
]


def reveal(i, n, total=3.2):
    """Opacity + small slide-in for line i of n. Base state stays visible for non-SMIL renderers."""
    t = round(0.08 + i / n * 0.75, 3)
    end = round(min(t + 0.08, 1), 3)
    kt = f"0;{t};{end};1"
    return (
        f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="{kt}" dur="{total}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="-8 0;-8 0;0 0;0 0" keyTimes="{kt}" dur="{total}s" fill="freeze"/>'
    )


def main(out="assets/neofetch.svg"):
    rows = [
        f'<tspan fill="{ACCENT}" font-weight="bold">mossab</tspan><tspan fill="{FG}">@</tspan><tspan fill="{ACCENT}" font-weight="bold">github</tspan>',
        f'<tspan fill="{MUTED}">{"-" * 13}</tspan>',
    ]
    rows += [
        f'<tspan fill="{ACCENT}" font-weight="bold">{escape(k + ":"):<12}</tspan><tspan fill="{FG}">{escape(v)}</tspan>'
        for k, v in INFO
    ]
    n = len(rows) + 1  # +1 for the colour strip
    body = []
    y0, step = 76, 24
    for i, r in enumerate(rows):
        body.append(f'<g><text x="22" y="{y0 + i * step}">{r}</text>{reveal(i, n)}</g>')

    # neofetch colour strip: the palette, then a blinking cursor
    sy = y0 + len(rows) * step + 4
    swatches = ["#151515", "#3a1a0f", "#7a2e15", "#b8421f", ACCENT, "#ff8a5c", MUTED, FG]
    strip = "".join(
        f'<rect x="{22 + k * 26}" y="{sy}" width="24" height="14" rx="2" fill="{c}" stroke="#333" stroke-width="1"/>'
        for k, c in enumerate(swatches)
    )
    body.append(f"<g>{strip}{reveal(len(rows), n)}</g>")
    cy = sy + 40
    body.append(
        f'<text x="22" y="{cy}"><tspan fill="{ACCENT}">mossab@github</tspan><tspan fill="{FG}"> ~ $ </tspan></text>'
        f'<rect x="{22 + 18 * 8.4:.0f}" y="{cy - 13}" width="9" height="16" fill="{ACCENT}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="neofetch-style card: {escape("; ".join(f"{k}: {v}" for k, v in INFO))}">
<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<path d="M0 10a10 10 0 0 1 10-10h{W - 20}a10 10 0 0 1 10 10v24H0z" fill="{BAR}"/>
<circle cx="20" cy="17" r="6" fill="#ff5f57"/><circle cx="40" cy="17" r="6" fill="#febc2e"/><circle cx="60" cy="17" r="6" fill="#28c840"/>
<text x="{W / 2}" y="22" text-anchor="middle" fill="{MUTED}" font-family="{FONT}" font-size="13">mossab@github: ~$ neofetch</text>
<g font-family="{FONT}" font-size="14" xml:space="preserve">
{chr(10).join(body)}
</g>
</svg>
'''
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
