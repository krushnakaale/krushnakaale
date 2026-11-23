"""Generate a responsive cyberpunk GitHub dashboard from real public API data."""
from html import escape


def render_stats(metrics, languages):
    """Build a GitHub-safe SVG. Metrics are supplied by the profile updater."""
    metrics = list(metrics)[:4]
    colors = ("#22D3EE", "#A78BFA", "#39FF88", "#22D3EE")
    cards = []
    for index, (label, value) in enumerate(metrics):
        x = 20 + index * 270
        color = colors[index]
        cards.append(
            f'<rect x="{x}" y="75" width="250" height="112" rx="13" fill="#111A2D" stroke="{color}" stroke-opacity=".75"/>'
            f'<rect x="{x+14}" y="91" width="4" height="17" rx="2" fill="{color}"/>'
            f'<text x="{x+27}" y="105" font-size="16" fill="#C6D5E7">{escape(str(label))}</text>'
            f'<text x="{x+17}" y="161" font-size="39" font-weight="800" fill="{color}">{max(0, int(value)):,}</text>'
        )
    items = languages.most_common(5) if languages else []
    maximum = max((count for _, count in items), default=1)
    bars = []
    for index, (language, count) in enumerate(items):
        y = 258 + index * 37
        color = colors[index % len(colors)]
        width = round(735 * count / maximum)
        bars.append(
            f'<text x="29" y="{y}" font-size="16" fill="#E6F0FF">{escape(str(language))}</text>'
            f'<rect x="225" y="{y-13}" width="735" height="14" rx="7" fill="#243047"/>'
            f'<rect class="bar" x="225" y="{y-13}" width="{width}" height="14" rx="7" fill="{color}"/>'
            f'<text x="1040" y="{y}" text-anchor="end" font-size="15" fill="#B5C6DD">{int(count)}</text>'
        )
    if not bars:
        bars.append('<text x="30" y="260" font-size="16" fill="#B5C6DD">No public language data available</text>')
    height = 465
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img" aria-labelledby="title desc">
<title id="title">Live GitHub dashboard</title>
<desc id="desc">Public repository counts, stars, forks, followers and repository primary languages</desc>
<defs>
<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#090D1C"/><stop offset="1" stop-color="#101B2B"/></linearGradient>
<style>.bar{{animation:grow 1.6s ease-out both;transform-box:fill-box;transform-origin:left center}}.signal{{animation:pulse 2.4s ease-in-out infinite alternate}}@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}@keyframes pulse{{to{{opacity:.25}}}}@media(prefers-reduced-motion:reduce){{.bar,.signal{{animation:none}}}}</style>
</defs>
<rect width="1100" height="{height}" rx="19" fill="url(#bg)"/>
<rect x="1" y="1" width="1098" height="{height-2}" rx="18" stroke="#344765" fill="none"/>
<circle class="signal" cx="27" cy="35" r="6" fill="#39FF88"/>
<text x="43" y="42" font-family="monospace" font-size="23" font-weight="700" fill="#F0F5FF">GITHUB / LIVE METRICS</text>
<text x="1072" y="40" text-anchor="end" font-family="monospace" font-size="13" fill="#22D3EE">GITHUB API · AUTO REFRESH</text>
<g font-family="Arial,sans-serif">{''.join(cards)}</g>
<path d="M21 211H1079" stroke="#33435F"/>
<text x="27" y="237" font-family="monospace" font-size="19" font-weight="700" fill="#A78BFA">TOP LANGUAGES</text>
<text x="1070" y="235" text-anchor="end" font-family="monospace" font-size="12" fill="#A0B0C8">PRIMARY LANGUAGE PER PUBLIC REPOSITORY</text>
<g font-family="Arial,sans-serif">{''.join(bars)}</g>
<text x="28" y="448" font-family="monospace" font-size="12" fill="#8B9DB8">VERIFIED PUBLIC REPOSITORY METRICS · COUNTS REFRESH WHEN THE WORKFLOW RUNS</text>
</svg>
"""
