"""Generate a responsive cyber-green statistics SVG from verified public metrics."""
from html import escape


def render_stats(metrics, languages):
    safe_metrics = [(str(label), max(0, int(value))) for label, value in metrics]
    items = list(languages.most_common(5))
    total = sum(count for _, count in items)
    width, height = 1100, 280
    cards = []
    for index, (label, value) in enumerate(safe_metrics[:4]):
        x = 14 + index * 275
        cards.append(
            f'<rect x="{x}" y="16" width="257" height="104" rx="15" fill="#0B1510" stroke="#267D3D"/>'
            f'<rect x="{x + 15}" y="30" width="4" height="18" rx="2" fill="#39FF88"/>'
            f'<text x="{x + 28}" y="45" fill="#B7D5C1" font-size="15">{escape(label)}</text>'
            f'<text x="{x + 19}" y="97" fill="#69FF55" font-size="39" font-weight="800">{value:,}</text>'
        )
    while len(cards) < 4:
        index = len(cards)
        x = 14 + index * 275
        cards.append(f'<rect x="{x}" y="16" width="257" height="104" rx="15" fill="#0B1510" stroke="#267D3D"/>')
    bars = []
    max_count = max((count for _, count in items), default=1)
    for index, (language, count) in enumerate(items):
        x = 35 + (index % 3) * 355
        y = 185 + (index // 3) * 40
        bars.append(
            f'<text x="{x}" y="{y}" fill="#E3F5E9" font-size="14">{escape(str(language))}</text>'
            f'<rect x="{x + 120}" y="{y - 12}" width="150" height="11" rx="5" fill="#193328"/>'
            f'<rect x="{x + 120}" y="{y - 12}" width="{round(150 * count / max_count)}" height="11" rx="5" fill="#42F65E"/>'
            f'<text x="{x + 283}" y="{y}" fill="#A5D9B2" font-size="13">{count}</text>'
        )
    if not items:
        bars.append('<text x="35" y="187" fill="#A5D9B2">No language data available</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Public GitHub repository statistics">
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#08130D"/><stop offset="1" stop-color="#030907"/></linearGradient>
</defs>
<rect width="{width}" height="{height}" rx="20" fill="url(#bg)"/>
<rect x="1" y="1" width="1098" height="278" rx="19" fill="none" stroke="#1F5732"/>
<g font-family="Arial, sans-serif">
{''.join(cards)}
<text x="27" y="155" fill="#69FF55" font-size="19" font-weight="700">TOP LANGUAGES</text>
<text x="1065" y="153" text-anchor="end" fill="#789D86" font-size="12">By public repository primary language</text>
{''.join(bars)}
</g>
</svg>
"""
