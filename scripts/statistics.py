"""Render the local GitHub statistics SVG."""
from html import escape


def render_stats(metrics, languages):
    labels = [
        f'<text x="24" y="{y}">{escape(label)}</text>'
        f'<text x="333" y="{y}" text-anchor="end" fill="#69ff45">{value}</text>'
        for y, (label, value) in zip(range(74, 187, 35), metrics)
    ]
    bars = []
    if languages:
        maximum = max(languages.values())
        for index, (language, count) in enumerate(languages.most_common(4)):
            y = 74 + index * 35
            bars.append(
                f'<text x="400" y="{y}">{escape(language)}</text>'
                f'<rect x="530" y="{y - 10}" width="142" height="8" rx="4" fill="#24422d"/>'
                f'<rect x="530" y="{y - 10}" width="{round(142 * count / maximum)}" height="8" rx="4" fill="#57ef38"/>'
                f'<text x="704" y="{y}" text-anchor="end">{count}</text>'
            )
    else:
        bars.append('<text x="400" y="74">No language data yet</text>')
    rows = "\n    ".join(labels + bars)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="728" height="204" viewBox="0 0 728 204">
  <rect x="1" y="1" width="355" height="202" rx="14" fill="#07110c" stroke="#46a847"/>
  <rect x="376" y="1" width="351" height="202" rx="14" fill="#07110c" stroke="#46a847"/>
  <g font-family="system-ui, sans-serif" font-size="17" fill="#e6f8e9">
    <text x="24" y="36" font-weight="700" fill="#69ff45">GitHub stats</text>
    <text x="400" y="36" font-weight="700" fill="#69ff45">Top languages by repository</text>
    {rows}
  </g>
</svg>
"""
