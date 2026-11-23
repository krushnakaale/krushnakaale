"""Centered, live GitHub primary-language pie chart in a cyber dashboard style."""
from html import escape
from math import cos, sin, pi

COLORS = ("#39FF88", "#22D3EE", "#A78BFA", "#FBBF24", "#FB7185", "#60A5FA", "#2DD4BF", "#F97316")


def render_language_pie(languages):
    items = [(str(k), max(0, int(v))) for k, v in languages.most_common() if int(v) > 0]
    total = sum(v for _, v in items)
    # Show at most seven named slices; aggregate the rest to preserve exact totals.
    if len(items) > 7:
        items = items[:7] + [("Other", sum(v for _, v in items[7:]))]
    cx, cy, r = 360, 214, 137
    slices, legend = [], []
    angle = -pi / 2
    for i, (name, value) in enumerate(items):
        portion = value / total
        color = COLORS[i % len(COLORS)]
        next_angle = angle + 2 * pi * portion
        if portion >= .999999:
            shape = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'
        else:
            x1, y1 = cx + r * cos(angle), cy + r * sin(angle)
            x2, y2 = cx + r * cos(next_angle), cy + r * sin(next_angle)
            large = 1 if portion > .5 else 0
            shape = f'<path d="M{cx},{cy} L{x1:.3f},{y1:.3f} A{r},{r} 0 {large} 1 {x2:.3f},{y2:.3f} Z" fill="{color}" stroke="#07121A" stroke-width="3"/>'
        slices.append(shape)
        ly = 101 + i * 43
        pct = 100 * portion
        legend.append(f'<circle cx="630" cy="{ly}" r="7" fill="{color}"/>'
                      f'<text x="650" y="{ly+5}" fill="#D9F7EA" font-size="17" font-weight="600">{escape(name[:19])}</text>'
                      f'<text x="1018" y="{ly+5}" text-anchor="end" fill="{color}" font-size="17" font-weight="700">{pct:.1f}%</text>'
                      f'<text x="1038" y="{ly+5}" fill="#85B9AA" font-size="12">({value})</text>')
        angle = next_angle
    if not items:
        slices.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#15362E"/>')
        legend.append('<text x="635" y="185" fill="#B5D4C8" font-size="18">No public language data yet</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="430" viewBox="0 0 1100 430" role="img" aria-labelledby="title desc">
<title id="title">Live language breakdown pie chart</title>
<desc id="desc">GitHub primary language distribution across {total} public repositories, updated automatically</desc>
<defs>
<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#061018"/><stop offset="1" stop-color="#09251D"/></linearGradient>
<radialGradient id="shine" cx=".32" cy=".22" r=".9"><stop stop-color="#FFFFFF" stop-opacity=".22"/><stop offset=".52" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" stroke="#39FF88" stroke-opacity=".055" fill="none"/></pattern>
</defs>
<rect width="1100" height="430" rx="20" fill="url(#bg)"/>
<rect width="1100" height="430" rx="20" fill="url(#grid)"/>
<rect x="2" y="2" width="1096" height="426" rx="18" stroke="#22684D" fill="none"/>
<text x="550" y="38" text-anchor="middle" font-family="monospace" font-size="20" font-weight="700" fill="#39FF88">LANGUAGE // DISTRIBUTION</text>
<text x="550" y="60" text-anchor="middle" font-family="monospace" font-size="12" fill="#9ABFAF">LIVE GITHUB PRIMARY LANGUAGE DATA</text>
<ellipse cx="370" cy="226" rx="145" ry="137" fill="#000" opacity=".45"/>
<g>{''.join(slices)}</g>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#shine)" pointer-events="none"/>
<circle cx="{cx}" cy="{cy}" r="{r+5}" fill="none" stroke="#39FF88" stroke-opacity=".35" stroke-width="1"/>
<g font-family="Arial,sans-serif">{''.join(legend)}</g>
<text x="550" y="403" text-anchor="middle" font-family="monospace" font-size="12" fill="#87AFA1">{total} REPOSITORIES WITH REPORTED PRIMARY LANGUAGE · AUTO-SYNC</text>
</svg>"""
