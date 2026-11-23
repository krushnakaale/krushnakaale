"""Generate a compact, professional GitHub-language pie chart without unused space."""
from html import escape
from math import cos, sin, pi

COLORS = ("#39FF88", "#22D3EE", "#A78BFA", "#FBBF24", "#FB7185", "#60A5FA", "#2DD4BF", "#F97316")


def render_language_pie(languages):
    raw = [(str(name), int(count)) for name, count in languages.most_common() if int(count) > 0]
    total = sum(count for _, count in raw)
    items = raw[:7]
    if len(raw) > 7:
        items.append(("Other", sum(count for _, count in raw[7:])))
    # Responsive SVG height: room only for rows that actually exist.
    height = max(276, 82 + 38 * max(1, len(items)))
    cx, cy, radius = 238, height // 2 + 5, 103
    legends, slices = [], []
    angle = -pi / 2
    for index, (name, amount) in enumerate(items):
        share = amount / total
        color = COLORS[index % len(COLORS)]
        next_angle = angle + 2 * pi * share
        if share >= 0.99999:
            svg_path = f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{color}"/>'
        else:
            x1, y1 = cx + radius * cos(angle), cy + radius * sin(angle)
            x2, y2 = cx + radius * cos(next_angle), cy + radius * sin(next_angle)
            svg_path = (f'<path d="M{cx},{cy} L{x1:.2f},{y1:.2f} '
                        f'A{radius},{radius} 0 {int(share > .5)} 1 {x2:.2f},{y2:.2f} Z" '
                        f'fill="{color}" stroke="#07151C" stroke-width="2.5"/>')
        slices.append(svg_path)
        y = 88 + index * 38
        legends.append(
            f'<circle cx="473" cy="{y}" r="6" fill="{color}"/>'
            f'<text x="489" y="{y+5}" font-size="16" font-weight="600" fill="#E2F5F0">{escape(name[:23])}</text>'
            f'<text x="1020" y="{y+5}" text-anchor="end" font-size="16" font-weight="700" fill="{color}">{share*100:.1f}%</text>'
            f'<rect x="780" y="{y-7}" width="140" height="8" rx="4" fill="#19332D"/>'
            f'<rect x="780" y="{y-7}" width="{140*share:.1f}" height="8" rx="4" fill="{color}" opacity=".9"/>'
        )
        angle = next_angle
    if not items:
        slices.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="#13362B"/>')
        legends.append('<text x="480" y="148" font-size="17" fill="#A8C7BA">No primary-language data available</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img" aria-labelledby="title desc">
<title id="title">Live primary language breakdown</title>
<desc id="desc">Distribution of {total} public repositories by GitHub-reported primary language.</desc>
<defs>
<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#07131B"/><stop offset="1" stop-color="#0A2019"/></linearGradient>
<radialGradient id="shine" cx=".28" cy=".18" r=".9"><stop stop-color="#FFFFFF" stop-opacity=".23"/><stop offset=".65" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#39FF88" stroke-opacity=".045"/></pattern>
</defs>
<rect width="1100" height="{height}" rx="16" fill="url(#bg)"/>
<rect width="1100" height="{height}" rx="16" fill="url(#grid)"/>
<rect x="1" y="1" width="1098" height="{height-2}" rx="15" fill="none" stroke="#246D4E"/>
<text x="23" y="32" font-family="monospace" font-size="16" font-weight="700" fill="#39FF88">LANGUAGE // BREAKDOWN</text>
<text x="1076" y="32" text-anchor="end" font-family="monospace" font-size="12" fill="#8FC5A7">{total} REPOS · AUTO-SYNC</text>
<ellipse cx="{cx+7}" cy="{cy+10}" rx="{radius+2}" ry="{radius}" fill="#000" opacity=".28"/>
<g>{''.join(slices)}</g>
<circle cx="{cx}" cy="{cy}" r="{radius}" fill="url(#shine)"/>
<circle cx="{cx}" cy="{cy}" r="{radius+4}" fill="none" stroke="#39FF88" stroke-opacity=".27"/>
<g font-family="Arial,sans-serif">{''.join(legends)}</g>
</svg>"""
