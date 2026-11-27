"""Responsive honeycomb language matrix using GitHub language bytes."""
from html import escape
from math import sin, cos, pi, ceil

def render_language_pie(languages, repo_count=None):
    raw = [(str(n), int(v)) for n,v in languages.most_common() if int(v)>0]
    total = sum(v for _,v in raw)
    items = raw[:14]
    if len(raw)>14:
        items.append(("Other",sum(v for _,v in raw[14:])))
    rows = max(1,ceil(len(items)/5))
    height = 110 + rows*154
    cells = []
    for i,(name,amount) in enumerate(items):
        row,col = divmod(i,5)
        count = min(5,len(items)-row*5)
        x = 550+(col-(count-1)/2)*188
        y = 130+row*154
        share = amount/total
        points = " ".join(f"{x+83*cos(pi*k/3):.2f},{y+83*sin(pi*k/3):.2f}" for k in range(6))
        cells.append(f'<g><polygon points="{points}" fill="#091C15" stroke="#246B49" stroke-width="1.5"/><polygon class="glow" style="animation-delay:{i*.45:.2f}s" points="{points}" fill="none" stroke="#39FF88" stroke-width="2" opacity=".45"/><text x="{x}" y="{y-23}" text-anchor="middle" fill="#8FC5A7" font-size="11">0{i+1:02d} / LANG</text><text x="{x}" y="{y-3}" text-anchor="middle" fill="#E6FFF0" font-size="14" font-weight="600">{escape(name[:17])}</text><text x="{x}" y="{y+26}" text-anchor="middle" fill="#39FF88" font-size="24" font-weight="700">{share*100:.1f}%</text><rect x="{x-40}" y="{y+38}" width="80" height="3" rx="1.5" fill="#234438"/><rect x="{x-40}" y="{y+38}" width="{80*share:.2f}" height="3" rx="1.5" fill="#39FF88"/></g>')
    if not cells:
        cells.append('<text x="550" y="130" text-anchor="middle" fill="#8FC5A7">No language data available</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img" aria-labelledby="title desc">
<title id="title">Language hexagon matrix</title><desc id="desc">GitHub language byte distribution across selected public projects.</desc>
<defs><pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#39FF88" stroke-opacity=".045"/></pattern><style>.glow{{animation:pulse 5s ease-in-out infinite}}@keyframes pulse{{50%{{opacity:.95}}}}@media(prefers-reduced-motion:reduce){{.glow{{animation:none}}}}</style></defs>
<rect width="1100" height="{height}" rx="16" fill="#050D0A"/><rect width="1100" height="{height}" rx="16" fill="url(#grid)"/>
<g font-family="monospace"><text x="28" y="32" font-size="18" font-weight="700" fill="#39FF88">LANGUAGE // HEX MATRIX</text><text x="1072" y="32" text-anchor="end" font-size="12" fill="#8FC5A7">{len(raw)} LANGUAGES · {repo_count if repo_count is not None else 'PUBLIC'} REPOS</text><path d="M28 48H1072" stroke="#204B37"/>{''.join(cells)}<text x="28" y="{height-18}" font-size="11" fill="#8FC5A7">GITHUB API // {total:,} CODE BYTES</text><text x="1072" y="{height-18}" text-anchor="end" font-size="11" fill="#39FF88">AUTO-SYNC</text></g></svg>"""
