"""Generate animated multicolor cyberpunk statistics from verified public metrics."""
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
            f'<rect class="card" x="{x}" y="16" width="257" height="104" rx="15" fill="#101426" stroke="#334B74"/>'
            f'<rect x="{x + 15}" y="30" width="4" height="18" rx="2" fill="#22D3EE"/>'
            f'<text x="{x + 28}" y="45" fill="#CBD5E1" font-size="15">{escape(label)}</text>'
            f'<text x="{x + 19}" y="97" fill="#22D3EE" font-size="39" font-weight="800">{value:,}</text>'
        )
    while len(cards) < 4:
        index = len(cards)
        x = 14 + index * 275
        cards.append(f'<rect x="{x}" y="16" width="257" height="104" rx="15" fill="#101426" stroke="#334B74"/>')
    bars = []
    max_count = max((count for _, count in items), default=1)
    for index, (language, count) in enumerate(items):
        x = 35 + (index % 3) * 355
        y = 185 + (index // 3) * 40
        bars.append(
            f'<text x="{x}" y="{y}" fill="#E2E8F0" font-size="14">{escape(str(language))}</text>'
            f'<rect x="{x + 120}" y="{y - 12}" width="150" height="11" rx="5" fill="#29324C"/>'
            f'<rect class="bar" x="{x + 120}" y="{y - 12}" width="{round(150 * count / max_count)}" height="11" rx="5" fill="#A78BFA"/>'
            f'<text x="{x + 283}" y="{y}" fill="#B9C5DE" font-size="13">{count}</text>'
        )
    if not items:
        bars.append('<text x="35" y="187" fill="#B9C5DE">No language data available</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Public GitHub repository statistics">
<defs>
  <style>.bar{{animation:grow 1.8s ease-out both;transform-box:fill-box;transform-origin:left center}}.card{{animation:appear 1.2s ease-out both}}@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}@keyframes appear{{from{{opacity:.3}}to{{opacity:1}}}}@media(prefers-reduced-motion:reduce){{.bar,.card{{animation:none}}}}</style>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0A0D1D"/><stop offset="1" stop-color="#091B27"/></linearGradient>
</defs>
<rect width="{width}" height="{height}" rx="20" fill="url(#bg)"/>
<rect x="1" y="1" width="1098" height="278" rx="19" fill="none" stroke="#334B74"/>
<g font-family="Arial, sans-serif">
{''.join(cards)}
<text x="27" y="155" fill="#22D3EE" font-size="19" font-weight="700">TOP LANGUAGES</text>
<text x="1065" y="153" text-anchor="end" fill="#94A3B8" font-size="12">By public repository primary language</text>
{''.join(bars)}
</g>
</svg>
"""
