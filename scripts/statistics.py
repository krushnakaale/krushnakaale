"""Generate a GitHub-compatible live SVG dashboard from verified public counts."""
from html import escape


def render_stats(metrics, languages):
    metrics = list(metrics)
    # Values are GitHub API derived. Never display fabricated commits/streaks.
    stats = []
    for i, (label, value) in enumerate(metrics[:4]):
        x = 24 + (i % 2) * 259
        y = 108 + (i // 2) * 70
        stats.append(
            f'<text x="{x}" y="{y}" fill="#a8c4b2" font-size="15">{escape(str(label))}</text>'
            f'<text x="{x}" y="{y + 32}" fill="#57ff83" font-weight="800" font-size="27">{int(value)}</text>'
        )
    bars = []
    items = languages.most_common(5) if languages else []
    maximum = max((count for _, count in items), default=1)
    for i, (language, count) in enumerate(items):
        y = 102 + i * 34
        width = round(290 * count / maximum)
        bars.append(
            f'<text x="572" y="{y}" fill="#d9fce4" font-size="14">{escape(str(language))}</text>'
            f'<rect x="724" y="{y - 12}" width="290" height="12" rx="6" fill="#173728"/>'
            f'<rect x="724" y="{y - 12}" width="{width}" height="12" rx="6" fill="#2bfa68"/>'
            f'<text x="1055" y="{y}" fill="#b8dfc3" text-anchor="end" font-size="14">{count}</text>'
        )
    if not bars:
        bars.append('<text x="572" y="110" font-size="17" fill="#a8c4b2">No public language data yet</text>')
    body = "\n".join(stats + bars)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="265" viewBox="0 0 1100 265" role="img" aria-labelledby="title description">
<title id="title">Live GitHub profile statistics</title>
<desc id="description">Verified public project counts and primary programming languages for the developer</desc>
<rect width="1100" height="265" rx="16" fill="#050c08"/>
<rect x="2" y="2" width="532" height="261" rx="16" fill="#08160e" stroke="#2fe66b" stroke-width="2"/>
<rect x="551" y="2" width="547" height="261" rx="16" fill="#08160e" stroke="#2fe66b" stroke-width="2"/>
<rect x="18" y="16" width="8" height="34" rx="2" fill="#39ff88"/>
<text x="40" y="40" font-family="monospace" font-size="21" font-weight="700" fill="#eaffee">LIVE GITHUB STATS</text>
<rect x="564" y="16" width="8" height="34" rx="2" fill="#39ff88"/>
<text x="586" y="40" font-family="monospace" font-size="21" font-weight="700" fill="#eaffee">TOP LANGUAGES</text>
<g font-family="system-ui,sans-serif">{body}</g>
<text x="570" y="246" font-family="monospace" font-size="12" fill="#729e7f">Primary languages by public repository count</text>
</svg>
"""
