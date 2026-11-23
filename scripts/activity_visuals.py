"""Render a compact cyber-terminal SVG from public GitHub activity."""
from html import escape


def render_activity(events):
    events = list(events)
    height = 84 + max(1, len(events)) * 68
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img">',
        '<title>Live public GitHub activity feed</title>',
        f'<rect width="1100" height="{height}" fill="#0D1117"/>',
        '<text x="30" y="35" font-family="monospace" font-size="16" fill="#39FF88">● ACTIVITY STREAM</text>',
        '<text x="1070" y="35" text-anchor="end" font-family="monospace" font-size="13" fill="#22D3EE">GITHUB API // PUBLIC EVENTS</text>',
    ]
    if not events:
        lines.append('<text x="32" y="104" font-family="monospace" font-size="17" fill="#C5D1DD">No recent public events available.</text>')
    for index, (label, repo, _url, day) in enumerate(events):
        y = 88 + index * 68
        label = str(label)
        repo = str(repo)
        if len(repo) > 58:
            repo = repo[:55] + "…"
        lines.extend([
            f'<text x="32" y="{y}" font-family="monospace" font-size="14" fill="#A78BFA">{escape(str(day))} UTC</text>',
            f'<text x="215" y="{y}" font-family="monospace" font-size="15" fill="#39FF88">▸ {escape(label)}</text>',
            f'<text x="215" y="{y+24}" font-family="monospace" font-size="15" fill="#C5D1DD">{escape(repo)}</text>',
        ])
    lines.append('</svg>')
    return "\n".join(lines)
