"""Minimal language analytics using GitHub-reported code bytes."""
from html import escape

COLORS = {"Python":"#3776AB","JavaScript":"#F1E05A","TypeScript":"#3178C6","HTML":"#E34C26","CSS":"#A78BFA","Java":"#B07219","C":"#A8B9CC","C++":"#F34B7D","Shell":"#89E051","Go":"#00ADD8","Rust":"#DEA584"}

def render_language_pie(languages, repo_count=None):
    raw = [(str(n), int(v)) for n,v in languages.most_common() if int(v)>0]
    total = sum(v for _,v in raw)
    items = raw[:9]
    if len(raw)>9:
        items.append(("Other",sum(v for _,v in raw[9:])))
    height = 158 + 42*max(1,len(items))
    rows, segments = [], []
    offset = 32
    for i,(name,amount) in enumerate(items):
        share = amount/total
        color = COLORS.get(name,"#94A3B8")
        width = 1036*share
        segments.append(f'<rect x="{offset:.3f}" y="87" width="{width:.3f}" height="12" fill="{color}"/>')
        offset += width
        y = 137+i*42
        rows.append(f'<circle cx="40" cy="{y}" r="5" fill="{color}"/><text x="55" y="{y+5}" fill="#E6E8EC" font-size="16">{escape(name[:30])}</text><rect x="310" y="{y-4}" width="570" height="8" rx="4" fill="#292D34"/><rect x="310" y="{y-4}" width="{570*share:.3f}" height="8" rx="4" fill="{color}"/><text x="1068" y="{y+5}" text-anchor="end" fill="#E6E8EC" font-size="16">{share*100:.1f}%</text>')
    if not rows:
        rows.append('<text x="32" y="142" fill="#A0A6B0">No language data available</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img" aria-labelledby="title desc">
<title id="title">Language analytics</title><desc id="desc">GitHub language byte distribution across selected public projects.</desc>
<defs><clipPath id="bar"><rect x="32" y="87" width="1036" height="12" rx="6"/></clipPath><style>.status{{animation:breathe 4s ease-in-out infinite}}@keyframes breathe{{50%{{opacity:.4}}}}@media(prefers-reduced-motion:reduce){{.status{{animation:none}}}}</style></defs>
<rect width="1100" height="{height}" rx="14" fill="#14161A"/>
<g font-family="Arial,sans-serif">
<text x="32" y="36" font-size="24" font-weight="700" fill="#F1F2F4">Language analytics</text>
<text x="32" y="62" font-size="14" fill="#A0A6B0">{len(raw)} languages · {repo_count if repo_count is not None else 'Public'} repositories</text>
<circle class="status" cx="972" cy="32" r="4" fill="#89E051"/><text x="1068" y="37" text-anchor="end" font-size="12" fill="#A0A6B0">AUTO-SYNC</text>
<rect x="32" y="87" width="1036" height="12" rx="6" fill="#292D34"/><g clip-path="url(#bar)">{''.join(segments)}</g>
{''.join(rows)}
<text x="32" y="{height-15}" font-size="12" fill="#A0A6B0">GitHub API · {total:,} language bytes</text>
</g></svg>"""
