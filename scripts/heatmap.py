#!/usr/bin/env python3
"""Generate an animated contribution heatmap SVG from the public GitHub contributions page.
Stdlib only, no token needed. Used by .github/workflows/heatmap.yml.

Usage: python scripts/heatmap.py [user] [assets/heatmap.svg]
"""
import datetime as dt
import re
import sys
import urllib.request

BG, FG, MUTED = "#151515", "#f4f1eb", "#b8b6b0"
LEVELS = ["#262626", "#5a2513", "#99391a", "#d24b22", "#F05A2A"]  # GitHub levels 0-4 in orange
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
CELL, GAP = 12, 3
LEFT, TOP = 46, 52


def fetch(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions", headers={"User-Agent": "profile-heatmap"}
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    # shortcut: scrapes GitHub's HTML; if the markup changes, switch to the GraphQL contributionsCollection API.
    days = {}
    for m in re.finditer(r'<td[^>]*?data-date="([\d-]+)"[^>]*?id="([^"]+)"[^>]*?data-level="(\d)"', html):
        days[m.group(2)] = [dt.date.fromisoformat(m.group(1)), int(m.group(3)), 0]
    for m in re.finditer(r'<tool-tip[^>]*?for="([^"]+)"[^>]*>\s*(No|\d[\d,]*) contribution', html):
        if m.group(1) in days and m.group(2) != "No":
            days[m.group(1)][2] = int(m.group(2).replace(",", ""))
    # fail loudly instead of committing an empty map
    assert len(days) > 300, f"parsed only {len(days)} days; GitHub markup may have changed"
    return sorted(days.values())


def main(user="idmossab", out="assets/heatmap.svg"):
    days = fetch(user)
    start = days[0][0] - dt.timedelta(days=days[0][0].isoweekday() % 7)  # Sunday on/before first day
    cols = (days[-1][0] - start).days // 7 + 1
    total = sum(d[2] for d in days)
    W = LEFT + cols * (CELL + GAP) + 20
    H = TOP + 7 * (CELL + GAP) + 44
    dur = 2.6

    cells, months, last_month = [], [], None
    for d, level, count in days:
        c, r = (d - start).days // 7, d.isoweekday() % 7
        x, y = LEFT + c * (CELL + GAP), TOP + r * (CELL + GAP)
        t = round(0.05 + c / cols * 0.7, 3)
        tip = f"{count} contribution{'s' * (count != 1)} on {d:%b %d, %Y}"
        # sweep left to right; base opacity 1 keeps it visible without SMIL
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LEVELS[level]}"><title>{tip}</title>'
            f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{t};{min(t + 0.15, 1)}" dur="{dur}s" fill="freeze"/></rect>'
        )
        if r == 0 and d.month != last_month and d.day <= 7:
            months.append(f'<text x="{x}" y="{TOP - 8}">{d:%b}</text>')
            last_month = d.month

    wk = "".join(f'<text x="{LEFT - 8}" y="{TOP + r * (CELL + GAP) + 10}" text-anchor="end">{n}</text>'
                 for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    ly = TOP + 7 * (CELL + GAP) + 18
    lx = W - 20 - 30 - 5 * (CELL + GAP)
    legend = "".join(f'<rect x="{lx + i * (CELL + GAP)}" y="{ly - 10}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
                     for i, c in enumerate(LEVELS))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total} GitHub contributions in the last year">
<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<g font-family="{FONT}" font-size="11" fill="{MUTED}">
<text x="{LEFT}" y="24" font-size="13" fill="{FG}"><tspan fill="#F05A2A">{total:,}</tspan> contributions in the last year</text>
{"".join(months)}{wk}
<text x="{lx - 6}" y="{ly}" text-anchor="end">Less</text>{legend}<text x="{lx + 5 * (CELL + GAP) + 3}" y="{ly}">More</text>
<text x="{LEFT}" y="{ly}">updated {dt.date.today():%Y-%m-%d}</text>
</g>
{"".join(cells)}
</svg>
'''
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}: {len(days)} days, {total} contributions")


if __name__ == "__main__":
    main(*sys.argv[1:3])
