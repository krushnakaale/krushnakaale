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
    # Subtle hooded-coder watermark only for latest repositories; keep text readable.
    if not featured:
        for row in range(rows):
            for column in range(2):
                cx = 437 + column * 550
                cy = 88 + row * row_height
                elements.extend([
                    f'<g transform="translate({cx} {cy})" opacity="0.48">',
                    '<path d="M-62 57Q-63 11-37-28Q-18-58 0-61Q18-58 37-28Q63 11 62 57Z" fill="#185D48" stroke="#39FF88" stroke-width="3"/>',
                    '<path d="M-35-9Q-22-38 0-42Q22-38 35-9L25 24Q0 37-25 24Z" fill="#071713"/>',
                    '<path d="M-23-5L-7-1M23-5L7-1" stroke="#22D3EE" stroke-width="4"/>',
                    '<path d="M-51 38H51L61 70H-61Z" fill="#0C332B" stroke="#39FF88" stroke-width="3"/>',
                    '<path d="M-12 51H12M0 45V57" stroke="#39FF88" stroke-width="3"/>',
                    '</g>',
                ])
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
