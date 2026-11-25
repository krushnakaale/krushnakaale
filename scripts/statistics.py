"""Single-orbit compact GitHub dashboard with real API-backed metrics."""
from html import escape
from math import pi


def render_stats(metrics, languages):
    values = {str(label).lower(): max(0, int(value)) for label, value in list(metrics)[:4]}
    projects = values.get("public projects", next(iter(values.values()), 0))
    colors = ("#39FF88", "#22D3EE", "#A78BFA", "#00E5A0", "#FBBF24")
    labels = []
    for i, (label, value) in enumerate(list(metrics)[:4]):
        x = 410 + (i % 2) * 330
        y = 98 + (i // 2) * 84
        color = colors[i]
        labels.append(
            f'<rect x="{x}" y="{y-31}" width="300" height="67" rx="10" fill="#071A15" stroke="#235E46"/>'
            f'<rect x="{x}" y="{y-31}" width="4" height="67" rx="2" fill="{color}"/>'
            f'<text x="{x+17}" y="{y-7}" font-size="14" fill="#9AC9B2">{escape(str(label))}</text>'
            f'<text x="{x+17}" y="{y+23}" font-size="29" font-weight="800" fill="{color}">{max(0,int(value)):,}</text>'
        )
    items = languages.most_common(5) if languages else []
    total = sum(max(0, int(count)) for _, count in items)
    segments = []
    legends = []
    offset = 0.0
    circumference = 2 * pi * 100
    for i, (language, count) in enumerate(items):
        count = max(0, int(count))
        color = colors[i % len(colors)]
        dash = circumference * count / total if total else 0
        segments.append(
            f'<circle cx="193" cy="145" r="100" fill="none" stroke="{color}" stroke-width="13" '
            f'stroke-dasharray="{dash:.3f} {circumference:.3f}" stroke-dashoffset="{-offset:.3f}" '
            f'transform="rotate(-90 193 145)"/>'
        )
        offset += dash
        legends.append(
            f'<circle cx="{420+i*133}" cy="251" r="5" fill="{color}"/>'
            f'<text x="{431+i*133}" y="255" font-size="12" fill="#B6EBD0">{escape(str(language))[:13]}</text>'
        )
    if not legends:
        legends.append('<text x="420" y="255" font-size="13" fill="#AFC3DB">No public language data yet</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="292" viewBox="0 0 1100 292" role="img" aria-labelledby="title desc">
<title id="title">Single orbit live GitHub dashboard</title>
<desc id="desc">One proportional language distribution circle, surrounded by verified public GitHub metrics</desc>
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#020A08"/><stop offset="1" stop-color="#071B17"/></linearGradient><pattern id="grid" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" fill="none" stroke="#39FF88" stroke-opacity=".065" stroke-width=".7"/></pattern>
<style>.halo{{animation:glow 3s ease-in-out infinite alternate}}@keyframes glow{{to{{opacity:.25}}}}.snake-orbit{{opacity:0;animation:ambush 8s linear infinite}}.snake-lunge{{animation:snakeBite 8s ease-in-out infinite}}.snake-jaw{{animation:jaw 8s ease-in-out infinite}}@keyframes ambush{{0%,60%,89%,100%{{opacity:0}}64%,82%{{opacity:1}}}}@keyframes snakeBite{{0%,65%,85%,100%{{transform:translateX(0)}}70%{{transform:translateX(-5px)}}73%,75%{{transform:translateX(23px)}}}}@keyframes jaw{{0%,65%,78%,100%{{opacity:0}}70%,74%{{opacity:1}}}}@media(prefers-reduced-motion:reduce){{.halo,.snake-orbit,.snake-lunge,.snake-jaw{{animation:none}}}}</style></defs>
<rect width="1100" height="292" rx="18" fill="url(#bg)"/><rect width="1100" height="292" rx="18" fill="url(#grid)"/>
<rect x="1" y="1" width="1098" height="290" rx="17" stroke="#227A50" fill="none"/>
<text x="27" y="28" font-family="monospace" font-size="17" font-weight="700" fill="#EAF2FF">root@github:~# ./live-orbit</text>
<text x="1070" y="28" text-anchor="end" font-family="monospace" font-size="12" fill="#39FF88">[ ● ] API CONNECTED // AUTO-SYNC</text>
<circle class="halo" cx="193" cy="145" r="118" fill="none" stroke="#39FF88" stroke-opacity=".6" stroke-width="2"/>
<circle cx="193" cy="145" r="100" fill="none" stroke="#194330" stroke-width="13"/>
<g>{''.join(segments)}</g>
<circle cx="193" cy="145" r="78" fill="#06140F"/>
<g transform="translate(193 145)">
<g class="snake-orbit" opacity="0">
<path d="M-69 0 A69 69 0 0 1 0 -69 A69 69 0 0 1 63 -28" fill="none" stroke="#123F2A" stroke-width="12" stroke-linecap="round"/>
<path d="M-69 0 A69 69 0 0 1 0 -69 A69 69 0 0 1 63 -28" fill="none" stroke="#38965A" stroke-width="8" stroke-linecap="round"/><path d="M-69 0 A69 69 0 0 1 0 -69 A69 69 0 0 1 63 -28" fill="none" stroke="#9DE8A1" stroke-width="3" stroke-dasharray="2 3"/>
<g transform="translate(63 -28) rotate(155)">
<g class="snake-lunge">
<path d="M-10 -9 Q3 -13 15 -5 L18 0 L15 5 Q3 13 -10 9 Z" fill="#39FF88" stroke="#B6FFD4" stroke-width="1"/>
<circle cx="5" cy="-5" r="2" fill="#071A15"/><circle cx="5" cy="5" r="2" fill="#071A15"/>
<path class="snake-jaw" d="M8 0 L19 0 L13 5 Z" fill="#071A15"/>
<path d="M15 -3 L11 0 L15 3" fill="#EAF2FF"/>
</g></g></g></g>
<text x="193" y="143" text-anchor="middle" font-family="Arial,sans-serif" font-size="46" font-weight="800" fill="#39FF88">{projects:,}</text>
<text x="193" y="166" text-anchor="middle" font-family="monospace" font-size="13" fill="#8DC7A9">PUBLIC REPOS</text>
<g font-family="Arial,sans-serif">{''.join(labels)}{''.join(legends)}</g>
<text x="27" y="277" font-family="monospace" font-size="11" fill="#8DA3BE">SYS::OK / LANGUAGE RING = PUBLIC REPO LANGUAGES / SOURCE: GITHUB API</text>
</svg>
"""
