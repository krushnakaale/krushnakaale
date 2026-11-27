"""Holographic language analytics from GitHub code bytes."""
from html import escape

def render_language_pie(languages, repo_count=None):
    raw = [(str(n), int(v)) for n,v in languages.most_common() if int(v)>0]
    total = sum(v for _,v in raw)
    items = raw[:7]
    if len(raw)>7:
        items.append(("Other",sum(v for _,v in raw[7:])))
    bars = []
    step = min(155, 960/max(1,len(items)))
    for i,(name,amount) in enumerate(items):
        share = amount/total
        x = 550+(i-(len(items)-1)/2)*step
        h = 220*share
        y = 310-h
        w = min(64,step*.48)
        a,b = x-w/2,x+w/2
        bars.append(f'<g><ellipse cx="{x+7}" cy="318" rx="{w*.8}" ry="9" fill="#39FF88" opacity=".12"/><path d="M{b} {y} l14 -9 V301 L{b} 310Z" fill="#116B48"/><rect x="{a}" y="{y}" width="{w}" height="{h}" fill="url(#bar)" stroke="#39FF88" stroke-width=".8"/><path d="M{a} {y} l14 -9 h{w} l-14 9Z" fill="#8BFFD0" opacity=".85"/><text x="{x}" y="{y-19}" text-anchor="middle" font-size="18" font-weight="700" fill="#B5FFDA">{share*100:.1f}%</text><text x="{x}" y="345" text-anchor="middle" font-size="13" fill="#E1F8EC">{escape(name[:15])}</text></g>')
    grid = []
    for tick in range(0,101,25):
        y=310-220*tick/100
        grid.append(f'<path d="M65 {y}H1040" stroke="#28523F" stroke-dasharray="3 7"/><text x="52" y="{y+4}" text-anchor="end" fill="#719C88" font-size="11">{tick}%</text>')
    if not bars:
        bars.append('<text x="550" y="180" text-anchor="middle" fill="#B5FFDA">No language data available</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="400" viewBox="0 0 1100 400" role="img" aria-labelledby="title desc">
<title id="title">Holographic language analytics</title><desc id="desc">Actual GitHub language byte percentages across selected public repositories.</desc>
<defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#040C0B"/><stop offset="1" stop-color="#0B2119"/></linearGradient><linearGradient id="bar" x2="0" y2="1"><stop stop-color="#39FF88"/><stop offset="1" stop-color="#075438"/></linearGradient><style>.scan{{animation:scan 8s ease-in-out infinite}}@keyframes scan{{0%,100%{{transform:translateY(0);opacity:.1}}50%{{transform:translateY(220px);opacity:.5}}}}@media(prefers-reduced-motion:reduce){{.scan{{animation:none}}}}</style></defs>
<rect width="1100" height="400" rx="16" fill="url(#bg)"/>
<g font-family="monospace"><text x="28" y="34" font-size="20" font-weight="700" fill="#39FF88">LANGUAGE // HOLOGRAPHIC ANALYTICS</text><text x="1072" y="34" text-anchor="end" font-size="12" fill="#9AC9B2">{len(raw)} LANGUAGES · {repo_count if repo_count is not None else 'PUBLIC'} REPOS</text><path d="M28 51H1072" stroke="#28523F"/>{''.join(grid)}<path d="M65 310H1040L1070 330H35Z" fill="#123B2A" opacity=".65"/>{''.join(bars)}<path class="scan" d="M65 90H1040" stroke="#39FF88" stroke-width="1" opacity=".2"/><text x="28" y="382" font-size="11" fill="#9AC9B2">GITHUB API // {total:,} CODE BYTES</text><text x="1072" y="382" text-anchor="end" font-size="11" fill="#39FF88">AUTO-SYNC</text></g></svg>"""
