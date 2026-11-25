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
<linearGradient id="skin" x2="0" y2="1"><stop stop-color="#152e17"/><stop offset=".35" stop-color="#719b45"/><stop offset=".65" stop-color="#365d27"/><stop offset="1" stop-color="#102515"/></linearGradient><pattern id="scales" width="9" height="6" patternUnits="userSpaceOnUse"><path d="M0 0Q4.5 7 9 0M-4.5 3Q0 10 4.5 3M4.5 3Q9 10 13.5 3" fill="none" stroke="#152d16" stroke-width=".7"/></pattern><style>.viper{{opacity:0;animation:emerge 8s infinite}}.strike{{animation:strike 8s infinite}}.jaw{{transform-origin:0px 5px;animation:snap 8s infinite}}@keyframes emerge{{0%,59%,91%,100%{{opacity:0}}63%,84%{{opacity:1}}}}@keyframes strike{{0%,63%,85%,100%{{transform:translateX(0)}}69%{{transform:translateX(8px)}}73%,76%{{transform:translateX(-28px)}}}}@keyframes snap{{0%,65%,76%,100%{{transform:rotate(0deg)}}71%,73%{{transform:rotate(-24deg)}}}}.halo{{animation:glow 3s ease-in-out infinite alternate}}@keyframes glow{{to{{opacity:.25}}}}@media(prefers-reduced-motion:reduce){{.halo,.viper,.strike,.jaw{{animation:none}}}}</style></defs>
<rect width="1100" height="292" rx="18" fill="url(#bg)"/><rect width="1100" height="292" rx="18" fill="url(#grid)"/>
<rect x="1" y="1" width="1098" height="290" rx="17" stroke="#227A50" fill="none"/>
<text x="27" y="28" font-family="monospace" font-size="17" font-weight="700" fill="#EAF2FF">root@github:~# ./live-orbit</text>
<text x="1070" y="28" text-anchor="end" font-family="monospace" font-size="12" fill="#39FF88">[ ● ] API CONNECTED // AUTO-SYNC</text>
<circle class="halo" cx="193" cy="145" r="118" fill="none" stroke="#39FF88" stroke-opacity=".6" stroke-width="2"/>
<circle cx="193" cy="145" r="100" fill="none" stroke="#194330" stroke-width="13"/>
<g>{''.join(segments)}</g>
<circle cx="193" cy="145" r="78" fill="#06140F"/>
<g class="viper" opacity="0" transform="translate(193 145)">
<path d="M-65 42 C-96 6 -75 -69 -22 -74 C28 -88 76 -58 76 -20 Q76 3 52 3" fill="none" stroke="#020906" stroke-width="19" stroke-linecap="round"/>
<path d="M-65 42 C-96 6 -75 -69 -22 -74 C28 -88 76 -58 76 -20 Q76 3 52 3" fill="none" stroke="url(#skin)" stroke-width="15" stroke-linecap="round"/>
<path d="M-65 42 C-96 6 -75 -69 -22 -74 C28 -88 76 -58 76 -20 Q76 3 52 3" fill="none" stroke="url(#scales)" stroke-width="14" stroke-linecap="round"/>
<g transform="translate(58 0)"><g class="strike">
<g class="jaw"><path d="M10 4 Q-6 7 -24 2 L-22 9 Q-4 16 10 8Z" fill="url(#skin)" stroke="#182c14"/><path d="M-19 5 L-15 1 L-14 7" fill="#e6e4c6"/></g>
<path d="M13 -8 Q4 -17 -10 -13 L-28 -4 Q-31 0 -24 3 L-8 5 Q6 7 14 1Z" fill="url(#skin)" stroke="#142714"/>
<path d="M13 -8 Q4 -17 -10 -13 L-28 -4 Q-31 0 -24 3 L-8 5 Q6 7 14 1Z" fill="url(#scales)" opacity=".7"/>
<ellipse cx="-12" cy="-6" rx="4" ry="3" fill="#c9ad43"/><ellipse cx="-12" cy="-6" rx="1" ry="2.8" fill="#080e08"/><circle cx="-25" cy="-2" r="1" fill="#101d0c"/>
</g></g></g>
<text x="193" y="143" text-anchor="middle" font-family="Arial,sans-serif" font-size="46" font-weight="800" fill="#39FF88">{projects:,}</text>
<text x="193" y="166" text-anchor="middle" font-family="monospace" font-size="13" fill="#8DC7A9">PUBLIC REPOS</text>
<g font-family="Arial,sans-serif">{''.join(labels)}{''.join(legends)}</g>
<text x="27" y="277" font-family="monospace" font-size="11" fill="#8DA3BE">SYS::OK / LANGUAGE RING = PUBLIC REPO LANGUAGES / SOURCE: GITHUB API</text>
</svg>
"""
