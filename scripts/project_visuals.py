"""Generate borderless two-column SVG showcases from live GitHub repository data."""
from html import escape
from textwrap import wrap


def _truncate(value, limit):
    value = str(value or '')
    return value if len(value) <= limit else value[:limit - 1].rstrip() + '…'


def _safe(value):
    return escape(str(value or ""), quote=True)


def render_projects(repositories, featured=False):
    repos = list(repositories)
    count = len(repos)
    rows = max(1, (count + 1) // 2)
    row_height = 166
    height = 16 + rows * row_height
    accent = "#A78BFA" if featured else "#22D3EE"
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img">',
        f'<title>{"Featured projects" if featured else "Latest repositories"} — live GitHub data</title>',
        '<rect width="1100" height="100%" fill="#0D1117"/>',
    ]
    if not repos:
        elements.append('<text x="20" y="70" fill="#9BAAB9" font-size="20">No public repositories yet</text>')
    for i, repo in enumerate(repos):
        x = 32 + (i % 2) * 550
        y = 20 + (i // 2) * row_height
        name = str(repo.get("name") or "Repository")
        language = str(repo.get("language") or "Other")
        description = str(repo.get("description") or "Explore source code and project details.")
        lines = wrap(description, width=49, break_long_words=True, break_on_hyphens=False)
        if len(lines) > 2:
            lines = [lines[0], _truncate(lines[1], 46)]
        stars = max(0, int(repo.get("stargazers_count") or 0))
        forks = max(0, int(repo.get("forks_count") or 0))
        pushed = str(repo.get("pushed_at") or "")[:10] or "N/A"
        elements.extend([
            f'<text x="{x}" y="{y+14}" font-size="13" font-family="monospace" fill="{accent}">{"// FEATURED" if featured else "// RECENT"}  ·  {_safe(_truncate(language, 22))}</text>',
            f'<text x="{x}" y="{y+49}" font-size="24" font-weight="700" font-family="Arial,sans-serif" fill="#39FF88">{_safe("› " + _truncate(name, 28))}</text>',
        ])
        for j, line in enumerate(lines[:2]):
            elements.append(f'<text x="{x}" y="{y+84+j*21}" font-size="16" font-family="Arial,sans-serif" fill="#C5D1DD">{_safe(line)}</text>')
        elements.append(f'<text x="{x}" y="{y+143}" font-size="14" font-family="monospace" fill="#9DB7AA">★ {stars}   ⑂ {forks}   ·   UPDATED {_safe(pushed)}</text>')
    elements.append('</svg>')
    return "\n".join(elements)
