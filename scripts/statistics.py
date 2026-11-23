"""Compact circular GitHub dashboard with verified public counts."""
from html import escape


def render_stats(metrics, languages):
    colors = ("#22D3EE", "#A78BFA", "#39FF88", "#F472B6", "#FBBF24")
    circles = []
    for i, (label, value) in enumerate(list(metrics)[:4]):
        x = 140 + i * 270
        color = colors[i]
        circles.append(
            f'<circle cx="{x}" cy="112" r="57" fill="#10192B" stroke="#283751" stroke-width="9"/>'
            f'<circle class="orbit" cx="{x}" cy="112" r="57" fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round" stroke-dasharray="252 358" transform="rotate(-90 {x} 112)"/>'
            f'<text x="{x}" y="123" text-anchor="middle" font-size="36" font-weight="800" fill="{color}">{max(0, int(value)):,}</text>'
            f'<text x="{x}" y="195" text-anchor="middle" font-size="16" fill="#DAE7F7">{escape(str(label))}</text>'
        )
    items = languages.most_common(5) if languages else []
    total = sum(max(0, int(count)) for _, count in items)
    segments = []
    legend = []
    offset = 0
    for i, (language, count) in enumerate(items):
        count = max(0, int(count))
        width = 1036 * count / total if total else 0
        color = colors[i % len(colors)]
        segments.append(f'<rect x="{32+offset:.2f}" y="228" width="{width:.2f}" height="11" fill="{color}"/>')
        legend.append(
            f'<circle cx="{34+i*205}" cy="264" r="5" fill="{color}"/>'
            f'<text x="{47+i*205}" y="269" font-size="13" fill="#BFCDE0">{escape(str(language))} · {count}</text>'
        )
        offset += width
    if not items:
        legend.append('<text x="34" y="264" fill="#A8BDD7" font-size="13">No public language data</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="292" viewBox="0 0 1100 292" role="img" aria-labelledby="title desc">
<title id="title">Compact live GitHub orbit dashboard</title>
<desc id="desc">Four verified public GitHub metrics in decorative rings and a proportional primary-language strip</desc>
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#090D1D"/><stop offset="1" stop-color="#101C2B"/></linearGradient>
<style>.orbit{{animation:orbit 12s linear infinite}}@keyframes orbit{{to{{stroke-dashoffset:-358}}}}@media(prefers-reduced-motion:reduce){{.orbit{{animation:none}}}}</style></defs>
<rect width="1100" height="292" rx="17" fill="url(#bg)"/>
<rect x="1" y="1" width="1098" height="290" rx="16" fill="none" stroke="#344767"/>
<text x="25" y="30" font-family="monospace" font-size="17" font-weight="700" fill="#EAF2FF">GITHUB // LIVE ORBIT</text>
<text x="1074" y="30" text-anchor="end" font-family="monospace" font-size="12" fill="#39FF88">● AUTO REFRESH</text>
<g font-family="Arial,sans-serif">{''.join(circles)}</g>
<rect x="32" y="228" width="1036" height="11" rx="5" fill="#25344C"/>
<g font-family="Arial,sans-serif">{''.join(segments)}{''.join(legend)}</g>
</svg>
"""
