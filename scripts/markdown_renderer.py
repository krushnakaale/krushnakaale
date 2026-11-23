"""Render safe Markdown and update only designated README regions."""
import re
from html import escape
from urllib.parse import quote

REGIONS = ("STATS", "FEATURED", "REPOSITORIES", "LANGUAGES", "ACTIVITY", "FOCUS")


def text(value):
    value = escape(" ".join(str(value or "").split()), quote=False)
    return re.sub(r"[!\\*_#\[\]~|\x60]", lambda match: f"&#{ord(match[0])};", value)


def project_cards(username, repositories):
    """Render theme-matched repository cards from fresh GitHub API metadata."""
    if not repositories:
        return "No public repositories to display yet."

    cards = []
    for repo in repositories:
        name = text(repo["name"])
        link = f"https://github.com/{quote(username, safe='')}/{quote(repo['name'], safe='')}"
        description = text(repo.get("description") or "Explore the project source code and documentation.")
        language = text(repo.get("language") or "Other")
        stars = max(0, int(repo.get("stargazers_count") or 0))
        forks = max(0, int(repo.get("forks_count") or 0))
        pushed = text((repo.get("pushed_at") or "")[:10])
        date = f"LAST PUSH // {pushed} UTC" if pushed else "LAST PUSH // unavailable"
        badge = (
            "https://img.shields.io/badge/STATUS-"
            + ("UNAVAILABLE-142017?style=flat-square%26labelColor=0D1712%26color=A78BFA"
               if repo.get("disabled") else
               "ACTIVE-142017?style=flat-square%26labelColor=0D1712%26color=39FF88")
        ).replace("%26", "&amp;")
        cards.append(
            '<td width="50%" valign="top">'
            f'<a href="{link}"><strong>▸ {name}</strong></a>'
            f'<br/><img src="{badge}" alt="Repository status" />'
            f'&nbsp;<sub>⌘ {language}</sub>'
            f'<p>{description}</p>'
            f'<sub>★ {stars} &nbsp;·&nbsp; ⑂ {forks}</sub>'
            f'<br/><sub><code>{date}</code></sub>'
            '</td>'
        )
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i + 2]
        if len(pair) == 1:
            pair.append('<td width="50%" valign="top"></td>')
        rows.append("<tr>" + "".join(pair) + "</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def featured_cards(username, repositories):
    """Display GitHub-compatible two-column cyber project cards."""
    if not repositories:
        return "No featured public projects to display."
    cards = []
    for repo in repositories:
        name = text(repo["name"])
        link = f"https://github.com/{username}/{quote(repo['name'], safe='')}"
        description = text(repo.get("description") or "Explore source code and project details.")
        language = text(repo.get("language") or "Repository")
        stars = int(repo.get("stargazers_count") or 0)
        pushed = text((repo.get("pushed_at") or "")[:10])
        updated = f" · Updated {pushed}" if pushed else ""
        cards.append(
            f'<td width="50%" valign="top">'
            f'<a href="{link}"><strong>▸ {name}</strong></a>'
            f'<br/><br/>{description}'
            f'<br/><br/><sub>⌘ {language} · ★ {stars}{updated}</sub>'
            f'</td>'
        )
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i + 2]
        if len(pair) == 1:
            pair.append('<td width="50%"></td>')
        rows.append("<tr>" + "".join(pair) + "</tr>")
    return '<table>\n' + '\n'.join(rows) + '\n</table>'


def render_regions(original, sections=None):
    positions = {}
    for key in REGIONS:
        start, end = f"<!-- {key}:START -->", f"<!-- {key}:END -->"
        if original.count(start) != 1 or original.count(end) != 1:
            raise ValueError(f"README must contain exactly one {key} marker pair")
        start_at, finish = original.index(start), original.index(end)
        begin = start_at + len(start)
        after = finish + len(end)
        if (
            begin >= finish
            or (start_at and original[start_at - 1] != "\n")
            or original[begin:begin + 1] != "\n"
            or original[finish - 1:finish] != "\n"
            or original[after:after + 1] not in {"", "\n"}
        ):
            raise ValueError(f"Invalid {key} README marker placement")
        positions[key] = (begin, finish)
    ordered = sorted(positions, key=positions.get)
    if any(positions[a][1] >= positions[b][0] for a, b in zip(ordered, ordered[1:])):
        raise ValueError("README marker regions overlap")
    if sections is not None:
        for key in reversed(ordered):
            begin, finish = positions[key]
            original = original[:begin] + "\n" + sections[key] + "\n" + original[finish:]
    return original
