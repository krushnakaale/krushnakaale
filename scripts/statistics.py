"""Animated circular cyberpunk dashboard using verified public GitHub metrics."""
from html import escape
from math import pi


def render_stats(metrics, languages):
    metrics = list(metrics)[:4]
    colors = ("#22D3EE", "#A78BFA", "#39FF88", "#F472B6")
    rings = []
    for i, (label, value) in enumerate(metrics):
        cx = 145 + i * 270
        cy = 153
        color = colors[i]
        # Decorative orbit: not a percentage or a progress claim.
        rings.append(
            f'<circle cx="{cx}" cy="{cy}" r="74" fill="#101A2D" stroke="#253650" stroke-width="13"/>'
            f'<circle class="orbit" cx="{cx}" cy="{cy}" r="74" fill="none" stroke="{color}" '
            f'stroke-width="13" stroke-linecap="round" stroke-dasharray="330 465" '
            f'transform="rotate(-90 {cx} {cy})"/>'
            f'<circle cx="{cx}" cy="{cy}" r="53" fill="#0B1223"/>'
            f'<text x="{cx}" y="{cy+11}" text-anchor="middle" fill="{color}" '
            f'font-size="40" font-weight="800">{max(0, int(value)):,}</text>'
            f'<text x="{cx}" y="264" text-anchor="middle" fill="#D8E5F4" font-size="17">{escape(str(label))}</text>'
        )
    items = languages.most_common(5) if languages else []
    total = sum(max(0, int(count)) for _, count in items)
    segments = []
    legend = []
    circumference = 2 * pi * 91
    offset = 0.0
    for i, (language, count) in enumerate(items):
        color = colors[i % len(colors)]
        fraction = max(0, int(count)) / total if total else 0
        dash = fraction * circumference
        segments.append(
            f'<circle cx="240" cy="420" r="91" fill="none" stroke="{color}" '
            f'stroke-width="24" stroke-dasharray="{dash:.2f} {circumference:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 240 420)"/>'
        )
        offset += dash
        x = 455 + (i % 2) * 310
        y = 365 + (i // 2) * 59
        legend.append(
            f'<circle cx="{x}" cy="{y}" r="7" fill="{color}"/>'
            f'<text x="{x+17}" y="{y+6}" font-size="17" fill="#E8F0FA">{escape(str(language))}</text>'
            f'<text x="{x+17}" y="{y+26}" font-size="13" fill="#A7BCD5">{int(count)} public repos</text>'
        )
    if not items:
        legend.append('<text x="460" y="405" font-size="18" fill="#A7BCD5">No public language data available</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="610" viewBox="0 0 1100 610" role="img" aria-labelledby="title desc">
<title id="title">Circular live GitHub dashboard</title>
<desc id="desc">Verified public repository statistics in decorative circular cards and a proportional language donut chart</desc>
<defs>
<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#080D1D"/><stop offset="1" stop-color="#101C2B"/></linearGradient>
<style>.orbit{{animation:orbit 14s linear infinite;transform-box:fill-box;transform-origin:center}}.pulse{{animation:pulse 2.5s ease-in-out infinite alternate}}@keyframes orbit{{to{{stroke-dashoffset:-465}}}}@keyframes pulse{{to{{opacity:.3}}}}@media(prefers-reduced-motion:reduce){{.orbit,.pulse{{animation:none}}}}</style>
</defs>
<rect width="1100" height="610" rx="20" fill="url(#bg)"/>
<rect x="1" y="1" width="1098" height="608" rx="19" stroke="#35486B" fill="none"/>
<circle class="pulse" cx="27" cy="35" r="6" fill="#39FF88"/>
<text x="43" y="42" font-family="monospace" font-size="22" font-weight="700" fill="#EFF6FF">GITHUB / LIVE ORBIT DASHBOARD</text>
<text x="1072" y="40" text-anchor="end" font-family="monospace" font-size="13" fill="#22D3EE">API DATA · AUTO REFRESH</text>
<g font-family="Arial,sans-serif">{''.join(rings)}</g>
<path d="M24 300H1076" stroke="#30425F"/>
<text x="28" y="334" font-family="monospace" font-size="20" font-weight="700" fill="#A78BFA">LANGUAGE DISTRIBUTION</text>
<circle cx="240" cy="420" r="91" fill="none" stroke="#24324B" stroke-width="24"/>
<g>{''.join(segments)}</g>
<text x="240" y="417" text-anchor="middle" font-family="Arial,sans-serif" font-size="33" font-weight="800" fill="#F1F5FF">{total}</text>
<text x="240" y="440" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#AFC2D9">REPOSITORIES</text>
<g font-family="Arial,sans-serif">{''.join(legend)}</g>
<text x="28" y="582" font-family="monospace" font-size="12" fill="#8DA3BE">METRICS ARE VERIFIED PUBLIC COUNTS · ORBIT RINGS ARE DECORATIVE · DONUT SHOWS PRIMARY REPO LANGUAGES</text>
</svg>
"""
